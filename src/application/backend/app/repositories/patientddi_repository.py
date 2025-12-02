from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, case, select
from app.db.models.patientddi import PatientDDI

# Similarity scoring weights
WEIGHT_SEX_MATCH = 50      # Points for exact sex match
WEIGHT_AGE_MAX = 50         # Maximum points for age similarity (exact match)
WEIGHT_COMORBIDITY = 50     # Points per matching comorbidity


def find_similar_interactions(
    db: Session,
    drug1: str,
    drug2: str,
    age: Optional[int] = None,
    sex: Optional[str] = None,
    comorbidities: Optional[List[str]] = None,
    limit: int = 10
) -> List[PatientDDI]:
    """
    Find similar DDI cases from the database.
    
    Strategy:
    1. First fetch all drug-drug interaction cases (drug1 + drug2)
    2. Then reorder by patient similarity (age, sex, comorbidities)
    
    Handles Comorbidities as JSON type (works with both PostgreSQL and SQLite).
    Input sanitization: case-insensitive, whitespace-trimmed comparisons.
    """
    # Sanitize drug inputs: strip whitespace
    drug1_clean = drug1.strip() if drug1 else drug1
    drug2_clean = drug2.strip() if drug2 else drug2
    
    # Step 1: Fetch all cases for this drug pair (bidirectional, case-insensitive)
    drug_condition = or_(
        and_(
            func.lower(PatientDDI.drug1_norm) == func.lower(drug1_clean),
            func.lower(PatientDDI.drug2_norm) == func.lower(drug2_clean)
        ),
        and_(
            func.lower(PatientDDI.drug1_norm) == func.lower(drug2_clean),
            func.lower(PatientDDI.drug2_norm) == func.lower(drug1_clean)
        ),
        # Also try original drug names
        and_(
            func.lower(PatientDDI.drug1) == func.lower(drug1_clean),
            func.lower(PatientDDI.drug2) == func.lower(drug2_clean)
        ),
        and_(
            func.lower(PatientDDI.drug1) == func.lower(drug2_clean),
            func.lower(PatientDDI.drug2) == func.lower(drug1_clean)
        )
    )
    
    all_cases = db.query(PatientDDI).filter(drug_condition).all()
    
    # Filter for unique patients (keep only one case per patient_uuid)
    # Group by patient_uuid and keep the first occurrence
    seen_patients = set()
    unique_cases = []
    for case in all_cases:
        if case.patient_uuid not in seen_patients:
            seen_patients.add(case.patient_uuid)
            unique_cases.append(case)
    
    # Step 2: Score and sort by patient similarity (using unique patients only)
    all_cases = unique_cases
    def calculate_similarity_score(case: PatientDDI) -> tuple:
        """
        Calculate similarity score for sorting.
        Returns tuple for multi-level sorting (higher is better match).
        Handles case-insensitive comparisons with input sanitization.
        """
        score = 0
        
        # Sex match (exact match = +WEIGHT_SEX_MATCH) - case-insensitive with sanitization
        sex_match = 0
        if sex and case.sex:
            # Sanitize: strip whitespace and convert to lowercase
            user_sex = sex.strip().lower()
            case_sex = case.sex.strip().lower()
            if case_sex == user_sex:
                sex_match = WEIGHT_SEX_MATCH
        
        # Age similarity (closer age = higher score, max +WEIGHT_AGE_MAX)
        age_score = 0
        if age is not None and case.age is not None:
            age_diff = abs(case.age - age)
            # Score decreases with age difference: WEIGHT_AGE_MAX points at exact match, 0 at WEIGHT_AGE_MAX+ years diff
            age_score = max(0, WEIGHT_AGE_MAX - age_diff)
        
        # Comorbidity overlap (each matching comorbidity = +WEIGHT_COMORBIDITY) - case-insensitive
        comorbidity_score = 0
        if comorbidities and case.comorbidities:
            # JSON type automatically deserializes to list
            # Normalize both user input and case comorbidities to lowercase for comparison
            case_comorbidities_lower = [c.strip().lower() for c in case.comorbidities if c]
            for comorbidity in comorbidities:
                # Sanitize user comorbidity: strip and lowercase
                if comorbidity and isinstance(comorbidity, str):
                    comorbidity_clean = comorbidity.strip().lower()
                    if comorbidity_clean and comorbidity_clean in case_comorbidities_lower:
                        comorbidity_score += WEIGHT_COMORBIDITY
        
        score = sex_match + age_score + comorbidity_score
        
        # Return tuple for sorting: (similarity_score, ddi_known, ddi_confidence)
        # Sort by similarity first, then known interactions, then confidence
        return (
            score,
            1 if case.ddi_known else 0,
            case.ddi_confidence if case.ddi_confidence is not None else 0.0
        )
    
    # Calculate maximum possible score for normalization
    # Max score = sex match + age match + comorbidity matches
    max_possible_score = WEIGHT_SEX_MATCH + WEIGHT_AGE_MAX
    if comorbidities:
        max_possible_score += WEIGHT_COMORBIDITY * len(comorbidities)
    
    # Sort cases by similarity score (descending) and attach normalized scores
    cases_with_scores = []
    for case in all_cases:
        score_tuple = calculate_similarity_score(case)
        raw_score = score_tuple[0]
        
        # Normalize score to 0-1 range
        normalized_score = raw_score / max_possible_score if max_possible_score > 0 else 0.0
        
        # Attach both raw and normalized scores to the case object
        case.similarity_score = normalized_score
        case.similarity_score_raw = raw_score
        
        cases_with_scores.append((case, score_tuple))
    
    # Sort by the full tuple (similarity, ddi_known, confidence)
    cases_with_scores.sort(key=lambda x: x[1], reverse=True)
    
    # Return just the cases (now with similarity_score attached)
    sorted_cases = [case for case, _ in cases_with_scores]
    
    return sorted_cases[:limit]


def get_interaction_statistics(
    db: Session,
    drug1: str,
    drug2: str
) -> dict:
    """
    Get aggregate statistics for a drug pair.
    Input sanitization: case-insensitive, whitespace-trimmed comparisons.
    """
    # Sanitize drug inputs: strip whitespace
    drug1_clean = drug1.strip() if drug1 else drug1
    drug2_clean = drug2.strip() if drug2 else drug2
    
    drug_condition = or_(
        and_(
            func.lower(PatientDDI.drug1_norm) == func.lower(drug1_clean),
            func.lower(PatientDDI.drug2_norm) == func.lower(drug2_clean)
        ),
        and_(
            func.lower(PatientDDI.drug1_norm) == func.lower(drug2_clean),
            func.lower(PatientDDI.drug2_norm) == func.lower(drug1_clean)
        )
    )
    # Get aggregate stats
    results = db.query(
        func.count(PatientDDI.patient_uuid).label('total_cases'),
        func.count(PatientDDI.unified_severity).label('known_severity_count'),
        func.avg(PatientDDI.ddi_confidence).label('avg_confidence'),
        func.max(
            case(
                (PatientDDI.ddi_known == True, 1),
                else_=0
            )
        ).label('is_known_interaction_from_patients')  # Database-agnostic boolean OR
    ).filter(drug_condition).first()
    
    # Get severity distribution
    severity_dist = db.query(
        PatientDDI.unified_severity,
        func.count(PatientDDI.patient_uuid).label('count')
    ).filter(
        drug_condition,
        PatientDDI.unified_severity.isnot(None)
    ).group_by(PatientDDI.unified_severity).all()

    return {
        'total_cases': results.total_cases or 0,
        'known_severity_count': results.known_severity_count or 0,
        'avg_confidence': float(results.avg_confidence or 0.0),
        'is_known_interaction_from_patients': bool(results.is_known_interaction_from_patients) or False,
        'severity_distribution': {sev: count for sev, count in severity_dist}
    }


def search_comorbidities(db: Session, comorbidity_name: str, limit: int) -> List[str]:
    """
    Searches for unique comorbidity names in PatientDDI.comorbidities 
    matching the input string. Works with both PostgreSQL and SQLite via JSON type.
    Returns the top N closest matches (shortest strings first).
    """
    if not comorbidity_name:
        return []

    search_pattern = comorbidity_name.lower()
    
    # Fetch all records with non-null comorbidities
    cases = db.query(PatientDDI).filter(PatientDDI.comorbidities.isnot(None)).all()
    
    # Extract and flatten all comorbidities, then filter by search pattern
    all_comorbidities = set()
    for case in cases:
        if isinstance(case.comorbidities, list):
            for comorbidity in case.comorbidities:
                if comorbidity and search_pattern in comorbidity.lower():
                    all_comorbidities.add(comorbidity)
    
    # Sort by length (shortest first) and limit
    results = sorted(all_comorbidities, key=len)[:limit]
    
    # Filter out None/empty strings if present in the data
    return [r for r in results if r]
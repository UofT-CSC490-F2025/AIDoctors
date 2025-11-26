from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, case
from app.db.models.ddi import PatientDDI


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
    Handles Comorbidities as TEXT (not PostgreSQL ARRAY).
    """
    query = db.query(PatientDDI)
    
    # Drug pair matching (bidirectional, case-insensitive)
    drug_condition = or_(
        and_(
            func.lower(PatientDDI.drug1_norm) == func.lower(drug1),
            func.lower(PatientDDI.drug2_norm) == func.lower(drug2)
        ),
        and_(
            func.lower(PatientDDI.drug1_norm) == func.lower(drug2),
            func.lower(PatientDDI.drug2_norm) == func.lower(drug1)
        ),
        # Also try original drug names
        and_(
            func.lower(PatientDDI.drug1) == func.lower(drug1),
            func.lower(PatientDDI.drug2) == func.lower(drug2)
        ),
        and_(
            func.lower(PatientDDI.drug1) == func.lower(drug2),
            func.lower(PatientDDI.drug2) == func.lower(drug1)
        )
    )
    query = query.filter(drug_condition)
    
    # Age range filtering (±10 years)
    if age is not None:
        query = query.filter(
            PatientDDI.age.between(age - 10, age + 10)
        )
    
    # Sex matching
    if sex:
        query = query.filter(func.lower(PatientDDI.sex) == func.lower(sex))
    
    # Comorbidity overlap using TEXT LIKE matching
    # Since Comorbidities is stored as "['Hypertension', 'Diabetes']"
    if comorbidities:
        comorbidity_conditions = []
        for comorbidity in comorbidities:
            # Match within the TEXT field (case-insensitive)
            # This will match 'Hypertension' in "['Hypertension', 'Diabetes']"
            comorbidity_conditions.append(
                func.lower(PatientDDI.comorbidities).like(f"%{comorbidity.lower()}%")
            )
        
        if comorbidity_conditions:
            query = query.filter(or_(*comorbidity_conditions))
    
    # Order by relevance: known interactions first, then by confidence
    query = query.order_by(
        PatientDDI.ddi_known.desc().nullslast(),
        PatientDDI.ddi_confidence.desc().nullslast()
    )
    
    return query.limit(limit).all()


def get_interaction_statistics(
    db: Session,
    drug1: str,
    drug2: str
) -> dict:
    """
    Get aggregate statistics for a drug pair.
    """
    drug_condition = or_(
        and_(
            func.lower(PatientDDI.drug1_norm) == func.lower(drug1),
            func.lower(PatientDDI.drug2_norm) == func.lower(drug2)
        ),
        and_(
            func.lower(PatientDDI.drug1_norm) == func.lower(drug2),
            func.lower(PatientDDI.drug2_norm) == func.lower(drug1)
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
        ).label('is_known_interaction')  # Database-agnostic boolean OR
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
        'is_known_interaction': bool(results.is_known_interaction) or False,
        'severity_distribution': {sev: count for sev, count in severity_dist}
    }
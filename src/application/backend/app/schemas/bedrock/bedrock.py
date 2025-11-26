from app.schemas.db.prediction import DDIPredictRequest
from app.utils.helpers import compute_overlap_days

def build_system_prompt() -> str:
    """
    Build the system prompt containing the 4 instructions for analysis format.
    """
    system_prompt = (
        "You are a clinical pharmacology expert analyzing drug-drug interactions (DDIs). "
        "When provided with patient information and medication details, return a comprehensive analysis in the following format:\n\n"
        "1) Predicted Severity Level:\n"
        '   {"severity":"<Minor|Moderate|Major>"}\n\n'
        "2) Comparison to Known DDI:\n"
        "   [Compare your prediction to the known clinical interaction if it exists.\n"
        "   Explain whether your assessment aligns with or differs from established\n"
        "   clinical knowledge and provide reasoning for any discrepancies.]\n\n"
        "3) Historical Cases Analysis:\n"
        "   [Based on your knowledge of hospitalizations involving patients taking\n"
        "   these two drugs (along with other medications), analyze the historical\n"
        "   evidence. Consider whether the historical cases show increased risk,\n"
        "   decreased risk, or no significant change compared to the known DDI.\n"
        "   Note that patients may be taking multiple medications, so reason about\n"
        "   whether the observed outcomes are likely due to this specific DDI or\n"
        "   other factors.]\n\n"
        "4) Clinical Concern Assessment:\n"
        "   [Based on the patient's specific information, historical cases,\n"
        "   and the DDI severity, determine if doctors should be concerned.\n"
        "   Doctors should be concerned if either: a) Historical cases do not\n"
        "   support evidence of the known DDI, or b) The DDI level is severe.\n"
        "   Provide clear guidance on the level of concern and recommended actions.]\n\n"
        "Provide your analysis based on clinical evidence, pharmacological principles, "
        "and real-world case data. Be thorough but concise in your explanations."
        f" Please output your response in the following format:\n\n{get_output_template()}"
    )
    return system_prompt


def build_user_prompt(payload: DDIPredictRequest, enriched_context: dict) -> str:
    """
    Build the user prompt containing the patient-specific information.
    """
    age = payload.Age if payload.Age is not None else ""
    sex = payload.Sex or ""
    comorbidities = payload.Comorbidities or []
    start = payload.overlap_start or ""
    end = payload.overlap_stop or ""
    overlap_days = compute_overlap_days(payload.overlap_start, payload.overlap_stop)
    ol_days_str = str(overlap_days) if overlap_days is not None else ""

    drug1 = payload.drug1_norm or payload.drug1 or ""
    drug2 = payload.drug2_norm or payload.drug2 or ""
    enriched_similar_cases = enriched_context.get("representative_cases", [])
    mech_list = enriched_context.get("top_mechanisms", [])
    if mech_list:
        mech += "\n".join(f"- {m}" for m in mech_list)
    enriched_mechanisms = "\n".join(f"- {case['mechanism']}" for case in enriched_similar_cases if case.get('mechanism')) or ""
    avg_confidence = enriched_context.get("avg_confidence") or ""
    known = enriched_context.get("known_interaction")
    known_str = "Unknown" if known is None else ("True" if known else "False")
    
    user_prompt = (
        "A patient is concurrently prescribed two medications.\n\n"
        "Patient information:\n"
        f"- Age: {age}\n"
        f"- Sex: {sex}\n"
        f"- Comorbidities: {comorbidities}\n\n"
        "Medication exposure:\n"
        f"- Start: {start}\n"
        f"- End: {end}\n"
        f"- Overlap days: {ol_days_str}\n\n"
        "Drugs:\n"
        f"- Drug 1: {drug1}\n"
        f"- Drug 2: {drug2}\n"
        f"- Known interaction in clinical sources: {known_str}\n"
        f"- Number of data sources supporting this: {avg_confidence}\n\n"
        "Mechanistic context:\n"
        f"{enriched_mechanisms}\n\n"
        "Please analyze this drug-drug interaction according to the format specified in the system instructions."
        f"\n\nRepresentative historical cases:\n {enriched_similar_cases}"
    )
    return user_prompt


def build_prompt(payload: DDIPredictRequest) -> str:
    """
    Build the complete prompt (legacy function for backward compatibility).
    """
    system_prompt = build_system_prompt()
    user_prompt = build_user_prompt(payload)
    return f"System: {system_prompt}\n\nUser: {user_prompt}"


def get_output_template() -> str:
    """
    Returns a template for the expected output format from the Bedrock model.
    This helps with parsing and validation of model responses.
    """
    template = '''<reasoning>
[YOUR STEP-BY-STEP REASONING PROCESS HERE]
</reasoning>

{
    "predicted_severity": "<Minor|Moderate|Major>",
    "comparison_to_known_ddi": {
        "known_interaction_exists": "<true|false>",
        "alignment_with_knowledge": "<aligned|contradicted|insufficient_data>",
        "explanation": "<detailed comparison explanation>"
    },
    "historical_cases_analysis": {
        "cases_reviewed": "<number or range>",
        "risk_assessment": "<increased_risk|decreased_risk|no_significant_change|insufficient_data>",
        "confidence": "<high|medium|low>",
        "reasoning": "<detailed analysis of historical evidence>"
    },
    "clinical_concern_assessment": {
        "should_be_concerned": "<true|false>",
        "concern_level": "<high|medium|low>",
        "primary_reason": "<historical_cases_evidence|severity_level|patient_factors>",
        "recommendations": ["<action1>", "<action2>", "<action3>"]
    },
    "summary": "<brief clinical summary for healthcare providers>"
}'''
    return template




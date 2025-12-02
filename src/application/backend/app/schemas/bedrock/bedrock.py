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
        '   {"severity":"<Minor|Moderate|Major>"}\n'
        "   [You will be provided with a known DDI severity if it exists in clinical databases.\n"
        "   Analyze the patient-specific factors and historical cases to determine a predicted\n"
        "   severity level that is specific to the patient at hand.]\n\n"
        "2) Comparison to Known DDI:\n"
        "   [The user will provide a known DDI severity if it exists. Compare your patient-specific\n"
        "   prediction to this known clinical interaction. Explain whether your assessment aligns\n"
        "   with or differs from the established severity level and provide reasoning for any\n"
        "   discrepancies based on the patient's unique characteristics.]\n\n"
        "3) Historical Cases Analysis:\n"
        "   [You will be provided with evidence of historical cases showcasing patients who are\n"
        "   already taking these two drugs. These patients are pre-filtered and you can assume\n"
        "   each case represents a patient who has undergone some medical incident while taking\n"
        "   these two drugs. While it is unclear if the two drugs are the direct cause of the\n"
        "   medical incident, any provided examples have relatively high confidence of demonstrating\n"
        "   a link. Analyze the similarities between the existing patient and the historical cases\n"
        "   to come up with a predicted severity level specific to the patient at hand. Consider\n"
        "   factors such as age, sex, comorbidities, and other medications that may influence\n"
        "   the interaction severity.]\n\n"
        "4) Clinical Concern Assessment:\n"
        "   [Based on the patient's specific information, historical cases, and the DDI severity,\n"
        "   determine if doctors should be concerned. In your summary, provide a clear determination\n"
        "   of whether doctors should be concerned about this specific patient taking these medications.\n"
        "   Consider the severity level, the strength of evidence from historical cases, and any\n"
        "   patient-specific risk factors. Provide clear guidance on the level of concern and\n"
        "   recommended actions.]\n\n"
        "IMPORTANT INSTRUCTIONS:\n"
        "- ALWAYS reference historical cases in your reasoning when they exist. Use the specific\n"
        "  details from these cases to support your severity prediction and clinical recommendations.\n"
        "- If no historical cases exist, please default to your own clinical knowledge but make it\n"
        "  very clear that there is no support from the database. Explicitly state that your analysis\n"
        "  is based solely on general pharmacological principles without real-world case evidence\n"
        "  from the database.\n\n"
        "Provide your analysis based on clinical evidence, pharmacological principles, "
        "and real-world case data. Be thorough but concise in your explanations."
        f" ALWAYS output your response in the following format:\n\n{get_output_template()}"
    )
    return system_prompt


def build_user_prompt(payload: DDIPredictRequest, enriched_context: dict) -> str:
    """
    Build the user prompt containing the patient-specific information.
    """
    age = payload.Age if payload.Age is not None else ""
    sex = payload.Sex or ""
    comorbidities = payload.Comorbidities or []

    drug1 = payload.drug1 or ""
    drug2 = payload.drug2 or ""
    enriched_similar_cases = enriched_context.get("representative_cases", [])
    enriched_mechanisms = "\n".join(f"- {case['mechanism']}" for case in enriched_similar_cases if case.get('mechanism')) or ""
    avg_confidence = enriched_context.get("avg_confidence") or ""
    known_from_patients = enriched_context.get("known_interaction_from_patients")
    known_from_patients_str = "Unknown" if known_from_patients is None else ("True" if known_from_patients else "False")
    static_severity = enriched_context.get('static_severity', 'Unknown')
    
    user_prompt = (
        "A patient is concurrently prescribed two medications.\n\n"
        "Patient information:\n"
        f"- Age: {age}\n"
        f"- Sex: {sex}\n"
        f"- Comorbidities: {comorbidities}\n\n"
        "Drugs:\n"
        f"- Drug 1: {drug1}\n"
        f"- Drug 2: {drug2}\n"
        f"- Known interaction severity from static DDI tables: {static_severity}\n"
        f"- Known interaction from real-world patient cases?: {known_from_patients_str}\n"
        f"- Confidence of interaction: {avg_confidence}\n\n"
        "Mechanistic context:\n"
        f"{enriched_mechanisms}\n\n"
        f"Representative historical cases:\n {enriched_similar_cases}\n\n"
        "Note that 'Unknown' or 'False' with respect to the previous interaction fields indicates a lack of data in our database, "
        "not that the interaction is necessarily unknown elsewhere. Do not reference this fact in your response" 
        "While you should use the information provided in this prompt, do not directly refer to there being a 'prompt' in your response. "
        "For example, avoid phrases like 'as mentioned in the prompt' or 'based on the prompt' or 'differs from the prompt'.\n\n"
        "Please analyze this drug-drug interaction according to the format specified in the system instructions. "
        "Note that the end user does not know the format or existence of this prompt."
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
        "explanation": "<Provide a detailed explanation of how your prediction aligns with or differs from the known DDI severity. (2-3 sentences)>"
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




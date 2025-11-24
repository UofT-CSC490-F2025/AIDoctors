export type PredictionContent = {
  predicted_severity: 'Minor' | 'Moderate' | 'Major' | string;
  comparison_to_known_ddi: {
    known_interaction_exists: boolean | string;
    alignment_with_knowledge:
      | 'aligned'
      | 'contradicted'
      | 'insufficient_data'
      | string;
    explanation: string;
  };
  historical_cases_analysis: {
    cases_reviewed: string;
    risk_assessment:
      | 'increased_risk'
      | 'decreased_risk'
      | 'no_significant_change'
      | 'insufficient_data'
      | string;
    confidence: 'high' | 'medium' | 'low' | string;
    reasoning: string;
  };
  clinical_concern_assessment: {
    should_be_concerned: boolean | string;
    concern_level: 'high' | 'medium' | 'low' | string;
    primary_reason:
      | 'historical_cases_evidence'
      | 'severity_level'
      | 'patient_factors'
      | string;
    recommendations: string[];
  };
  summary: string;
};

export type AlertResult = {
  reasoning: string;
  content: PredictionContent;
  model_path?: string;
  known_severity?: string;
  drug1: string;
  drug2: string;
};

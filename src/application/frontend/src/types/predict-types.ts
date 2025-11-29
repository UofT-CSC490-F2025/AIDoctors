/**
 * Details comparing the prediction against existing medical knowledge.
 */
export type ComparisonToKnownDDI = {
  /** Whether a known interaction for this drug pair exists in the database. */
  known_interaction_exists: boolean; // JSON parsing should convert "true"/"false" strings to boolean
  /** Alignment of the predicted severity with known information. */
  alignment_with_knowledge: 'aligned' | 'contradicted' | 'insufficient_data';
  /** Detailed explanation of the comparison. */
  explanation: string;
};

/**
 * Analysis section based on historical patient cases (RAG context).
 */
export type HistoricalCasesAnalysis = {
  /** The number or range of cases reviewed (e.g., "10-20" or "15"). */
  cases_reviewed: string;
  /** The overall risk assessment based on historical data. */
  risk_assessment:
    | 'increased_risk'
    | 'decreased_risk'
    | 'no_significant_change'
    | 'insufficient_data';
  /** Model's confidence in the analysis. */
  confidence: 'high' | 'medium' | 'low';
  /** Detailed analysis and reasoning based on the historical evidence. */
  reasoning: string;
};

/**
 * Clinical assessment and recommended actions.
 */
export type ClinicalConcernAssessment = {
  /** Whether a healthcare provider should be concerned. */
  should_be_concerned: boolean; // JSON parsing should convert "true"/"false" strings to boolean
  /** The level of concern assessed by the model. */
  concern_level: 'high' | 'medium' | 'low';
  /** The primary factor driving the concern level. */
  primary_reason:
    | 'historical_cases_evidence'
    | 'severity_level'
    | 'patient_factors';
  /** A list of recommended actions for the clinical setting. */
  recommendations: string[];
};

/**
 * The full structured JSON object contained within the AlertResult.completion field.
 */
export type PredictionDetails = {
  /** The final predicted severity level. */
  predicted_severity: 'Minor' | 'Moderate' | 'Major' | 'Unknown';
  comparison_to_known_ddi: ComparisonToKnownDDI;
  historical_cases_analysis: HistoricalCasesAnalysis;
  clinical_concern_assessment: ClinicalConcernAssessment;
  /** A brief clinical summary suitable for healthcare providers. */
  summary: string;
};

/**
 * Statistics detailing the severity distribution for the known interaction.
 */
export type SeverityDistribution = {
  /** A mapping of severity level (string) to the count (number) of cases with that severity. */
  known_severity_count: Record<string, number>;
  /** The total number of cases used to calculate the severity distribution. */
  total_cases: number;
};

/**
 * Details of a single, representative historical case of a DDI.
 */
export type RepresentativeCase = {
  /** The anonymized ID for the patient in this case. */
  patient_uuid: string;
  /** The patient's age at the time of the interaction. */
  age: number;
  /** The patient's sex. */
  sex: string;
  /** The unified severity level of the interaction (e.g., 'Severe', 'Moderate'). */
  severity: string | null;
  /** The unified proposed mechanism of the interaction. */
  mechanism: string | null;
  /** The confidence score assigned to the DDI in this case. */
  confidence: number;
  /** A list of pre-existing conditions (comorbidities) for the patient. */
  comorbidities: string[];
};

/**
 * Represents the structured context enriched from the database (RAG approach).
 */
export type EnrichedContext = {
  similar_cases_count: number;
  known_interaction: boolean;
  avg_confidence: number | null;
  top_mechanisms: string[];
  representative_cases: RepresentativeCase[];
  /** Severity distribution statistics. Can be an empty object if no stats are available. */
  severity_distribution: SeverityDistribution | Record<string, never>;
};

/**
 * The final response structure from the DDI Prediction API endpoint.
 * Note: The 'completion' field is a JSON string that conforms to the PredictionDetails type.
 */
export type AlertResult = {
  /** The first drug involved in the interaction. */
  drug1: string;
  /** The second drug involved in the interaction. */
  drug2: string;
  /** The final predicted severity (derived from the model's completion). */
  severity: 'Minor' | 'Moderate' | 'Major' | 'Unknown';
  /** The step-by-step reasoning from the model (extracted from the <reasoning> tags). */
  reasoning: string;
  /** The raw JSON string output from the model, conforming to the PredictionDetails structure. */
  completion: string;
  /** The identifier for the underlying AI model used. */
  model_path: string;
  /** Optional echo of a known severity label provided in the request (if any). */
  known_severity: string | null;
  /** The database context used for RAG, or null if no enrichment occurred. */
  enriched_context: EnrichedContext | null;
};

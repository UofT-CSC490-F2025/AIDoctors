import { AlertResult, PredictionDetails } from '@/types/predict-types';

export const DUMMY_ALERTS: AlertResult[] = [
  {
    drug1: 'ibuprofen',
    drug2: 'lisinopril',
    severity: 'Major',
    reasoning: '',
    completion: '{\"predicted_severity\": \"Major\", \"comparison_to_known_ddi\": {\"explanation\": \"The static DDI tables list the ibuprofen\\u2011lisinopril interaction as moderate, reflecting average risk. In this patient, ischemic heart disease and chronic pain increase cardiovascular and renal susceptibility, aligning with historical cases that showed serious outcomes, thus we predict a higher, major severity.\"}, \"historical_cases_analysis\": {\"cases_reviewed\": 4, \"risk_assessment\": \"increased_risk\", \"confidence\": \"high\", \"reasoning\": \"All four cases had confidence 1.0 and shared key comorbidities (ischemic heart disease, hypertension, chronic pain, obesity/metabolic syndrome). Two cases had similarity scores >0.75, directly mirroring the current patient\'s profile, and were associated with adverse events attributable to the NSAID\\u2011ACE\\u2011I combination. This real\\u2011world evidence supports an elevated risk beyond the generic moderate rating.\"}, \"clinical_concern_assessment\": {\"should_be_concerned\": true, \"concern_level\": \"high\", \"primary_reason\": \"historical_cases_evidence\", \"recommendations\": [\"Monitor blood pressure and renal function (serum creatinine, eGFR, potassium) closely after initiating or continuing ibuprofen.\", \"Consider substituting ibuprofen with acetaminophen or another non\\u2011NSAID analgesic for chronic pain.\", \"If NSAID use is unavoidable, use the lowest effective dose for the shortest duration and re\\u2011evaluate the need for lisinopril dose adjustment.\"]}, \"summary\": \"In a 52\\u2011year\\u2011old male with ischemic heart disease and chronic pain, concomitant ibuprofen and lisinopril poses a major interaction risk, supported by high\\u2011confidence historical cases showing clinically significant hypertension or renal events. Close monitoring, renal labs, and an alternative pain regimen are strongly advised.\"}',
  
    model_path: 'openai.gpt-oss-120b-1:0',
    known_severity: 'Moderate',
    enriched_context: {
      similar_cases_count: 4,
      static_severity: 'Moderate',
      known_interaction_from_patients: true,
      avg_confidence: 1.0,
      top_mechanisms: ['risk or severity of adverse effects'],
      representative_cases: [
        {
          patient_uuid: '36ddb5d8-028f-c544-2fe7-b3863ab3ee65',
          age: 44,
          sex: 'M',
          similarity_score: 0.96,
          mechanism: null,
          confidence: 1.0,
          comorbidities: [
            'Ischemic heart disease (disorder)',
            'Chronic pain (finding)',
            'Essential hypertension (disorder)',
            'Body mass index 30+ - obesity (finding)',
            'Metabolic syndrome X (disorder)',
          ],
        },
        {
          patient_uuid: 'ee0fc0f5-ed3b-dc1b-bca5-c16f7eaeef64',
          age: 52,
          sex: 'M',
          similarity_score: 0.75,
          mechanism: null,
          confidence: 1.0,
          comorbidities: [
            'Chronic pain (finding)',
            'Essential hypertension (disorder)',
            'Hyperlipidemia (disorder)',
            'Body mass index 30+ - obesity (finding)',
          ],
        },
        {
          patient_uuid: '1c5f0118-d669-00c5-ddac-5a8cc06a2bac',
          age: 43,
          sex: 'M',
          similarity_score: 0.455,
          mechanism: null,
          confidence: 1.0,
          comorbidities: [
            'Essential hypertension (disorder)',
            'Hyperlipidemia (disorder)',
            'Body mass index 30+ - obesity (finding)',
          ],
        },
        {
          patient_uuid: '17751391-0d94-10d9-8569-184b223ba3dc',
          age: 65,
          sex: 'F',
          similarity_score: 0.435,
          mechanism: null,
          confidence: 1.0,
          comorbidities: [
            'Ischemic heart disease (disorder)',
            'Essential hypertension (disorder)',
            'Prediabetes (finding)',
          ],
        },
      ],
      severity_distribution: {
        known_severity_count: { Moderate: 13 },
        total_cases: 13,
      },
    },
  },
];

import { AlertResult, PredictionDetails } from '@/types/predict-types';

const DUMMY_PREDICTION_DETAILS: PredictionDetails[] = [
  {
    predicted_severity: 'Major',
    comparison_to_known_ddi: {
      known_interaction_exists: true,
      alignment_with_knowledge: 'aligned',
      explanation:
        'The predicted major severity aligns with pharmacological knowledge regarding the synergistic increased bleeding risk.',
    },
    historical_cases_analysis: {
      cases_reviewed: '25+',
      risk_assessment: 'increased_risk',
      confidence: 'high',
      reasoning:
        'Analysis of 25 similar patient records (age >65, multiple comorbidities) shows significant increase in hospitalization rate due to severe bleeding events within 90 days of co-therapy initiation.',
    },
    clinical_concern_assessment: {
      should_be_concerned: true,
      concern_level: 'high',
      primary_reason: 'severity_level',
      recommendations: [
        'Increase INR monitoring frequency (e.g., weekly)',
        'Assess need for GI protection (PPI)',
        'Educate patient on signs of major bleeding (e.g., melena, hematuria)',
        'Consider alternative antiplatelet agent or dose reduction for Warfarin',
      ],
    },
    summary:
      'High clinical concern due to the Major predicted severity and strong supporting evidence from historical patient data, indicating a substantial increased risk of bleeding.',
  },
  {
    predicted_severity: 'Major',
    comparison_to_known_ddi: {
      known_interaction_exists: true, // "true" in raw output
      alignment_with_knowledge: 'contradicted',
      explanation:
        'Authoritative drug interaction references (Lexicomp, Micromedex, FDA labeling) list a major interaction between warfarin and aspirin due to additive anticoagulant/antiplatelet effects, resulting in a significantly increased risk of major bleeding. This contradicts the user\u2011provided flag that no known interaction exists.',
    },
    historical_cases_analysis: {
      cases_reviewed:
        'dozens of published case reports and >30,000 patients in cohort studies',
      risk_assessment: 'increased_risk',
      confidence: 'high',
      reasoning:
        'Large observational datasets and meta\u2011analyses consistently demonstrate a 2\u2011 to 3\u2011fold rise in major bleeding when aspirin is added to warfarin, with higher absolute risk in patients >65\u202fy and those with hypertension or diabetes. The evidence is robust despite the lack of user\u2011specific case listings.',
    },
    clinical_concern_assessment: {
      should_be_concerned: true, // "true" in raw output
      concern_level: 'high',
      primary_reason: 'severity_level',
      recommendations: [
        'Obtain baseline INR and monitor INR more frequently (e.g., weekly) after initiating aspirin.',
        'Re\u2011evaluate the indication for aspirin; discontinue if used for primary prevention.',
        'If aspirin is required, consider lowering the warfarin dose and add a proton\u2011pump inhibitor for GI protection.',
        'Educate the patient on signs of bleeding (e.g., melena, hematuria, unexplained bruising) and advise immediate medical attention if they occur.',
      ],
    },
    summary:
      "Warfarin and aspirin together constitute a major drug\u2011drug interaction that substantially raises the risk of serious bleeding, especially in a 65\u2011year\u2011old male with hypertension and diabetes. The interaction is well\u2011documented, contrary to the user's claim of no known interaction. Clinicians should treat this combination with high concern, closely monitor anticoagulation parameters, reassess the necessity of aspirin, and implement protective measures.",
  },
];

export const DUMMY_ALERTS: AlertResult[] = [
  {
    drug1: 'Warfarin',
    drug2: 'Aspirin',
    severity: 'Major',
    reasoning:
      'Step-by-step reasoning:\n1. Pharmacological Review: Warfarin is an anticoagulant; Aspirin is an antiplatelet. Combined use creates synergistic anti-hemostatic effects.\n2. Context Analysis: RAG query found 28 similar cases, most showing moderate to severe outcomes.\n3. Severity Prediction: Based on mechanisms and case data, predicted severity is Major.\n4. Conclusion: Immediate clinical action required to mitigate high bleeding risk.',
    completion: JSON.stringify(DUMMY_PREDICTION_DETAILS[0]),
    model_path: 'gemini-2.5-flash-preview-09-2025',
    known_severity: 'Moderate',
    enriched_context: {
      similar_cases_count: 28,
      static_severity: 'Moderate',
      known_interaction_from_patients: true,
      avg_confidence: 0.92,
      top_mechanisms: [
        'Anti-hemostatic synergism',
        'Platelet aggregation inhibition',
        'PK/PD Interference',
      ],
      representative_cases: [
        {
          patient_uuid: 'pat-001-f2a',
          age: 72,
          sex: 'Female',
          severity: 'Severe',
          mechanism: 'Synergistic bleeding risk elevation',
          confidence: 0.95,
          comorbidities: ['Hypertension', 'Afib'],
        },
        {
          patient_uuid: 'pat-002-c7d',
          age: 68,
          sex: 'Male',
          severity: 'Moderate',
          mechanism: 'Increased INR due to unknown mechanism',
          confidence: 0.88,
          comorbidities: ['Diabetes'],
        },
        {
          patient_uuid: 'pat-003-e8b',
          age: 76,
          sex: 'Male',
          severity: 'Major',
          mechanism: 'Anti-platelet effects combined with anti-coagulation',
          confidence: 0.98,
          comorbidities: ['CKD', 'Smoker'],
        },
      ],
      severity_distribution: {
        known_severity_count: { Major: 15, Moderate: 10, Minor: 3 },
        total_cases: 28,
      },
    },
  },
  {
    drug1: 'Warfarin',
    drug2: 'Aspirin',
    severity: 'Major',
    reasoning:
      'We need to answer per format. The user says known interaction in clinical sources: False, meaning there is no known interaction? Actually warfarin and aspirin have known interaction (increased bleeding risk). But user says known interaction false. We must evaluate. According to our knowledge, warfarin + aspirin is a major interaction (increased bleeding). So we need to compare prediction to known DDI: known_interaction_exists false per input, but we know it\'s true. So we will say known_interaction_exists: true (contradicts input). But the system says we should compare our prediction to known clinical interaction if it exists. Since the user says false, we need to note discrepancy. Provide analysis.\n\nSeverity: Major (increased bleeding risk). Predicted severity major.\n\nComparison: known_interaction_exists: true (clinical sources do report interaction). alignment: contradicted (our assessment differs from user-provided "False").\n\nHistorical cases: none provided; we can say insufficient data, but we can reference literature: many cases of bleeding. So risk increased. Cases reviewed: many case reports, high confidence.\n\nClinical concern: should be concerned true, high level, primary reason severity and known interaction. Recommendations: monitor INR, avoid concomitant use if possible, consider dose reduction, use PPI for GI protection, consider alternative antiplatelet.\n\nNow format: include reasoning block. Then JSON as specified.\n\n\n**Step‑1 – Pharmacologic relationship**\n\n- **Warfarin** is a vitamin‑K antagonist that inhibits synthesis of clotting factors II, VII, IX, and X. Its anticoagulant effect is monitored by the INR and is highly sensitive to changes in hepatic metabolism, protein binding, and platelet function.\n- **Aspirin** irreversibly inhibits cyclo‑oxygenase‑1 (COX‑1) in platelets, impairing thromboxane‑A₂ production and thus platelet aggregation.  \n- When combined, aspirin adds an antiplatelet effect to the anticoagulant effect of warfarin, markedly increasing the risk of **major bleeding** (gastrointestinal, intracranial, etc.). The interaction is pharmacodynamic (additive effect on hemostasis) and is well‑documented in major drug interaction compendia (e.g., Lexicomp, Micromedex, FDA labeling).\n\n**Step‑2 – Predict severity**\n\nGiven the robust evidence of a clinically significant increase in bleeding risk, the interaction is classified as **Major**.\n\n**Step‑3 – Compare to user‑provided “known interaction = False”**\n\n- Authoritative sources (Lexicomp, Micromedex, FDA, WHO) list a *major* interaction between warfarin and aspirin.  \n- Therefore the user’s statement that a known interaction does **not** exist is **incorrect**. Our assessment **contradicts** the user‑provided flag.\n\n**Step‑4 – Historical case evidence**\n\n- Numerous case reports and observational studies have documented serious hemorrhagic events when warfarin and aspirin are co‑prescribed, especially in older adults and those with comorbidities such as hypertension and diabetes (both risk factors for bleeding).  \n- A meta‑analysis of 12 cohort studies (≈30,000 patients) showed a **2‑ to 3‑fold increase** in major bleeding when aspirin was added to warfarin (RR ≈ 2.4, 95 % CI 1.8‑3.1).  \n- In patients ≥65 y, the absolute risk increase is ≈4–5 % per year.  \n- Although the user supplied no specific historical cases, the broader literature provides high‑confidence evidence of increased risk.\n\n**Step‑5 – Clinical concern for this patient**\n\n- Age 65, hypertension, and diabetes further predispose to bleeding.  \n- The interaction is major and well‑supported; therefore clinicians should be **highly concerned**.  \n- Recommended actions include: close INR monitoring, consider dose reduction of warfarin, evaluate the necessity of aspirin (e.g., if primary prevention, discontinue), use gastro‑protective agents, and educate the patient on signs of bleeding.\n\n**Conclusion:** The warfarin‑aspirin combination is a major, well‑documented interaction that markedly raises bleeding risk, especially in an older patient with cardiovascular comorbidities. Immediate clinical attention is warranted.',
    completion: JSON.stringify(DUMMY_PREDICTION_DETAILS[1]),
    model_path: 'openai.gpt-oss-120b-1:0',
    known_severity: null,
    enriched_context: {
      static_severity: '',
      similar_cases_count: 0,
      known_interaction_from_patients: false,
      avg_confidence: 0.0,
      severity_distribution: {},
      top_mechanisms: [],
      representative_cases: [],
    },
  },
];

import { AlertResult } from "@/types/predict-types";

export const DUMMY_ALERTS: AlertResult[] = [
  {
    drug1: 'Warfarin',
    drug2: 'Aspirin',
    severity: 'Major',
    reasoning:
      "We need to output in required format. The user provides no start/end dates, overlap days, no mechanistic context, known interaction false. So there is no known DDI. Need to predict severity based on pharmacology: Warfarin + Aspirin is known to increase bleeding risk, a major interaction. But user says known interaction in clinical sources: False. That conflicts with known knowledge. We must treat that as \"known_interaction_exists\": false per user input. Then we need to predict severity based on pharmacology: likely major. Provide comparison: alignment? Since known interaction false but we think there is a major interaction, we have contradiction. Provide explanation.\n\nHistorical cases: none provided (empty list). So cases reviewed = 0, risk assessment insufficient.\n\nClinical concern: should be concerned because severity major.\n\nProvide recommendations: monitor INR more frequently, consider alternative antiplatelet therapy, use lowest aspirin dose, evaluate bleeding risk.\n\nNow format: include <reasoning> tags with step-by-step.\n\nThen JSON fields as specified.\n\nLet's craft.\n**Step 1: Identify pharmacological interaction potential**  \n- **Warfarin** is a vitamin K antagonist anticoagulant metabolized primarily by CYP2C9 and is highly protein‑bound. Its anticoagulant effect is monitored via INR.  \n- **Aspirin** (acetylsalicylic acid) irreversibly inhibits platelet cyclooxygenase‑1 (COX‑1), reducing thromboxane A₂ and impairing primary hemostasis.  \n\nWhen both agents are used together, the anticoagulant effect of warfarin (secondary hemostasis) and the antiplatelet effect of aspirin (primary hemostasis) act synergistically, markedly increasing the risk of gastrointestinal and intracranial bleeding. This interaction is well‑documented in major drug interaction references (e.g., Lexicomp, Micromedex, FDA).  \n\n**Step 2: Predict severity**  \nGiven the strong mechanistic basis and clinical reports of serious bleeding, the interaction is classified as **Major**.\n\n**Step 3: Compare with user‑provided “known interaction” flag**  \nThe user states *Known interaction in clinical sources: False*. This contradicts established pharmacology. Therefore:\n- `known_interaction_exists` = false (as per user input)  \n- Our assessment *contradicts* the user‑provided claim.\n\n**Step 4: Historical case evidence**  \nNo specific cases were supplied (`[]`). In the literature, dozens of case series and pharmacovigilance reports describe increased bleeding when warfarin and aspirin are co‑prescribed, especially in elderly patients with comorbidities such as hypertension and diabetes. Because no cases are supplied, we must acknowledge insufficient direct case data for this request, but we can cite the general evidence base.\n\n**Step 5: Clinical concern assessment**  \n- Severity: Major → warrants high clinical vigilance.  \n- Even though the user’s dataset does not list a known interaction, the pharmacologic reality dictates concern.  \n- Patient factors (age 76, hypertension, diabetes) further increase bleeding risk.\n\nThus, clinicians should be **concerned** and take proactive measures.\n\n**Step 6: Recommendations**  \n1. Re‑evaluate the need for concomitant aspirin; consider using a lower‑dose aspirin (≤81 mg) or alternative antiplatelet if indicated.  \n2. Increase INR monitoring frequency (e.g., weekly after initiation or dose change).  \n3. Educate the patient on signs of bleeding (e.g., melena, hematuria, bruising).  \n4. Assess gastrointestinal protection (e.g., PPI) if aspirin is continued.  \n5. Consider dose reduction of warfarin if therapeutic INR exceeds target range.",
      completion: {
        predicted_severity: 'Major',
        comparison_to_known_ddi: {
          known_interaction_exists: true,
          alignment_with_knowledge: 'aligned',
          explanation:
            'DDI tables flag increased bleed risk; historical outcomes suggest a higher severity for this patient.',
        },
        historical_cases_analysis: {
          cases_reviewed: '18',
          risk_assessment: 'increased_risk',
          confidence: 'high',
          reasoning:
            'Multiple similar patients (age >60, hypertension) showed INR spikes within 72h of co-administration.',
        },
        clinical_concern_assessment: {
          should_be_concerned: true,
          concern_level: 'high',
          primary_reason: 'historical_cases_evidence',
          recommendations: [
            'Increase INR monitoring within 48 hours',
            'Consider gastroprotection and bleed risk counseling',
            'Evaluate alternative antiplatelet if possible',
          ],
        },
        summary:
          'Upgrade to major concern due to cohort evidence of bleeding events in similar patients.',
      },
    model_path: "openai.gpt-oss-120b-1:0",
    known_severity: 'Moderate',
    enriched_context: {
      similar_cases_count: 0,
      known_interaction: false,
      avg_confidence: 0,
      severity_distribution: {
        known_severity_count: 70,
        total_cases: 100,
      },
      top_mechanisms: [],
      representative_cases: []
    }
  },
];

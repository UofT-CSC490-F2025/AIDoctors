export const DUMMY_ALERTS = [
  {
    reasoning:
      'Known interaction exists. Cohort outcomes show elevated bleeding risk when combining warfarin with aspirin for similar profiles.',
    known_severity: 'Moderate',
    drug1: 'Warfarin',
    drug2: 'Aspirin',
    content: {
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
  },
  {
    reasoning:
      'No strong historical signals beyond known table interaction. Standard caution recommended.',
    known_severity: 'Minor',
    drug1: 'Metformin',
    drug2: 'Amlodipine',
    content: {
      predicted_severity: 'Moderate',
      comparison_to_known_ddi: {
        known_interaction_exists: true,
        alignment_with_knowledge: 'aligned',
        explanation:
          'Table lists mild interaction; slight elevation based on age and comorbidity profile.',
      },
      historical_cases_analysis: {
        cases_reviewed: '6',
        risk_assessment: 'no_significant_change',
        confidence: 'medium',
        reasoning:
          'Few similar cases; no clear increase in adverse outcomes beyond expected.',
      },
      clinical_concern_assessment: {
        should_be_concerned: true,
        concern_level: 'medium',
        primary_reason: 'patient_factors',
        recommendations: [
          'Monitor vitals during initiation',
          'Reassess after first week',
          'Educate patient on symptoms to report',
        ],
      },
      summary:
        'Slightly elevated concern due to age and comorbidities; monitor but proceed with caution.',
    },
  },
];

import React from 'react';
import { render, screen, within } from '@testing-library/react';
import { Alert } from '@/components/ui/alert';

const baseInfo = {
  drug1: 'A',
  drug2: 'B',
  severity: 'Major',
  reasoning: '',
  model_path: 'm1',
  known_severity: 'Moderate',
  completion: JSON.stringify({
    predicted_severity: 'Major',
    comparison_to_known_ddi: {
      known_interaction_exists: true,
      alignment_with_knowledge: 'aligned',
      explanation: 'exp',
    },
    historical_cases_analysis: {
      cases_reviewed: '10',
      risk_assessment: 'increased_risk',
      confidence: 'high',
      reasoning: 'reason',
    },
    clinical_concern_assessment: {
      should_be_concerned: true,
      concern_level: 'high',
      primary_reason: 'severity_level',
      recommendations: ['rec1'],
    },
    summary: 'summary text',
  }),
  enriched_context: {
    similar_cases_count: 2,
    known_interaction: true,
    avg_confidence: 0.9,
    top_mechanisms: ['mA', 'mB'],
    representative_cases: [
      {
        patient_uuid: 'u1',
        age: 70,
        sex: 'F',
        severity: 'Moderate',
        mechanism: 'mechanism long text here',
        confidence: 0.88,
        comorbidities: [],
      },
      {
        patient_uuid: 'u2',
        age: 40,
        sex: 'M',
        severity: 'Minor',
        mechanism: 'another mechanism long text',
        confidence: 0.65,
        comorbidities: [],
      },
    ],
    severity_distribution: { known_severity_count: {}, total_cases: 0 },
  },
} as const;

// Utility builder
function buildInfo(overrides: Partial<any> = {}) {
  return {
    drug1: 'A',
    drug2: 'B',
    severity: 'Unknown',
    reasoning: '',
    model_path: 'm1',
    known_severity: 'Moderate',
    completion: JSON.stringify({
      predicted_severity: 'Major',
      summary: 'S',
      comparison_to_known_ddi: {
        known_interaction_exists: true,
        alignment_with_knowledge: 'aligned',
        explanation: 'E1',
      },
      historical_cases_analysis: {
        cases_reviewed: '10',
        risk_assessment: 'increased_risk',
        confidence: 'high',
        reasoning: 'E2',
      },
      clinical_concern_assessment: {
        should_be_concerned: true,
        concern_level: 'high',
        primary_reason: 'severity_level',
        recommendations: ['R1', 'R2'],
      },
    }),
    enriched_context: {
      similar_cases_count: 5,
      known_interaction: true,
      avg_confidence: 0.9,
      top_mechanisms: ['M1', 'M2'],
      representative_cases: [
        {
          patient_uuid: 'p1',
          age: 60,
          sex: 'M',
          severity: 'Severe',
          mechanism: 'Mechanism Long Text',
          confidence: 0.8,
          comorbidities: [],
        },
      ],
      severity_distribution: { known_severity_count: {}, total_cases: 0 },
    },
    ...overrides,
  };
}

describe('Alert', () => {
  test('renders header, drug names, model path, known severity, predicted severity', () => {
    render(<Alert info={baseInfo} />);

    screen.getByText('DDI ALERT');
    screen.getByText('A + B');
    screen.getByText(/Model:/);
    screen.getByText('m1');
    screen.getByText('Known: Moderate');
    screen.getByText('Predicted: Major');
  });

  test('parses JSON completion and renders summary and all sections', () => {
    render(<Alert info={buildInfo()} />);

    expect(screen.getByText('S')).toBeInTheDocument();
    expect(screen.getByText('Known Interaction Exists')).toBeInTheDocument();
    expect(screen.getByText(/Alignment:/)).toHaveTextContent('aligned');
    expect(screen.getByText('E1')).toBeInTheDocument();

    expect(screen.getByText(/10 cases/)).toBeInTheDocument();
    expect(screen.getByText('increased risk')).toBeInTheDocument();
    expect(screen.getByText('E2')).toBeInTheDocument();

    expect(screen.getByText(/Concern Level: HIGH/)).toBeInTheDocument();
    expect(screen.getByText('R1')).toBeInTheDocument();
    expect(screen.getByText('R2')).toBeInTheDocument();
  });

  test('enriched context: renders top mechanisms and representative cases', () => {
    render(<Alert info={baseInfo} />);

    screen.getByText('Cases Found:');
    screen.getByText('2');
    screen.getByText(/Top Mechanisms:/);
    screen.getByText('mA, mB');

    screen.getByText('Case #1');
    screen.getByText('Case #2');

    const case1 = screen.getByText('Case #1').closest('div');
    const case2 = screen.getByText('Case #2').closest('div');

    within(case1).getByText(/Severity:/);
    within(case1).getByText(/Age\/Sex:/);
    within(case1).getByText(/Confidence:/);

    within(case2).getByText(/Severity:/);
    within(case2).getByText(/Age\/Sex:/);
    within(case2).getByText(/Confidence:/);
  });

  test('no representative cases → section omitted', () => {
    const info = buildInfo({
      enriched_context: {
        ...buildInfo().enriched_context,
        representative_cases: [],
      },
    });
    render(<Alert info={info} />);
    expect(screen.queryByText(/Representative Historical Cases/)).toBeNull();
  });

  test('completion invalid JSON → fallback empty object, fallback severity + summary', () => {
    const info = buildInfo({
      completion: 'INVALID JSON',
      severity: 'Moderate',
    });
    render(<Alert info={info} />);

    // fallback predicted severity = info.severity
    expect(screen.getByText(/Predicted: Moderate/)).toBeInTheDocument();

    // fallback summary text
    expect(screen.getByText(/No brief summary available/)).toBeInTheDocument();
  });

  test('known_severity null → omits known severity badge', () => {
    const info = buildInfo({ known_severity: null });
    render(<Alert info={info} />);
    expect(screen.queryByText(/Known:/)).toBeNull();
  });

  test('model_path null → model path omitted', () => {
    const info = buildInfo({ model_path: null });
    render(<Alert info={info} />);
    expect(screen.queryByText(/Model:/)).toBeNull();
  });

  test('isPreview = true → grid remains single column', () => {
    render(<Alert info={buildInfo()} isPreview={true} />);
    const grid = screen
      .getAllByText(/Knowledge & Context/)[0]
      .closest('div')!.parentElement;
    expect(grid?.className).not.toContain('lg:grid-cols-3');
  });

  test('severity style Major', () => {
    const info = buildInfo({
      completion: JSON.stringify({
        predicted_severity: 'Major',
      }),
      enriched_context: null,
    });
    render(<Alert info={info} />);
    const badge = screen.getByText(/Predicted: Major/).closest('span');
    expect(badge?.className).toContain('bg-red-100');
    expect(badge?.className).toContain('text-red-800');
  });

  test('severity style Moderate', () => {
    const info = buildInfo({
      completion: JSON.stringify({
        predicted_severity: 'Moderate',
      }),
      enriched_context: null,
    });
    render(<Alert info={info} />);
    const badge = screen.getByText(/Predicted: Moderate/).closest('span');
    expect(badge?.className).toContain('bg-yellow-100');
    expect(badge?.className).toContain('text-yellow-800');
  });

  test('severity style Minor', () => {
    const info = buildInfo({
      completion: JSON.stringify({
        predicted_severity: 'Minor',
      }),
      enriched_context: null,
    });
    render(<Alert info={info} />);
    const badge = screen.getByText(/Predicted: Minor/).closest('span');
    expect(badge?.className).toContain('bg-green-100');
    expect(badge?.className).toContain('text-green-800');
  });

  test('severity style Unknown (default branch)', () => {
    const info = buildInfo({
      completion: JSON.stringify({
        predicted_severity: 'Unknown',
      }),
      enriched_context: null,
    });
    render(<Alert info={info} />);
    const badge = screen.getByText(/Predicted: Unknown/).closest('span');
    expect(badge?.className).toContain('bg-gray-100');
    expect(badge?.className).toContain('text-gray-700');
  });

  test('no recommendations → fallback message', () => {
    const info = buildInfo({
      completion: JSON.stringify({
        predicted_severity: 'Major',
        clinical_concern_assessment: {
          should_be_concerned: false,
          concern_level: 'low',
          primary_reason: 'patient_factors',
          recommendations: [],
        },
      }),
      enriched_context: null,
    });
    render(<Alert info={info} />);
    expect(
      screen.getByText(/No specific recommendations provided/)
    ).toBeInTheDocument();
  });

  test('no enriched_context → no enrichment section', () => {
    const info = buildInfo({ enriched_context: null });
    render(<Alert info={info} />);
    expect(screen.queryByText(/Database Enrichment/)).toBeNull();
  });
});

import { describe, expect, it } from '@jest/globals';
import { DUMMY_ALERTS } from '@/utils/testing';

describe('DUMMY_ALERTS', () => {
  it('should be an array', () => {
    expect(Array.isArray(DUMMY_ALERTS)).toBe(true);
  });

  it('should contain exactly 2 alerts', () => {
    expect(DUMMY_ALERTS).toHaveLength(2);
  });

  describe('First alert (Warfarin + Aspirin)', () => {
    const firstAlert = DUMMY_ALERTS[0];

    it('should have correct drug names', () => {
      expect(firstAlert.drug1).toBe('Warfarin');
      expect(firstAlert.drug2).toBe('Aspirin');
    });

    it('should have known_severity of Moderate', () => {
      expect(firstAlert.known_severity).toBe('Moderate');
    });

    it('should have reasoning field', () => {
      expect(firstAlert.reasoning).toBeDefined();
      expect(typeof firstAlert.reasoning).toBe('string');
      expect(firstAlert.reasoning.length).toBeGreaterThan(0);
    });

    it('should have content object with required fields', () => {
      expect(firstAlert.content).toBeDefined();
      expect(firstAlert.content.predicted_severity).toBe('Major');
      expect(firstAlert.content.comparison_to_known_ddi).toBeDefined();
      expect(firstAlert.content.historical_cases_analysis).toBeDefined();
      expect(firstAlert.content.clinical_concern_assessment).toBeDefined();
      expect(firstAlert.content.summary).toBeDefined();
    });

    it('should have comparison_to_known_ddi with correct structure', () => {
      const comparison = firstAlert.content.comparison_to_known_ddi;
      expect(comparison.known_interaction_exists).toBe(true);
      expect(comparison.alignment_with_knowledge).toBe('aligned');
      expect(typeof comparison.explanation).toBe('string');
    });

    it('should have historical_cases_analysis with correct structure', () => {
      const historical = firstAlert.content.historical_cases_analysis;
      expect(historical.cases_reviewed).toBe('18');
      expect(historical.risk_assessment).toBe('increased_risk');
      expect(historical.confidence).toBe('high');
      expect(typeof historical.reasoning).toBe('string');
    });

    it('should have clinical_concern_assessment with recommendations', () => {
      const concern = firstAlert.content.clinical_concern_assessment;
      expect(concern.should_be_concerned).toBe(true);
      expect(concern.concern_level).toBe('high');
      expect(concern.primary_reason).toBe('historical_cases_evidence');
      expect(Array.isArray(concern.recommendations)).toBe(true);
      expect(concern.recommendations.length).toBeGreaterThan(0);
    });

    it('should have at least 3 recommendations', () => {
      expect(firstAlert.content.clinical_concern_assessment.recommendations).toHaveLength(3);
    });
  });

  describe('Second alert (Metformin + Amlodipine)', () => {
    const secondAlert = DUMMY_ALERTS[1];

    it('should have correct drug names', () => {
      expect(secondAlert.drug1).toBe('Metformin');
      expect(secondAlert.drug2).toBe('Amlodipine');
    });

    it('should have known_severity of Minor', () => {
      expect(secondAlert.known_severity).toBe('Minor');
    });

    it('should have reasoning field', () => {
      expect(secondAlert.reasoning).toBeDefined();
      expect(typeof secondAlert.reasoning).toBe('string');
    });

    it('should have content object with predicted_severity of Moderate', () => {
      expect(secondAlert.content.predicted_severity).toBe('Moderate');
    });

    it('should have comparison_to_known_ddi indicating aligned interaction', () => {
      const comparison = secondAlert.content.comparison_to_known_ddi;
      expect(comparison.known_interaction_exists).toBe(true);
      expect(comparison.alignment_with_knowledge).toBe('aligned');
    });

    it('should have historical_cases_analysis with medium confidence', () => {
      const historical = secondAlert.content.historical_cases_analysis;
      expect(historical.cases_reviewed).toBe('6');
      expect(historical.risk_assessment).toBe('no_significant_change');
      expect(historical.confidence).toBe('medium');
    });

    it('should have clinical_concern_assessment with medium concern level', () => {
      const concern = secondAlert.content.clinical_concern_assessment;
      expect(concern.should_be_concerned).toBe(true);
      expect(concern.concern_level).toBe('medium');
      expect(concern.primary_reason).toBe('patient_factors');
    });

    it('should have recommendations array', () => {
      const recommendations = secondAlert.content.clinical_concern_assessment.recommendations;
      expect(Array.isArray(recommendations)).toBe(true);
      expect(recommendations.length).toBeGreaterThan(0);
    });
  });

  describe('Alert structure consistency', () => {
    it('should have consistent structure across all alerts', () => {
      DUMMY_ALERTS.forEach((alert, index) => {
        expect(alert).toHaveProperty('reasoning');
        expect(alert).toHaveProperty('known_severity');
        expect(alert).toHaveProperty('drug1');
        expect(alert).toHaveProperty('drug2');
        expect(alert).toHaveProperty('content');
        expect(alert.content).toHaveProperty('predicted_severity');
        expect(alert.content).toHaveProperty('comparison_to_known_ddi');
        expect(alert.content).toHaveProperty('historical_cases_analysis');
        expect(alert.content).toHaveProperty('clinical_concern_assessment');
        expect(alert.content).toHaveProperty('summary');
      });
    });

    it('should have all concern assessments with recommendations', () => {
      DUMMY_ALERTS.forEach((alert) => {
        const concern = alert.content.clinical_concern_assessment;
        expect(Array.isArray(concern.recommendations)).toBe(true);
        expect(concern.recommendations.length).toBeGreaterThan(0);
        concern.recommendations.forEach((rec) => {
          expect(typeof rec).toBe('string');
          expect(rec.length).toBeGreaterThan(0);
        });
      });
    });

    it('should have valid severity levels', () => {
      const validKnownSeverities = ['Minor', 'Moderate', 'Major', 'Severe'];
      const validPredictedSeverities = ['Minor', 'Moderate', 'Major', 'Severe'];

      DUMMY_ALERTS.forEach((alert) => {
        expect(validKnownSeverities).toContain(alert.known_severity);
        expect(validPredictedSeverities).toContain(alert.content.predicted_severity);
      });
    });

    it('should have valid confidence levels in historical analysis', () => {
      const validConfidenceLevels = ['low', 'medium', 'high'];

      DUMMY_ALERTS.forEach((alert) => {
        expect(validConfidenceLevels).toContain(
          alert.content.historical_cases_analysis.confidence
        );
      });
    });

    it('should have valid concern levels in clinical assessment', () => {
      const validConcernLevels = ['low', 'medium', 'high', 'critical'];

      DUMMY_ALERTS.forEach((alert) => {
        expect(validConcernLevels).toContain(
          alert.content.clinical_concern_assessment.concern_level
        );
      });
    });
  });
});

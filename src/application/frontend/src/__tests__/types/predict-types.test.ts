/// <reference types="@testing-library/jest-dom" />
import { describe, expect, it } from '@jest/globals';
import {
  PredictionContent,
  AlertResult,
} from '@/types/predict-types';

describe('Predict Types', () => {
  describe('PredictionContent Type', () => {
    it('should accept valid PredictionContent with all required fields', () => {
      const validContent: PredictionContent = {
        predicted_severity: 'Major',
        comparison_to_known_ddi: {
          known_interaction_exists: true,
          alignment_with_knowledge: 'aligned',
          explanation: 'Test explanation',
        },
        historical_cases_analysis: {
          cases_reviewed: '50',
          risk_assessment: 'increased_risk',
          confidence: 'high',
          reasoning: 'Test reasoning',
        },
        clinical_concern_assessment: {
          should_be_concerned: true,
          concern_level: 'high',
          primary_reason: 'severity_level',
          recommendations: ['Monitor closely', 'Consider alternatives'],
        },
        summary: 'Test summary',
      };

      expect(validContent).toBeDefined();
      expect(validContent.predicted_severity).toBe('Major');
      expect(validContent.summary).toBe('Test summary');
    });

    it('should accept predicted_severity as Minor', () => {
      const content: PredictionContent = {
        predicted_severity: 'Minor',
        comparison_to_known_ddi: {
          known_interaction_exists: false,
          alignment_with_knowledge: 'aligned',
          explanation: 'Test',
        },
        historical_cases_analysis: {
          cases_reviewed: '10',
          risk_assessment: 'no_significant_change',
          confidence: 'low',
          reasoning: 'Test',
        },
        clinical_concern_assessment: {
          should_be_concerned: false,
          concern_level: 'low',
          primary_reason: 'patient_factors',
          recommendations: [],
        },
        summary: 'Test',
      };

      expect(content.predicted_severity).toBe('Minor');
    });

    it('should accept predicted_severity as Moderate', () => {
      const content: PredictionContent = {
        predicted_severity: 'Moderate',
        comparison_to_known_ddi: {
          known_interaction_exists: true,
          alignment_with_knowledge: 'aligned',
          explanation: 'Test',
        },
        historical_cases_analysis: {
          cases_reviewed: '25',
          risk_assessment: 'increased_risk',
          confidence: 'medium',
          reasoning: 'Test',
        },
        clinical_concern_assessment: {
          should_be_concerned: true,
          concern_level: 'medium',
          primary_reason: 'historical_cases_evidence',
          recommendations: ['Monitor'],
        },
        summary: 'Test',
      };

      expect(content.predicted_severity).toBe('Moderate');
    });

    it('should accept predicted_severity as custom string', () => {
      const content: PredictionContent = {
        predicted_severity: 'Critical',
        comparison_to_known_ddi: {
          known_interaction_exists: true,
          alignment_with_knowledge: 'aligned',
          explanation: 'Test',
        },
        historical_cases_analysis: {
          cases_reviewed: '100',
          risk_assessment: 'increased_risk',
          confidence: 'high',
          reasoning: 'Test',
        },
        clinical_concern_assessment: {
          should_be_concerned: true,
          concern_level: 'high',
          primary_reason: 'severity_level',
          recommendations: ['Urgent action required'],
        },
        summary: 'Test',
      };

      expect(content.predicted_severity).toBe('Critical');
    });

    it('should accept known_interaction_exists as boolean or string', () => {
      const contentBoolean: PredictionContent = {
        predicted_severity: 'Major',
        comparison_to_known_ddi: {
          known_interaction_exists: true,
          alignment_with_knowledge: 'aligned',
          explanation: 'Test',
        },
        historical_cases_analysis: {
          cases_reviewed: '50',
          risk_assessment: 'increased_risk',
          confidence: 'high',
          reasoning: 'Test',
        },
        clinical_concern_assessment: {
          should_be_concerned: true,
          concern_level: 'high',
          primary_reason: 'severity_level',
          recommendations: [],
        },
        summary: 'Test',
      };

      const contentString: PredictionContent = {
        ...contentBoolean,
        comparison_to_known_ddi: {
          ...contentBoolean.comparison_to_known_ddi,
          known_interaction_exists: 'yes',
        },
      };

      expect(contentBoolean.comparison_to_known_ddi.known_interaction_exists).toBe(true);
      expect(contentString.comparison_to_known_ddi.known_interaction_exists).toBe('yes');
    });

    it('should accept all alignment_with_knowledge enum values', () => {
      const alignments = ['aligned', 'contradicted', 'insufficient_data'];

      alignments.forEach((alignment) => {
        const content: PredictionContent = {
          predicted_severity: 'Major',
          comparison_to_known_ddi: {
            known_interaction_exists: true,
            alignment_with_knowledge: alignment,
            explanation: 'Test',
          },
          historical_cases_analysis: {
            cases_reviewed: '50',
            risk_assessment: 'increased_risk',
            confidence: 'high',
            reasoning: 'Test',
          },
          clinical_concern_assessment: {
            should_be_concerned: true,
            concern_level: 'high',
            primary_reason: 'severity_level',
            recommendations: [],
          },
          summary: 'Test',
        };

        expect(content.comparison_to_known_ddi.alignment_with_knowledge).toBe(alignment);
      });
    });

    it('should accept all risk_assessment enum values', () => {
      const riskAssessments = [
        'increased_risk',
        'decreased_risk',
        'no_significant_change',
        'insufficient_data',
      ];

      riskAssessments.forEach((risk) => {
        const content: PredictionContent = {
          predicted_severity: 'Major',
          comparison_to_known_ddi: {
            known_interaction_exists: true,
            alignment_with_knowledge: 'aligned',
            explanation: 'Test',
          },
          historical_cases_analysis: {
            cases_reviewed: '50',
            risk_assessment: risk,
            confidence: 'high',
            reasoning: 'Test',
          },
          clinical_concern_assessment: {
            should_be_concerned: true,
            concern_level: 'high',
            primary_reason: 'severity_level',
            recommendations: [],
          },
          summary: 'Test',
        };

        expect(content.historical_cases_analysis.risk_assessment).toBe(risk);
      });
    });

    it('should accept all confidence level values', () => {
      const confidenceLevels = ['high', 'medium', 'low'];

      confidenceLevels.forEach((confidence) => {
        const content: PredictionContent = {
          predicted_severity: 'Major',
          comparison_to_known_ddi: {
            known_interaction_exists: true,
            alignment_with_knowledge: 'aligned',
            explanation: 'Test',
          },
          historical_cases_analysis: {
            cases_reviewed: '50',
            risk_assessment: 'increased_risk',
            confidence: confidence,
            reasoning: 'Test',
          },
          clinical_concern_assessment: {
            should_be_concerned: true,
            concern_level: 'high',
            primary_reason: 'severity_level',
            recommendations: [],
          },
          summary: 'Test',
        };

        expect(content.historical_cases_analysis.confidence).toBe(confidence);
      });
    });

    it('should accept all concern_level values', () => {
      const concernLevels = ['high', 'medium', 'low'];

      concernLevels.forEach((level) => {
        const content: PredictionContent = {
          predicted_severity: 'Major',
          comparison_to_known_ddi: {
            known_interaction_exists: true,
            alignment_with_knowledge: 'aligned',
            explanation: 'Test',
          },
          historical_cases_analysis: {
            cases_reviewed: '50',
            risk_assessment: 'increased_risk',
            confidence: 'high',
            reasoning: 'Test',
          },
          clinical_concern_assessment: {
            should_be_concerned: true,
            concern_level: level,
            primary_reason: 'severity_level',
            recommendations: [],
          },
          summary: 'Test',
        };

        expect(content.clinical_concern_assessment.concern_level).toBe(level);
      });
    });

    it('should accept all primary_reason values', () => {
      const primaryReasons = [
        'historical_cases_evidence',
        'severity_level',
        'patient_factors',
      ];

      primaryReasons.forEach((reason) => {
        const content: PredictionContent = {
          predicted_severity: 'Major',
          comparison_to_known_ddi: {
            known_interaction_exists: true,
            alignment_with_knowledge: 'aligned',
            explanation: 'Test',
          },
          historical_cases_analysis: {
            cases_reviewed: '50',
            risk_assessment: 'increased_risk',
            confidence: 'high',
            reasoning: 'Test',
          },
          clinical_concern_assessment: {
            should_be_concerned: true,
            concern_level: 'high',
            primary_reason: reason,
            recommendations: [],
          },
          summary: 'Test',
        };

        expect(content.clinical_concern_assessment.primary_reason).toBe(reason);
      });
    });

    it('should accept empty and populated recommendations arrays', () => {
      const emptyRecs: PredictionContent = {
        predicted_severity: 'Minor',
        comparison_to_known_ddi: {
          known_interaction_exists: false,
          alignment_with_knowledge: 'aligned',
          explanation: 'Test',
        },
        historical_cases_analysis: {
          cases_reviewed: '10',
          risk_assessment: 'no_significant_change',
          confidence: 'low',
          reasoning: 'Test',
        },
        clinical_concern_assessment: {
          should_be_concerned: false,
          concern_level: 'low',
          primary_reason: 'patient_factors',
          recommendations: [],
        },
        summary: 'Test',
      };

      const populatedRecs: PredictionContent = {
        ...emptyRecs,
        clinical_concern_assessment: {
          ...emptyRecs.clinical_concern_assessment,
          recommendations: ['Monitor', 'Follow-up', 'Adjust dosage'],
        },
      };

      expect(emptyRecs.clinical_concern_assessment.recommendations).toHaveLength(0);
      expect(populatedRecs.clinical_concern_assessment.recommendations).toHaveLength(3);
    });
  });

  describe('AlertResult Type', () => {
    it('should accept valid AlertResult with all required fields', () => {
      const validAlert: AlertResult = {
        drug1: 'Aspirin',
        drug2: 'Warfarin',
        severity: 'major',
        reasoning: 'Test reasoning',
        content: {
          predicted_severity: 'Major',
          comparison_to_known_ddi: {
            known_interaction_exists: true,
            alignment_with_knowledge: 'aligned',
            explanation: 'Test',
          },
          historical_cases_analysis: {
            cases_reviewed: '50',
            risk_assessment: 'increased_risk',
            confidence: 'high',
            reasoning: 'Test',
          },
          clinical_concern_assessment: {
            should_be_concerned: true,
            concern_level: 'high',
            primary_reason: 'severity_level',
            recommendations: [],
          },
          summary: 'Test',
        },
      };

      expect(validAlert).toBeDefined();
      expect(validAlert.drug1).toBe('Aspirin');
      expect(validAlert.drug2).toBe('Warfarin');
      expect(validAlert.severity).toBe('major');
    });

    it('should accept AlertResult with optional fields', () => {
      const alertWithOptionals: AlertResult = {
        drug1: 'Aspirin',
        drug2: 'Warfarin',
        severity: 'major',
        reasoning: 'Test',
        known_severity: 'moderate',
        model_path: 'model-v1.0',
        content: {
          predicted_severity: 'Major',
          comparison_to_known_ddi: {
            known_interaction_exists: true,
            alignment_with_knowledge: 'aligned',
            explanation: 'Test',
          },
          historical_cases_analysis: {
            cases_reviewed: '50',
            risk_assessment: 'increased_risk',
            confidence: 'high',
            reasoning: 'Test',
          },
          clinical_concern_assessment: {
            should_be_concerned: true,
            concern_level: 'high',
            primary_reason: 'severity_level',
            recommendations: [],
          },
          summary: 'Test',
        },
      };

      expect(alertWithOptionals.known_severity).toBe('moderate');
      expect(alertWithOptionals.model_path).toBe('model-v1.0');
    });

    it('should accept AlertResult without optional fields', () => {
      const alertWithoutOptionals: AlertResult = {
        drug1: 'Aspirin',
        drug2: 'Warfarin',
        severity: 'major',
        reasoning: 'Test',
        content: {
          predicted_severity: 'Major',
          comparison_to_known_ddi: {
            known_interaction_exists: true,
            alignment_with_knowledge: 'aligned',
            explanation: 'Test',
          },
          historical_cases_analysis: {
            cases_reviewed: '50',
            risk_assessment: 'increased_risk',
            confidence: 'high',
            reasoning: 'Test',
          },
          clinical_concern_assessment: {
            should_be_concerned: true,
            concern_level: 'high',
            primary_reason: 'severity_level',
            recommendations: [],
          },
          summary: 'Test',
        },
      };

      expect(alertWithoutOptionals.known_severity).toBeUndefined();
      expect(alertWithoutOptionals.model_path).toBeUndefined();
    });

    it('should accept AlertResult with enriched_context', () => {
      const alertWithEnriched: AlertResult = {
        drug1: 'Aspirin',
        drug2: 'Warfarin',
        severity: 'major',
        reasoning: 'Test',
        content: {
          predicted_severity: 'Major',
          comparison_to_known_ddi: {
            known_interaction_exists: true,
            alignment_with_knowledge: 'aligned',
            explanation: 'Test',
          },
          historical_cases_analysis: {
            cases_reviewed: '50',
            risk_assessment: 'increased_risk',
            confidence: 'high',
            reasoning: 'Test',
          },
          clinical_concern_assessment: {
            should_be_concerned: true,
            concern_level: 'high',
            primary_reason: 'severity_level',
            recommendations: [],
          },
          summary: 'Test',
        },
        enriched_context: {
          similar_cases: [{ id: 1, case: 'test' }],
          top_mechanisms: [{ mechanism: 'bleeding' }],
          representative_cases: [{ case_id: '123' }],
          severity_distribution: {
            known_severity_count: 45,
            total_cases: 50,
          },
        },
      };

      expect(alertWithEnriched.enriched_context).toBeDefined();
      expect(alertWithEnriched.enriched_context?.severity_distribution.known_severity_count).toBe(45);
      expect(alertWithEnriched.enriched_context?.severity_distribution.total_cases).toBe(50);
    });

    it('should properly nest PredictionContent in AlertResult', () => {
      const alert: AlertResult = {
        drug1: 'Drug A',
        drug2: 'Drug B',
        severity: 'minor',
        reasoning: 'Test',
        content: {
          predicted_severity: 'Minor',
          comparison_to_known_ddi: {
            known_interaction_exists: false,
            alignment_with_knowledge: 'insufficient_data',
            explanation: 'Not enough data',
          },
          historical_cases_analysis: {
            cases_reviewed: '5',
            risk_assessment: 'no_significant_change',
            confidence: 'low',
            reasoning: 'Limited cases',
          },
          clinical_concern_assessment: {
            should_be_concerned: false,
            concern_level: 'low',
            primary_reason: 'patient_factors',
            recommendations: ['Standard monitoring'],
          },
          summary: 'Low risk interaction',
        },
      };

      expect(alert.content.predicted_severity).toBe('Minor');
      expect(alert.content.summary).toBe('Low risk interaction');
      expect(alert.content.clinical_concern_assessment.recommendations).toContain('Standard monitoring');
    });
  });
});

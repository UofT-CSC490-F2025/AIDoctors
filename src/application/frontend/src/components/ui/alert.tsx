import React, { useMemo } from 'react';
import { AlertResult, RepresentativeCase } from '@/types/predict-types';
import { cn } from '@/utils/general';

const getSeverityStyle = (
  severity: 'Minor' | 'Moderate' | 'Major' | 'Unknown'
) => {
  switch (severity) {
    case 'Major':
      return { bg: 'bg-red-100', text: 'text-red-800' };
    case 'Moderate':
      return { bg: 'bg-yellow-100', text: 'text-yellow-800' };
    case 'Minor':
      return { bg: 'bg-green-100', text: 'text-green-800' };
    case 'Unknown':
    default:
      return { bg: 'bg-gray-100', text: 'text-gray-700' };
  }
};

type AlertProps = React.ComponentProps<'div'> & {
  info: AlertResult;
  isPreview?: boolean;
};

export function Alert({
  info,
  isPreview = false,
  className,
  ...props
}: AlertProps) {
  const {
    drug1,
    drug2,
    known_severity,
    model_path,
    enriched_context,
    completion,
  } = info;

  // Use useMemo to parse the JSON string completion only when it changes
  const predictionDetails = useMemo(() => {
    try {
      if (completion) {
        // Since the backend sometimes includes a non-JSON prefix (e.g., '{"severity": "Major"}'),
        // we assume the completion string here is the raw JSON that needs parsing.
        return JSON.parse(completion);
      }
    } catch (e) {
      console.error('Failed to parse completion JSON:', e);
    }
    return {};
  }, [completion]);

  const {
    predicted_severity = info.severity || 'Unknown',
    comparison_to_known_ddi,
    historical_cases_analysis,
    clinical_concern_assessment,
    summary,
  } = predictionDetails;

  const severityStyle = getSeverityStyle(predicted_severity);

  // RAG/Enrichment data helper variables
  const hasEnrichedContext =
    enriched_context && enriched_context.similar_cases_count > 0;
  const topMechanisms = enriched_context?.top_mechanisms || [];
  const repCases: RepresentativeCase[] = enriched_context?.representative_cases || [];

  return (
    <div
      className={cn(
        'rounded-xl border border-gray-200 bg-white p-6 shadow-2xl space-y-6 max-w-7xl mx-auto font-sans',
        className
      )}
      {...props}
    >
      {/* 1. Header and Severity Badges */}
      <div className="flex flex-wrap items-start justify-between gap-4 border-b pb-4">
        <div className="space-y-1">
          <p className="text-xs font-bold uppercase text-gray-500">DDI ALERT</p>
          <h1 className="text-2xl font-extrabold text-gray-900 leading-tight">
            {drug1} + {drug2}
          </h1>
          {model_path ? (
            <p className="text-xs text-gray-500">
              Model: <span className="font-mono">{model_path}</span>
            </p>
          ) : null}
        </div>
        <div className="flex flex-wrap gap-2 text-xs font-semibold">
          {known_severity ? (
            <span className="rounded-full bg-gray-100 px-4 py-1.5 text-gray-700 border border-gray-300">
              Known: {known_severity}
            </span>
          ) : null}
          <span
            className={cn(
              'rounded-full px-4 py-1.5 border',
              severityStyle.bg,
              severityStyle.text,
              'border-current'
            )}
          >
            Predicted: {predicted_severity}
          </span>
        </div>
      </div>

      {/* 2. Model Summary */}
      <div className="space-y-2">
        <h2 className="text-lg font-bold text-gray-900 border-b border-gray-100 pb-1">
          Clinical Summary
        </h2>
        <p className="text-gray-700 text-base italic leading-relaxed">
          {summary || 'No brief summary available from the model output.'}
        </p>
      </div>

      {/* 3. Core Analysis Grids */}
      <div
        className={cn(
          'grid grid-cols-1 gap-4 text-sm',
          !isPreview && 'lg:grid-cols-3'
        )}
      >
        {/* Card 1: Known DDI & Enrichment Context */}
        <div className="space-y-3 rounded-xl border border-blue-100 bg-blue-50 p-4 shadow-inner">
          <h3 className="text-xs font-semibold uppercase text-blue-600">
            Knowledge & Context
          </h3>
          <p className="font-extrabold text-lg text-gray-900">
            {known_severity && known_severity !== 'Unknown'
              ? 'Known Interaction Exists'
              : 'No Known Interaction Found'}
          </p>
          <div className="space-y-2 text-gray-700">
            <p className="font-medium">
              Static Severity:{' '}
              <span className="capitalize font-semibold">
                {enriched_context?.static_severity || 'Unknown'}
              </span>
            </p>
            <p className="text-sm">{comparison_to_known_ddi?.explanation}</p>

            {/* Enrichment Details */}
            {hasEnrichedContext && (
              <div className="pt-2 border-t border-blue-200 mt-2 space-y-1">
                <p className="text-xs font-bold uppercase text-gray-600">
                  Database Enrichment
                </p>
                <p>
                  Cases Found:{' '}
                  <span className="font-bold">
                    {enriched_context.similar_cases_count}
                  </span>
                </p>
                {topMechanisms.length > 0 && (
                  <p className="text-sm">
                    Top Mechanisms:{' '}
                    <span className="font-mono">
                      {topMechanisms.join(', ')}
                    </span>
                  </p>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Card 2: Historical Cases Analysis */}
        <div className="space-y-3 rounded-xl border border-purple-100 bg-purple-50 p-4 shadow-inner">
          <h3 className="text-xs font-semibold uppercase text-purple-600">
            Historical Cases Analysis
          </h3>
          <p className="font-extrabold text-lg text-gray-900">
            {historical_cases_analysis?.risk_assessment.replace(/_/g, ' ')}
          </p>
          <div className="space-y-2 text-gray-700">
            <p className="font-medium">
              Reviewed:{' '}
              <span className="font-semibold">
                {historical_cases_analysis?.cases_reviewed} cases
              </span>
            </p>
            <p className="font-medium">
              Confidence:{' '}
              <span className="capitalize font-semibold">
                {historical_cases_analysis?.confidence}
              </span>
            </p>
            <p className="text-sm">{historical_cases_analysis?.reasoning}</p>
          </div>
        </div>

        {/* Card 3: Clinical Concern & Recommendations */}
        <div className="space-y-3 rounded-xl border border-green-100 bg-green-50 p-4 shadow-inner">
          <h3 className="text-xs font-semibold uppercase text-green-600">
            Clinical Assessment
          </h3>
          <p className="font-extrabold text-lg text-gray-900">
            {clinical_concern_assessment?.should_be_concerned
              ? `Concern Level: ${clinical_concern_assessment?.concern_level.toUpperCase()}`
              : 'Low Clinical Concern'}
          </p>
          <div className="space-y-2 text-gray-700">
            <p className="font-medium">
              Primary Reason:{' '}
              <span className="capitalize font-semibold">
                {clinical_concern_assessment?.primary_reason.replace(/_/g, ' ')}
              </span>
            </p>
            <h4 className="font-bold pt-1 text-gray-800">Recommendations:</h4>
            <ul className="list-disc space-y-1 pl-5 text-gray-700">
              {clinical_concern_assessment?.recommendations?.length > 0 ? (
                clinical_concern_assessment.recommendations.map(
                  (recommendation: any, idx: number) => (
                    <li key={idx} className="text-sm">
                      {recommendation}
                    </li>
                  )
                )
              ) : (
                <li className="text-sm italic">
                  No specific recommendations provided.
                </li>
              )}
            </ul>
          </div>
        </div>
      </div>

      {/* 4. Representative Cases (New Section) */}
      {repCases.length > 0 && (
        <div className="space-y-2 pt-4">
          <h2 className="text-lg font-bold text-gray-900 border-b border-gray-100 pb-1">
            Representative Historical Cases
          </h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
            {repCases.map((caseInfo: RepresentativeCase, idx: number) => (
              <div
                key={caseInfo.patient_uuid || idx}
                className="rounded-lg border border-orange-200 bg-orange-50 p-3 text-xs shadow-sm"
              >
                <p className="font-bold text-orange-800">Case #{idx + 1}</p>
                <p>
                  Similarity Score:{' '}
                  <span className="font-semibold">
                    {caseInfo.similarity_score?.toFixed(2) || 'N/A'}
                  </span>
                </p>
                <p>
                  Mechanism:{' '}
                  <span className="font-medium">
                    {caseInfo.mechanism?.substring(0, 30)}...
                  </span>
                </p>
                <p>
                  Age/Sex: {caseInfo.age}/{caseInfo.sex}
                </p>
                <p>Confidence: {caseInfo.confidence.toFixed(2)}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

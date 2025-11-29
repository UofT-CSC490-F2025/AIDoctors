import * as React from 'react';
import { AlertResult } from '@/types/predict-types';
import { cn } from '@/utils/general';

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
  const { drug1, drug2, known_severity, model_path, completion } = info;
  const {
    predicted_severity = 'Unknown',
    comparison_to_known_ddi,
    historical_cases_analysis,
    clinical_concern_assessment,
    summary,
  } = completion;

  return (
    <div
      className={cn(
        'rounded-xl border border-gray-200 bg-white p-4 shadow-sm space-y-4',
        className
      )}
      {...props}
    >
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="space-y-1">
          <p className="text-xs font-semibold uppercase text-orange-600">
            Alert
          </p>
          <p className="text-base font-semibold text-gray-900">
            {drug1} + {drug2}
          </p>
          {model_path ? (
            <p className="text-xs text-gray-500">Model: {model_path}</p>
          ) : null}
        </div>
        <div className="flex flex-wrap gap-2 text-xs font-medium">
          {known_severity ? (
            <span className="rounded-full bg-gray-100 px-3 py-1 text-gray-700">
              Known: {known_severity}
            </span>
          ) : null}
          <span className="rounded-full bg-orange-100 px-3 py-1 text-orange-800">
            Predicted: {predicted_severity}
          </span>
        </div>
      </div>

      <div className="space-y-1 text-sm">
        <p className="font-semibold text-gray-900">Summary</p>
        <p className="text-gray-700">{summary}</p>
      </div>

      <div
        className={
          'grid grid-cols-1 gap-3 text-sm' +
          (isPreview ? '' : ' md:grid-cols-3')
        }
      >
        <div className="space-y-1 rounded-lg border border-gray-100 bg-gray-50 p-3">
          <p className="text-xs font-semibold uppercase text-gray-500">
            Known DDI
          </p>
          <p className="font-medium text-gray-900">
            {comparison_to_known_ddi?.known_interaction_exists
              ? 'Known interaction'
              : 'No known interaction'}
          </p>
          <p className="text-gray-700">
            Alignment: {comparison_to_known_ddi?.alignment_with_knowledge}
          </p>
          <p className="text-gray-700">{comparison_to_known_ddi?.explanation}</p>
        </div>

        <div className="space-y-1 rounded-lg border border-gray-100 bg-gray-50 p-3">
          <p className="text-xs font-semibold uppercase text-gray-500">
            Historical cases
          </p>
          <p className="text-medium text-gray-900">
            {historical_cases_analysis?.cases_reviewed} cases ·{' '}
            {historical_cases_analysis?.risk_assessment}
          </p>
          <p className="text-gray-700">
            Confidence: {historical_cases_analysis?.confidence}
          </p>
          <p className="text-gray-700">{historical_cases_analysis?.reasoning}</p>
        </div>

        <div className="space-y-1 rounded-lg border border-gray-100 bg-gray-50 p-3">
          <p className="text-xs font-semibold uppercase text-gray-500">
            Clinical concern
          </p>
          <p className="font-medium text-gray-900">
            {clinical_concern_assessment?.should_be_concerned
              ? 'Concern present'
              : 'Low concern'}{' '}
            · {clinical_concern_assessment?.concern_level}
          </p>
          <p className="text-gray-700">
            Reason: {clinical_concern_assessment?.primary_reason}
          </p>
          <ul className="list-disc space-y-1 pl-5 text-gray-700">
            {clinical_concern_assessment?.recommendations.map(
              (recommendation, idx) => (
                <li key={idx}>{recommendation}</li>
              )
            )}
          </ul>
        </div>
      </div>
    </div>
  );
}

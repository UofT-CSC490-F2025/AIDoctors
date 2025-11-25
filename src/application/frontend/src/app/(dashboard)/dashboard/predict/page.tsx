'use client';
import { useEffect, useRef, useState } from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { AlertResult } from '@/types/predict-types';
import { Alert } from '@/components/ui/alert';
import { PredictionForm } from '@/components/forms/prediction-form';

export default function PredictPage() {
  const [results, setResults] = useState<AlertResult | null>(null);

  const alertsRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (results) {
      alertsRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [results]);

  return (
    <section className="flex-1 p-4 lg:p-8 space-y-8">
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div>
          <p className="text-xs font-semibold text-orange-600 uppercase tracking-wide">
            Predict
          </p>
          <h1 className="text-2xl lg:text-3xl font-semibold text-gray-900 mt-2">
            Compare two medications for DDI risk
          </h1>
          <p className="text-sm text-gray-600 mt-2 max-w-2xl">
            Submit the patient context plus a current and a new medication. The
            model blends DDI tables with similar-patient outcomes to rank risks.
          </p>
        </div>
      </div>

      <div className="flex flex-col gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Patient & medication details</CardTitle>
            <CardDescription>
              All fields help the model find similar cohorts and weigh severity.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <PredictionForm setResults={setResults} />
          </CardContent>
        </Card>

        <Card className="h-fit">
          <CardHeader>
            <CardTitle>Alerts</CardTitle>
            <CardDescription>
              Structured output from the prediction service.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3" ref={alertsRef}>
            {results ? (
              <Alert info={results} />
            ) : (
              <div className="rounded-xl border border-dashed border-gray-200 bg-gray-50 px-4 py-6 text-sm text-gray-600">
                Predictions will appear here.
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </section>
  );
}

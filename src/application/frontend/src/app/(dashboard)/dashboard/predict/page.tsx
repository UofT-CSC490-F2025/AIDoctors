'use client';
import { useEffect, useRef, useState } from 'react';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { AlertTriangle, Loader2, Calendar } from 'lucide-react';
import { Select } from '@/components/ui/select';
import { AlertResult, PredictFormValues } from '@/types/predict-types';
import { Alert } from '@/components/ui/alert';
import { getApiBaseUrl } from '@/utils/api';
import { useForm } from 'react-hook-form';
import { useUser } from '@/hooks/useUser';

export default function PredictPage() {
  const { register, handleSubmit, formState } = useForm<PredictFormValues>();
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<AlertResult[]>([]);
  const { setUser } = useUser();

  const alertsRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (results.length > 0) {
      alertsRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [results]);

  const errorRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (error) {
      errorRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [error]);

  const onSubmit = async (data: PredictFormValues) => {
    setError(null);
    setResults([]);

    try {
      const comorbiditiesArr = data.comorbidities
        .split(',')
        .map((c) => c.trim())
        .filter(Boolean);

      const bodyData = {
        Age: Number(data.age),
        Sex: data.sex,
        drug1: data.drugCurrent,
        drug2: data.drugNew,
        Comorbidities: comorbiditiesArr,
        overlap_start: data.overlapStart,
        overlap_stop: data.overlapStop,
      };
      const response = await fetch(`${getApiBaseUrl()}/predict`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(bodyData),
      });
      const responseData = await response.json();

      if (response.status === 401) {
        setError('Unauthenticated request. Please log in again.');
        setUser(null);
        return;
      }

      if (response.status >= 400 && response.status < 500) {
        setError(responseData.detail);
        return;
      }

      if (!response.ok) {
        setError('Request failed. Please try again later.');
        return;
      }

      setResults(responseData.alerts || []);
    } catch (error) {
      console.error('Prediction error:', error);
      setError('An unexpected error occurred. Please try again later.');
    }
  };

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
            <form className="grid gap-4" onSubmit={handleSubmit(onSubmit)}>
              <div className="grid sm:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="age" className="mb-2">
                    Age
                  </Label>
                  <Input
                    id="age"
                    type="number"
                    placeholder="65"
                    {...register('age', { min: 0 })}
                  />
                </div>
                <div>
                  <Label htmlFor="sex" className="mb-2">
                    Sex
                  </Label>
                  <Select
                    id="sex"
                    className="w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 shadow-sm focus:border-orange-500 focus:outline-none focus:ring-2 focus:ring-orange-500"
                    defaultValue=""
                    {...register('sex')}
                  >
                    <option value="">Select...</option>
                    <option value="M">Male</option>
                    <option value="F">Female</option>
                  </Select>
                </div>
              </div>

              <div className="grid sm:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="drugCurrent" className="mb-2">
                    Current medication<span className="text-red-500">*</span>
                  </Label>
                  <Input
                    id="drugCurrent"
                    placeholder="Warfarin"
                    {...register('drugCurrent', { required: true })}
                  />
                </div>
                <div>
                  <Label htmlFor="drugNew" className="mb-2">
                    New medication being considered
                    <span className="text-red-500">*</span>
                  </Label>
                  <Input
                    id="drugNew"
                    placeholder="Aspirin"
                    {...register('drugNew', { required: true })}
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="comorbidities" className="mb-2">
                  Comorbidities
                </Label>
                <Textarea
                  id="comorbidities"
                  placeholder="Hypertension, Diabetes"
                  {...register('comorbidities')}
                />
                <p className="text-xs text-gray-500 mt-1">
                  Separate multiple entries with commas.
                </p>
              </div>

              <div className="grid sm:grid-cols-2 gap-4">
                <div>
                  <Label
                    htmlFor="overlapStart"
                    className="mb-2 flex items-center gap-2 text-sm"
                  >
                    <Calendar className="h-4 w-4 text-gray-500" />
                    Overlap start
                  </Label>
                  <Input
                    id="overlapStart"
                    type="date"
                    {...register('overlapStart')}
                  />
                </div>
                <div>
                  <Label
                    htmlFor="overlapStop"
                    className="mb-2 flex items-center gap-2 text-sm"
                  >
                    <Calendar className="h-4 w-4 text-gray-500" />
                    Overlap stop
                  </Label>
                  <Input
                    id="overlapStop"
                    type="date"
                    {...register('overlapStop')}
                  />
                </div>
              </div>

              <Button
                type="submit"
                disabled={formState.isSubmitting}
                className="rounded-full w-full sm:w-auto"
              >
                {formState.isSubmitting ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Generating alerts...
                  </>
                ) : (
                  'Predict'
                )}
              </Button>
            </form>
            {error ? (
              <div
                ref={errorRef}
                className="mt-4 rounded-xl border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700 flex items-start gap-2"
              >
                <AlertTriangle className="h-4 w-4 mt-0.5" />
                <span>{error}</span>
              </div>
            ) : null}
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
            {results.length === 0 ? (
              <div className="rounded-xl border border-dashed border-gray-200 bg-gray-50 px-4 py-6 text-sm text-gray-600">
                Predictions will appear here.
              </div>
            ) : (
              results.map((alert, index) => <Alert key={index} info={alert} />)
            )}
          </CardContent>
        </Card>
      </div>
    </section>
  );
}

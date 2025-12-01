'use client';
import { useEffect, useRef, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { AlertTriangle, Loader2, Calendar } from 'lucide-react';
import { Select } from '@/components/ui/select';
import { getApiBaseUrl } from '@/utils/api';
import { useForm } from 'react-hook-form';
import { useUser } from '@/hooks/useUser';
import { AlertResult } from '@/types/predict-types';

type PredictFormValues = {
  age: number;
  sex: 'M' | 'F' | '';
  drugCurrent: string;
  drugNew: string;
  comorbidities: string;
  overlapStart: string;
  overlapStop: string;
};

type PredictionFormProps = {
  setResults: (results: AlertResult | null) => void;
};

export function PredictionForm({ setResults }: PredictionFormProps) {
  const { register, handleSubmit, formState } = useForm<PredictFormValues>();
  const [error, setError] = useState<string | null>(null);
  const { setUser } = useUser();

  const errorRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (error) {
      errorRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [error]);

  const onSubmit = async (data: PredictFormValues) => {
    setError(null);
    setResults(null);

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
        credentials: 'include', // Send cookies
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(bodyData),
      });
      const responseData = await response.json();

      console.log(responseData);

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

      setResults(responseData);
    } catch (error) {
      console.error('Prediction error:', error);
      setError('An unexpected error occurred. Please try again later.');
    }
  };

  return (
    <>
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
    </>
  );
}

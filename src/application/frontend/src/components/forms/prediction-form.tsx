'use client';
import AsyncSelect from 'react-select/async';
import { useEffect, useRef, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { AlertTriangle, Loader2 } from 'lucide-react';
import { Select } from '@/components/ui/select';
import { getApiBaseUrl } from '@/utils/api';
import { Controller, useForm } from 'react-hook-form';
import { useUser } from '@/hooks/useUser';
import { AlertResult } from '@/types/predict-types';
import { makeDebouncedLoader } from '@/utils/general';

const fetchDrugs = async (input: string) => {
  if (!input) return [];

  const response = await fetch(
    `${getApiBaseUrl()}/predict/matching_drugs?name=${encodeURIComponent(input)}`,
    {
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
    }
  );
  if (!response.ok) return [];
  const data = await response.json();
  return data.map((d: string) => ({ label: d, value: d }));
};
const loadDrugOptions = makeDebouncedLoader(fetchDrugs, 300);

const fetchComorbidities = async (input: string) => {
  if (!input) return [];

  const response = await fetch(
    `${getApiBaseUrl()}/predict/matching_comorbidities?name=${encodeURIComponent(input)}`,
    {
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
    }
  );
  if (!response.ok) return [];
  const data = await response.json();
  return data.map((d: string) => ({ label: d, value: d }));
};
const loadComorbidityOptions = makeDebouncedLoader(fetchComorbidities, 300);

type PredictFormValues = {
  age: number;
  sex: 'M' | 'F' | '';
  drugCurrent: string;
  drugNew: string;
  comorbidities: string[];
};

type PredictionFormProps = {
  setResults: (results: AlertResult | null) => void;
};

export function PredictionForm({ setResults }: PredictionFormProps) {
  const {
    control,
    register,
    handleSubmit,
    formState: { isValid, isSubmitting },
  } = useForm<PredictFormValues>({
    mode: 'onChange',
  });
  const [error, setError] = useState<string | null>(null);
  const { setUser } = useUser();

  const baseUrl = getApiBaseUrl();

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
      const bodyData = {
        Age: Number(data.age),
        Sex: data.sex,
        drug1: data.drugCurrent,
        drug2: data.drugNew,
        Comorbidities: data.comorbidities,
      };

      const response = await fetch(`${baseUrl}/predict`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
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

      setResults(responseData);
    } catch {
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
              min={0}
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
              Current medication
              <span className="text-red-500">*</span>
            </Label>
            <Controller
              name="drugCurrent"
              control={control}
              rules={{ required: true }}
              render={({ field }) => (
                <AsyncSelect
                  inputId="drugCurrent"
                  cacheOptions
                  defaultOptions={false}
                  loadOptions={loadDrugOptions}
                  onChange={(opt) => field.onChange(opt?.value ?? '')}
                  value={
                    field.value
                      ? { label: field.value, value: field.value }
                      : null
                  }
                  placeholder="Search drug..."
                />
              )}
            />
          </div>

          <div>
            <Label htmlFor="drugNew" className="mb-2">
              New medication being considered
              <span className="text-red-500">*</span>
            </Label>
            <Controller
              name="drugNew"
              control={control}
              rules={{ required: true }}
              render={({ field }) => (
                <AsyncSelect
                  inputId="drugNew"
                  cacheOptions
                  defaultOptions={false}
                  loadOptions={loadDrugOptions}
                  onChange={(opt) => field.onChange(opt?.value ?? '')}
                  value={
                    field.value
                      ? { label: field.value, value: field.value }
                      : null
                  }
                  placeholder="Search drug..."
                />
              )}
            />
          </div>
        </div>

        <div>
          <Label htmlFor="comorbidities" className="mb-2">
            Comorbidities
          </Label>
          <Controller
            name="comorbidities"
            control={control}
            render={({ field }) => (
              <AsyncSelect
                inputId="comorbidities"
                isMulti
                cacheOptions
                defaultOptions={false}
                loadOptions={loadComorbidityOptions}
                placeholder="Search comorbidities..."
                value={
                  Array.isArray(field.value)
                    ? field.value.map((v: string) => ({ label: v, value: v }))
                    : []
                }
                onChange={(opts) => {
                  const values = Array.isArray(opts)
                    ? opts.map((o) => o.value)
                    : [];
                  field.onChange(values);
                }}
              />
            )}
          />
        </div>

        <Button
          type="submit"
          disabled={!isValid || isSubmitting}
          className="rounded-full w-full sm:w-auto"
        >
          {isSubmitting ? (
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

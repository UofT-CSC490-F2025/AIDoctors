import { Button } from '@/components/ui/button';
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { ArrowRight, Database, ShieldCheck, Sparkles } from 'lucide-react';
import Link from 'next/link';

const steps = [
  {
    title: 'Collect context',
    description:
      'Age, sex, comorbidities, and current medications are captured for the visit.',
    icon: Database,
  },
  {
    title: 'Blend evidence',
    description:
      'Combine curated DDI tables with outcomes from similar patients to re-rank severity.',
    icon: Sparkles,
  },
  {
    title: 'Deliver the top-k alerts',
    description:
      'Return only the most critical, explainable warnings so clinicians can act quickly.',
    icon: ShieldCheck,
  },
];

export default function DashboardPage() {
  return (
    <section className="flex-1 p-4 lg:p-8 space-y-8">
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div>
          <p className="text-xs font-semibold text-orange-600 uppercase tracking-wide">
            Dashboard
          </p>
          <h1 className="text-2xl lg:text-3xl font-semibold text-gray-900 mt-2">
            Patient-aware drug interaction alerts
          </h1>
          <p className="text-sm text-gray-600 mt-2 max-w-2xl">
            Enable safer prescribing by surfacing patient-specific drug
            interaction alerts that prioritize the most critical, explainable
            risks for clinicians to review quickly.
          </p>
        </div>
        <Button asChild className="rounded-full px-5">
          <Link href="/dashboard/predict">
            Run a prediction
            <ArrowRight className="ml-2 h-4 w-4" />
          </Link>
        </Button>
      </div>

      <div className="grid md:grid-cols-3 gap-4">
        {steps.map((step) => (
          <Card key={step.title}>
            <CardHeader className="flex flex-row items-start gap-3">
              <div className="p-2 rounded-xl bg-orange-50 text-orange-600">
                <step.icon className="h-5 w-5" />
              </div>
              <div>
                <CardTitle>{step.title}</CardTitle>
                <CardDescription className="mt-1">
                  {step.description}
                </CardDescription>
              </div>
            </CardHeader>
          </Card>
        ))}
      </div>
    </section>
  );
}

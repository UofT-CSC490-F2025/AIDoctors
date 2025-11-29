import Link from 'next/link';
import { ArrowRight, ShieldCheck, Activity, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Alert } from '@/components/ui/alert';
import { DUMMY_ALERTS } from '@/utils/constants';
import { Header } from '@/components/layout/header';

const featureCards = [
  {
    title: 'Patient-aware alerts',
    description:
      'Age, sex, comorbidities, and current meds all inform the risk scoring instead of static pairwise tables.',
    icon: ShieldCheck,
  },
  {
    title: 'Learn from real outcomes',
    description:
      'Historical cases from similar patients boost signals when the DDI table alone underestimates severity.',
    icon: Activity,
  },
  {
    title: 'Explainable outputs',
    description:
      'Each alert ships with the evidence driving the score so clinicians understand why a recommendation matters.',
    icon: Sparkles,
  },
];

export default function HomePage() {
  return (
    <main className="bg-gradient-to-b from-orange-50 via-white to-white">
      <Header />
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 pointer-events-none bg-[radial-gradient(circle_at_20%_20%,rgba(255,159,64,0.12),transparent_35%),radial-gradient(circle_at_80%_0%,rgba(59,130,246,0.08),transparent_28%)]" />
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12 relative">
          <div className="grid gap-12 items-center">
            <div className="space-y-6 py-12">
              <p className="inline-flex items-center px-3 py-1 rounded-full bg-white/80 border border-orange-200 text-xs font-semibold text-orange-700 shadow-sm">
                Clinical safety, ML-first
              </p>
              <h1 className="text-4xl sm:text-5xl font-semibold text-gray-900 leading-tight max-w-xl">
                Catch drug interactions
                <span className="text-orange-600">
                  {' '}
                  before they become harmful
                </span>
              </h1>
              <p className="text-lg text-gray-600 max-w-xl">
                AI Doctors blends trusted DDI tables with outcomes from similar
                patients to surface the most severe alerts for every new
                prescription decision.
              </p>
              <div className="flex flex-wrap gap-4">
                <Button asChild size="lg" className="rounded-full px-6">
                  <Link href="/signup">
                    Get started
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
                <Button
                  asChild
                  variant="outline"
                  size="lg"
                  className="rounded-full px-6"
                >
                  <Link href="/login">Log in</Link>
                </Button>
              </div>
            </div>

            <Alert info={DUMMY_ALERTS[1]} className="shadow-xl" />
          </div>
        </div>
      </section>

      <section className="py-14 sm:py-16 bg-white border-t border-gray-100">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-3 gap-6">
            {featureCards.map((feature) => (
              <div
                key={feature.title}
                className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm"
              >
                <div className="inline-flex items-center justify-center rounded-xl bg-orange-50 text-orange-600 p-3 mb-4">
                  <feature.icon className="h-5 w-5" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900">
                  {feature.title}
                </h3>
                <p className="text-sm text-gray-600 mt-2">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-14 sm:py-16 bg-gray-50">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="rounded-3xl bg-white border border-gray-200 shadow-sm p-8 sm:p-10">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
              <div>
                <h2 className="text-2xl font-semibold text-gray-900">
                  Built for safer prescribing
                </h2>
                <p className="text-sm text-gray-600 mt-2 max-w-2xl">
                  Bring patient context and drug interaction knowledge together
                  so care teams can spot the most important risks before a
                  medication is added.
                </p>
              </div>
              <Button asChild size="lg" className="rounded-full px-6">
                <Link href="/dashboard">Go to dashboard</Link>
              </Button>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}

'use client';
import { Suspense, useEffect } from 'react';
import Link from 'next/link';
import { Brain } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useUser } from '@/hooks/useUser';
import { LoadingScreen } from '@/components/ui/loading-screen';
import { LoginForm } from '@/components/forms/login-form';

export default function LoginPage() {
  const router = useRouter();
  const { user, isLoading: userIsLoading } = useUser();

  useEffect(() => {
    if (user) {
      router.replace('/dashboard');
    }
  }, [user, userIsLoading, router]);

  if (user || userIsLoading) {
    return <LoadingScreen />;
  }

  return (
    <Suspense>
      <div className="min-h-[100dvh] flex flex-col justify-center py-12 px-4 sm:px-6 lg:px-8 bg-gray-50">
        <div className="sm:mx-auto sm:w-full sm:max-w-md">
          <div className="flex justify-center">
            <Link href="/">
              <Brain className="h-12 w-12 text-orange-500" />
            </Link>
          </div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Welcome back to AI Doctors
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Securely access patient-specific DDI insights.
          </p>
        </div>

        <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
          <LoginForm />
          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-gray-50 text-gray-500">
                  New to AI Doctors?
                </span>
              </div>
            </div>

            <div className="mt-6">
              <Link
                href="/signup"
                className="w-full flex justify-center py-2 px-4 border border-gray-300 rounded-full shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500"
              >
                Create an account
              </Link>
            </div>
          </div>
        </div>
      </div>
    </Suspense>
  );
}

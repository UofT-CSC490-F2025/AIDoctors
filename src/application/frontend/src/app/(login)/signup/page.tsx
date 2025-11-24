'use client';
import { Suspense, useEffect, useState } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Brain, Loader2 } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { SignUpFormValues } from '@/types/login-types';
import { getApiBaseUrl } from '@/utils/api';
import { useUser } from '@/hooks/useUser';
import { LoadingScreen } from '@/components/ui/loading-screen';

export default function SignUpPage() {
  const router = useRouter();
  const { register, handleSubmit, formState } = useForm<SignUpFormValues>();
  const [error, setError] = useState<string | null>(null);
  const { user, isLoading: userIsLoading } = useUser();

  useEffect(() => {
    if (user) {
      router.replace('/dashboard');
    }
  }, [user, userIsLoading, router]);

  const onSubmit = async (data: SignUpFormValues) => {
    setError(null);

    try {
      const bodyData = {
        first_name: data.firstName,
        last_name: data.lastName,
        username: data.username,
        email: data.email,
        password: data.password,
      };
      const response = await fetch(`${getApiBaseUrl()}/users/register`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(bodyData),
      });
      const responseData = await response.json();

      if (response.status >= 400 && response.status < 500) {
        setError(responseData.detail);
        return;
      }

      if (!response.ok) {
        setError('Request failed. Please try again later.');
        return;
      }

      router.push('/login');
    } catch (error) {
      console.error('Signup error:', error);
      setError('An unexpected error occurred. Please try again later.');
    }
  };

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
            Create your AI Doctors account
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Securely access patient-specific DDI insights.
          </p>
        </div>

        <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
          <form className="space-y-6" onSubmit={handleSubmit(onSubmit)}>
            <div>
              <Label
                htmlFor="firstName"
                className="block text-sm font-medium text-gray-700"
              >
                First Name
              </Label>
              <div className="mt-1">
                <Input
                  id="firstName"
                  type="text"
                  autoComplete="given-name"
                  className="appearance-none rounded-full relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-orange-500 focus:border-orange-500 focus:z-10 sm:text-sm"
                  placeholder="Enter your first name"
                  {...register('firstName', { required: true })}
                />
              </div>
            </div>

            <div>
              <Label
                htmlFor="lastName"
                className="block text-sm font-medium text-gray-700"
              >
                Last Name
              </Label>
              <div className="mt-1">
                <Input
                  id="lastName"
                  type="text"
                  autoComplete="family-name"
                  className="appearance-none rounded-full relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-orange-500 focus:border-orange-500 focus:z-10 sm:text-sm"
                  placeholder="Enter your last name"
                  {...register('lastName', { required: true })}
                />
              </div>
            </div>

            <div>
              <Label
                htmlFor="username"
                className="block text-sm font-medium text-gray-700"
              >
                Username
              </Label>
              <div className="mt-1">
                <Input
                  id="username"
                  type="text"
                  autoComplete="username"
                  className="appearance-none rounded-full relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-orange-500 focus:border-orange-500 focus:z-10 sm:text-sm"
                  placeholder="Enter a username"
                  {...register('username', { required: true })}
                />
              </div>
            </div>

            <div>
              <Label
                htmlFor="email"
                className="block text-sm font-medium text-gray-700"
              >
                Email
              </Label>
              <div className="mt-1">
                <Input
                  id="email"
                  type="email"
                  autoComplete="email"
                  className="appearance-none rounded-full relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-orange-500 focus:border-orange-500 focus:z-10 sm:text-sm"
                  placeholder="Enter your email"
                  {...register('email', { required: true })}
                />
              </div>
            </div>

            <div>
              <Label
                htmlFor="password"
                className="block text-sm font-medium text-gray-700"
              >
                Password
              </Label>
              <div className="mt-1">
                <Input
                  id="password"
                  type="password"
                  autoComplete="new-password"
                  className="appearance-none rounded-full relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-orange-500 focus:border-orange-500 focus:z-10 sm:text-sm"
                  placeholder="Enter a password"
                  {...register('password', { required: true })}
                />
              </div>
            </div>

            {error && <div className="text-red-500 text-sm">{error}</div>}

            <div>
              <Button
                type="submit"
                className="w-full flex justify-center items-center py-2 px-4 border border-transparent rounded-full shadow-sm text-sm font-medium text-white bg-orange-600 hover:bg-orange-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500"
              >
                {formState.isSubmitting ? (
                  <>
                    <Loader2 className="animate-spin mr-2 h-4 w-4" />
                    Loading...
                  </>
                ) : (
                  'Sign up'
                )}
              </Button>
            </div>
          </form>

          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-gray-50 text-gray-500">
                  Already have an account?
                </span>
              </div>
            </div>

            <div className="mt-6">
              <Link
                href="/login"
                className="w-full flex justify-center py-2 px-4 border border-gray-300 rounded-full shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500"
              >
                Sign in to existing account
              </Link>
            </div>
          </div>
        </div>
      </div>
    </Suspense>
  );
}

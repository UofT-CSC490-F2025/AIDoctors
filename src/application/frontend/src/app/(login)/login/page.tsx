'use client';
import { Suspense, useEffect, useState } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Brain, Loader2 } from 'lucide-react';
import { useForm } from 'react-hook-form';
import { LoginFormValues } from '@/types/login-types';
import { getApiBaseUrl } from '@/utils/api';
import { useRouter } from 'next/navigation';
import { useUser } from '@/hooks/useUser';
import { User } from '@/types/user-types';
import { LoadingScreen } from '@/components/ui/loading-screen';

export default function LoginPage() {
  const router = useRouter();
  const { register, handleSubmit, formState } = useForm<LoginFormValues>();
  const [error, setError] = useState<string | null>(null);
  const { setUser, user, isLoading: userIsLoading } = useUser();

  useEffect(() => {
    if (user) {
      router.replace('/dashboard');
    }
  }, [user, userIsLoading, router]);

  const onSubmit = async (data: LoginFormValues) => {
    setError(null);

    try {
      const body = new URLSearchParams();
      body.append('username', data.username);
      body.append('password', data.password);

      const responseToken = await fetch(`${getApiBaseUrl()}/auth/token`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body,
      });

      if (responseToken.status === 401) {
        setError('Invalid username or password.');
        return;
      }

      if (!responseToken.ok) {
        setError('Request failed. Please try again later.');
        return;
      }

      const responseUser = await fetch(`${getApiBaseUrl()}/users/me`, {
        method: 'GET',
        credentials: 'include',
      });

      if (!responseUser.ok) {
        setUser(null);
        setError('Failed to fetch user data.');
        return;
      }

      const userData: User = await responseUser.json();
      setUser(userData);

      router.push('/dashboard');
    } catch (error) {
      console.error('Login error:', error);
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
            Welcome back to AI Doctors
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Securely access patient-specific DDI insights.
          </p>
        </div>

        <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
          <form className="space-y-6" onSubmit={handleSubmit(onSubmit)}>
            <div>
              <Label
                htmlFor="email"
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
                  placeholder="Enter your username"
                  {...register('username', { required: true })}
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
                  autoComplete="current-password"
                  className="appearance-none rounded-full relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-orange-500 focus:border-orange-500 focus:z-10 sm:text-sm"
                  placeholder="Enter your password"
                  {...register('password', { required: true })}
                />
              </div>
            </div>

            {error && <div className="text-red-500 text-sm">{error}</div>}

            <div>
              <Button
                type="submit"
                className="w-full flex justify-center items-center py-2 px-4 border border-transparent rounded-full shadow-sm text-sm font-medium text-white bg-orange-600 hover:bg-orange-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500"
                disabled={formState.isSubmitting}
              >
                {formState.isSubmitting ? (
                  <>
                    <Loader2 className="animate-spin mr-2 h-4 w-4" />
                    Loading...
                  </>
                ) : (
                  'Sign in'
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

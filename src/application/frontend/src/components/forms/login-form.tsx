'use client';
import { useUser } from '@/hooks/useUser';
import { User } from '@/types/user-types';
import { getApiBaseUrl } from '@/utils/api';
import { Loader2 } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { useRouter } from 'next/navigation';

type LoginFormValues = {
  username: string;
  password: string;
};

export function LoginForm() {
  const router = useRouter();
  const { register, handleSubmit, formState } = useForm<LoginFormValues>();
  const [error, setError] = useState<string | null>(null);
  const { setUser } = useUser();

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

  return (
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
  );
}

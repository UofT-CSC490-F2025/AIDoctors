'use client';
import { useForm } from 'react-hook-form';
import { getApiBaseUrl } from '@/utils/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { Loader2 } from 'lucide-react';

type SignUpFormValues = {
  firstName: string;
  lastName: string;
  username: string;
  email: string;
  password: string;
};

export function SignupForm() {
  const router = useRouter();
  const { register, handleSubmit, formState } = useForm<SignUpFormValues>();
  const [error, setError] = useState<string | null>(null);

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

  return (
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
  );
}

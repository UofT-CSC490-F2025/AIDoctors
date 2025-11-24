'use client';
import { useUser } from '@/hooks/useUser';
import { Brain } from 'lucide-react';
import { Button } from '@/components/ui/button';
import Link from 'next/link';

export function Header() {
  const { user } = useUser();

  return (
    <header className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6 flex items-center justify-between">
      <Link href="/" className="flex items-center space-x-2">
        <Brain className="h-9 w-9 text-orange-500" />
        <span className="text-lg font-semibold text-gray-900">AI Doctors</span>
      </Link>
      {user ? (
        <div className="flex items-center gap-3">
          <Button asChild className="rounded-full px-4">
            <Link href="/dashboard">Go to dashboard</Link>
          </Button>
          <div className="flex items-center gap-3 rounded-full bg-white border border-gray-200 px-3 py-1.5 shadow-sm">
            <div className="text-sm text-gray-800">
              {user.username || 'Account'}
            </div>
          </div>
        </div>
      ) : (
        <div className="flex items-center gap-3">
          <Button asChild variant="ghost" className="rounded-full px-4">
            <Link href="/login">Log in</Link>
          </Button>
          <Button asChild className="rounded-full px-4">
            <Link href="/signup">Sign up</Link>
          </Button>
        </div>
      )}
    </header>
  );
}

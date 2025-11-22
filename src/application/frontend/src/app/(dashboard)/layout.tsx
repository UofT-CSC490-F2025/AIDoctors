'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Brain } from 'lucide-react';
import { getApiBaseUrl } from '@/utils/api';
import { AuthRequired } from '@/components/auth/auth-required';
import { useUser } from '@/hooks/useUser';

const navLinks = [
  { href: '/dashboard', label: 'Overview' },
  { href: '/dashboard/predict', label: 'Predict' },
];

export default function Layout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { setUser } = useUser();

  const handleLogout = async () => {
    try {
      const response = await fetch(`${getApiBaseUrl()}/auth/logout`, {
        method: 'POST',
        credentials: 'include',
      });

      if (response.ok) {
        setUser(null);
      }
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  return (
    <AuthRequired>
      <section className="flex flex-col min-h-screen">
        <header className="border-b border-gray-200 bg-white/80 backdrop-blur">
          <div className="max-w-8xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex flex-wrap gap-3 justify-between items-center">
            <Link href="/" className="flex items-center space-x-2">
              <Brain className="h-6 w-6 text-orange-500" />
              <span className="text-xl font-semibold text-gray-900">
                AI Doctors
              </span>
            </Link>
            <div className="flex items-center gap-3">
              {navLinks.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`text-sm font-medium px-3 py-2 rounded-full transition ${
                    pathname === link.href
                      ? 'bg-orange-50 text-orange-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  {link.label}
                </Link>
              ))}
              <div className="ml-1">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  className="rounded-full"
                  onClick={handleLogout}
                >
                  Sign out
                </Button>
              </div>
            </div>
          </div>
        </header>
        {children}
      </section>
    </AuthRequired>
  );
}

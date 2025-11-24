import { useUser } from '@/hooks/useUser';
import { useRouter } from 'next/dist/client/components/navigation';
import { LoadingScreen } from '../ui/loading-screen';
import { useEffect } from 'react';

export function AuthRequired({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { user, isLoading } = useUser();

  useEffect(() => {
    if (!user && !isLoading) {
      router.replace('/login');
    }
  }, [user, isLoading, router]);

  if (!user || isLoading) {
    return <LoadingScreen />;
  }

  return <>{children}</>;
}

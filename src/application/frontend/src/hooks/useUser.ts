import { UserCtx } from '@/components/auth/user-context';
import { useContext } from 'react';

export function useUser() {
  const ctx = useContext(UserCtx);
  if (!ctx) throw new Error('useUser must be inside UserProvider');
  return ctx;
}

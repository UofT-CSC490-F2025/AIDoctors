'use client';
import { UserCtx } from '@/components/features/auth/user-context';
import { useContext } from 'react';

export function useUser() {
  const ctx = useContext(UserCtx);
  if (!ctx) throw new Error('useUser must be inside UserProvider');
  return ctx;
}

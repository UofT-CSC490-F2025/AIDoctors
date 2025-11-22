'use client';
import { User, UserContext } from '@/types/user-types';
import { getApiBaseUrl } from '@/utils/api';
import { createContext, useEffect, useState } from 'react';

export const UserCtx = createContext<UserContext | undefined>(undefined);

export function UserProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    async function fetchUser() {
      setIsLoading(true);

      try {
        const response = await fetch(`${getApiBaseUrl()}/users/me`, {
          method: 'GET',
          credentials: 'include',
        });

        if (!response.ok) {
          setUser(null);
          return;
        }

        const userData: User = await response.json();
        setUser(userData);
      } catch (error) {
        console.error('Error fetching user:', error);
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    }

    fetchUser();
  }, []);

  const value = { user, setUser, isLoading };

  return <UserCtx.Provider value={value}>{children}</UserCtx.Provider>;
}

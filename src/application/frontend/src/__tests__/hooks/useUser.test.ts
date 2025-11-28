import { renderHook } from '@testing-library/react';
import { useUser } from '../../hooks/useUser';
import { UserCtx } from '@/components/features/auth/user-context';
import React from 'react';

describe('useUser', () => {
  it('should return user context when inside UserProvider', () => {
    const mockUserContext = { id: '1', name: 'John Doe' };
    const wrapper = ({ children }: { children: React.ReactNode }) =>
      React.createElement(
        UserCtx.Provider,
        { value: mockUserContext },
        children
      );

    const { result } = renderHook(() => useUser(), { wrapper });
    expect(result.current).toEqual(mockUserContext);
  });

  it('should throw error when useUser is used outside UserProvider', () => {
    expect(() => renderHook(() => useUser())).toThrow(
      'useUser must be inside UserProvider'
    );
  });
});

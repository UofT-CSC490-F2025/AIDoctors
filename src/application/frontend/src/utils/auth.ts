/**
 * Get the access token from localStorage
 */
export function getAccessToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('access_token');
}

/**
 * Set the access token in localStorage
 */
export function setAccessToken(token: string): void {
  localStorage.setItem('access_token', token);
}

/**
 * Remove the access token from localStorage
 */
export function removeAccessToken(): void {
  localStorage.removeItem('access_token');
}

/**
 * Get headers with Authorization token if available
 */
export function getAuthHeaders(additionalHeaders?: HeadersInit): HeadersInit {
  const token = getAccessToken();
  const headers: HeadersInit = {
    ...additionalHeaders,
  };

  if (token) {
    (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
  }

  return headers;
}

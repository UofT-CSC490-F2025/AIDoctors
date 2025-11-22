const _DEFAULT_API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export function getApiBaseUrl() {
  return _DEFAULT_API_BASE.replace(/\/$/, '');
}

const _DEFAULT_API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export function getApiBaseUrl() {
  // In production (CloudFront), use relative /api path
  // In development, use the full API URL
  if (
    typeof window !== 'undefined' &&
    window.location.hostname.includes('cloudfront.net')
  ) {
    return '/api';
  }
  return _DEFAULT_API_BASE.replace(/\/$/, '');
}

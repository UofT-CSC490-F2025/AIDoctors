export function getApiBaseUrl() {
  // Use environment variable directly
  // Production: /api (relative path through CloudFront)
  // Development: http://localhost:8000/api
  const apiBaseUrl =
    process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api';
  return apiBaseUrl.replace(/\/$/, '');
}

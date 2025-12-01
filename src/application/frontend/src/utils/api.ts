const _DEFAULT_API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export function getApiBaseUrl() {
  // Production: Always use relative /api path (routed through CloudFront to ALB)
  // Development: Use full API URL (typically http://localhost:8000)
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;
    
    // Only use full API URL on localhost/127.0.0.1
    // All other domains (CloudFront, custom domains, etc.) use relative /api path
    const isLocalDevelopment =
      hostname.includes('localhost') || hostname.includes('127.0.0.1');
    
    if (!isLocalDevelopment) {
      return '/api';
    }
  }
  
  // Local development: use the configured API base URL
  return _DEFAULT_API_BASE.replace(/\/$/, '');
}

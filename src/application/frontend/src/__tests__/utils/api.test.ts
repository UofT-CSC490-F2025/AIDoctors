import {
  afterAll,
  beforeEach,
  describe,
  expect,
  it,
  jest,
} from '@jest/globals';

const modulePath = '@/utils/api';
const originalEnv = process.env;

// Tests for getApiBaseUrl function // again
describe('getApiBaseUrl', () => {
  beforeEach(() => {
    jest.resetModules();
    process.env = { ...originalEnv };
  });

  afterAll(() => {
    process.env = originalEnv;
  });

  it('returns the default base URL when env var is not set', async () => {
    delete process.env.NEXT_PUBLIC_API_BASE_URL;

    const { getApiBaseUrl } = await import(modulePath);

    expect(getApiBaseUrl()).toBe('http://localhost:8000');
  });

  it('uses the env base URL without altering it when no trailing slash exists', async () => {
    process.env.NEXT_PUBLIC_API_BASE_URL = 'https://api.example.com';

    const { getApiBaseUrl } = await import(modulePath);

    expect(getApiBaseUrl()).toBe('https://api.example.com');
  });

  it('trims a trailing slash from the env base URL', async () => {
    process.env.NEXT_PUBLIC_API_BASE_URL = 'https://api.example.com/';

    const { getApiBaseUrl } = await import(modulePath);

    expect(getApiBaseUrl()).toBe('https://api.example.com');
  });
});

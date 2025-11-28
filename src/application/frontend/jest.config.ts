import type { Config } from 'jest';
import nextJest from 'next/jest.js';

const createJestConfig = nextJest({
  // Provide the path to your Next.js app to load next.config.js and .env files in your test environment
  dir: './',
});

const config: Config = {
  // Indicates whether the coverage information should be collected while executing the test
  collectCoverage: true,

  // A list of reporter names that Jest uses when writing coverage reports
  coverageReporters: ['text', 'lcov', 'json-summary'],

  // The directory where Jest should output its coverage files
  coverageDirectory: './coverage',

  // An array of glob patterns indicating a set of files for which coverage information should be collected
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
    '!**/node_modules/**',
  ],

  // Indicates which provider should be used to instrument code for coverage
  coverageProvider: 'v8',

  // A map from regular expressions to module names or to arrays of module names that allow to stub out resources with a single module
  moduleNameMapper: {
    // Mapping for tsconfig.json's default "@/components" and "@/lib" base alias:
    '^@/(.*)$': '<rootDir>/src/$1',
    // Mappings for components.json aliases:
    '^components/(.*)$': '<rootDir>/src/components/$1',
    '^utils/(.*)$': '<rootDir>/src/lib/utils/$1',
    '^ui/(.*)$': '<rootDir>/src/components/ui/$1',
    '^lib/(.*)$': '<rootDir>/src/lib/$1',
    '^hooks/(.*)$': '<rootDir>/src/hooks/$1',
  },

  // The test environment that will be used for testing
  testEnvironment: 'jsdom',
};

// createJestConfig is exported this way to ensure that next/jest can load the Next.js config which is async
export default createJestConfig(config);

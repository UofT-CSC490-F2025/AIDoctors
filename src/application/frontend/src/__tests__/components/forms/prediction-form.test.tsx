/// <reference types="@testing-library/jest-dom" />
import { describe, expect, it, jest, beforeEach } from '@jest/globals';
import { render, screen, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';

// Mock scrollIntoView
Element.prototype.scrollIntoView = jest.fn();

const mockSetUser = jest.fn();
const mockSetResults = jest.fn();
const mockGetApiBaseUrl = jest.fn(() => 'http://localhost:8000/api');
const mockFetch = jest.fn();

global.fetch = mockFetch as any;

jest.mock('@/hooks/useUser', () => ({
  useUser: () => ({
    setUser: mockSetUser,
  }),
}));

jest.mock('@/utils/api', () => ({
  getApiBaseUrl: mockGetApiBaseUrl,
}));

describe('PredictionForm Component', () => {
  // Default data for mocks
  const mockOptions = [
    'Warfarin',
    'Aspirin',
    'Hypertension',
    'Diabetes',
    'COPD',
  ];
  const mockPredictionResponse = {
    alert_level: 'high',
    interaction_description: 'Severe interaction detected',
    recommendations: ['Monitor patient closely'],
  };

  beforeEach(() => {
    jest.clearAllMocks();

    // Setup a "smart" mock that handles both Autocomplete (GET) and Submit (POST)
    mockFetch.mockImplementation(async (url: any, options: any) => {
      const urlString = url.toString();

      // Handle Autocomplete Endpoints
      if (
        urlString.includes('/predict/matching_drugs') ||
        urlString.includes('/predict/matching_comorbidities')
      ) {
        return {
          ok: true,
          status: 200,
          json: async () => mockOptions,
        };
      }

      // Handle Prediction Endpoint (Default Success)
      if (urlString.includes('/predict') && options?.method === 'POST') {
        return {
          ok: true,
          status: 200,
          json: async () => mockPredictionResponse,
        };
      }

      return { ok: false, status: 404 };
    });
  });

  // Helper to interact with AsyncSelect components
  const selectOption = async (labelText: RegExp, optionText: string) => {
    const input = screen.getByLabelText(labelText);
    await userEvent.type(input, optionText);
    // Wait for the mock fetch to resolve and options to render
    const option = await screen.findByText(optionText);
    await userEvent.click(option);
  };

  it('should render prediction form with all required fields', async () => {
    const { PredictionForm } = await import(
      '@/components/forms/prediction-form'
    );
    render(<PredictionForm setResults={mockSetResults} />);

    expect(screen.getByLabelText(/age/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/sex/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/current medication/i)).toBeInTheDocument();
    expect(
      screen.getByLabelText(/new medication being considered/i)
    ).toBeInTheDocument();
    expect(screen.getByLabelText(/comorbidities/i)).toBeInTheDocument();
    expect(
      screen.getByRole('button', { name: /predict/i })
    ).toBeInTheDocument();
  });

  it('should submit form with valid data and display results', async () => {
    const { PredictionForm } = await import(
      '@/components/forms/prediction-form'
    );
    render(<PredictionForm setResults={mockSetResults} />);

    // Standard inputs
    await userEvent.type(screen.getByLabelText(/age/i), '65');
    await userEvent.selectOptions(screen.getByLabelText(/sex/i), 'M');

    // Async Selects
    await selectOption(/current medication/i, 'Warfarin');
    await selectOption(/new medication being considered/i, 'Aspirin');
    await selectOption(/comorbidities/i, 'Hypertension');
    // Multi-select: add another
    await selectOption(/comorbidities/i, 'Diabetes');

    const submitButton = screen.getByRole('button', { name: /predict/i });
    await userEvent.click(submitButton);

    await waitFor(() => {
      // Find the specific POST call among the various GET calls
      const postCall = mockFetch.mock.calls.find(
        (call: any) =>
          call[0].includes('/predict') && call[1]?.method === 'POST'
      );

      expect(postCall).toBeTruthy();
      expect(postCall[1]).toEqual(
        expect.objectContaining({
          headers: { 'Content-Type': 'application/json' },
          body: expect.any(String),
        })
      );
    });

    expect(mockSetResults).toHaveBeenCalledWith(mockPredictionResponse);
  });

  it('should display error message when API returns 401', async () => {
    // Override ONLY the POST response
    mockFetch.mockImplementation(async (url: any, options: any) => {
      if (url.toString().includes('matching_')) {
        return { ok: true, json: async () => mockOptions };
      }
      if (options?.method === 'POST') {
        return {
          status: 401,
          ok: false,
          json: async () => ({ detail: 'Unauthorized' }),
        };
      }
      return { ok: false };
    });

    const { PredictionForm } = await import(
      '@/components/forms/prediction-form'
    );
    render(<PredictionForm setResults={mockSetResults} />);

    await selectOption(/current medication/i, 'Warfarin');
    await selectOption(/new medication being considered/i, 'Aspirin');

    await userEvent.click(screen.getByRole('button', { name: /predict/i }));

    await waitFor(() => {
      expect(screen.getByText(/unauthenticated request/i)).toBeInTheDocument();
    });

    expect(mockSetUser).toHaveBeenCalledWith(null);
  });

  it('should display error message when API returns client error', async () => {
    const errorMessage = 'Invalid drug name provided';

    mockFetch.mockImplementation(async (url: any, options: any) => {
      if (url.toString().includes('matching_')) {
        return { ok: true, json: async () => mockOptions };
      }
      if (options?.method === 'POST') {
        return {
          status: 400,
          ok: false,
          json: async () => ({ detail: errorMessage }),
        };
      }
      return { ok: false };
    });

    const { PredictionForm } = await import(
      '@/components/forms/prediction-form'
    );
    render(<PredictionForm setResults={mockSetResults} />);

    await selectOption(/current medication/i, 'Warfarin');
    await selectOption(/new medication being considered/i, 'Aspirin');

    await userEvent.click(screen.getByRole('button', { name: /predict/i }));

    await waitFor(() => {
      expect(screen.getByText(errorMessage)).toBeInTheDocument();
    });
  });

  it('should display generic error message when API request fails', async () => {
    mockFetch.mockImplementation(async (url: any, options: any) => {
      if (url.toString().includes('matching_')) {
        return { ok: true, json: async () => mockOptions };
      }
      if (options?.method === 'POST') {
        return {
          status: 500,
          ok: false,
          json: async () => ({}),
        };
      }
      return { ok: false };
    });

    const { PredictionForm } = await import(
      '@/components/forms/prediction-form'
    );
    render(<PredictionForm setResults={mockSetResults} />);

    await selectOption(/current medication/i, 'Warfarin');
    await selectOption(/new medication being considered/i, 'Aspirin');

    await userEvent.click(screen.getByRole('button', { name: /predict/i }));

    await waitFor(() => {
      expect(screen.getByText(/request failed/i)).toBeInTheDocument();
    });
  });

  it('should display error message when network error occurs', async () => {
    const consoleSpy = jest
      .spyOn(console, 'error')
      .mockImplementation(() => {});

    // Only fail the POST, allow GETs so the form doesn't crash while typing
    mockFetch.mockImplementation(async (url: any, options: any) => {
      if (url.toString().includes('matching_')) {
        return { ok: true, json: async () => mockOptions };
      }
      if (options?.method === 'POST') {
        throw new Error('Network error');
      }
      return { ok: false };
    });

    const { PredictionForm } = await import(
      '@/components/forms/prediction-form'
    );
    render(<PredictionForm setResults={mockSetResults} />);

    await selectOption(/current medication/i, 'Warfarin');
    await selectOption(/new medication being considered/i, 'Aspirin');

    await userEvent.click(screen.getByRole('button', { name: /predict/i }));

    await waitFor(() => {
      expect(
        screen.getByText(/an unexpected error occurred/i)
      ).toBeInTheDocument();
    });

    consoleSpy.mockRestore();
  });

  it('should show loading state when form is submitting', async () => {
    // Hang the POST request forever
    mockFetch.mockImplementation(async (url: any, options: any) => {
      if (url.toString().includes('matching_')) {
        return { ok: true, json: async () => mockOptions };
      }
      if (options?.method === 'POST') {
        return new Promise(() => {});
      }
      return { ok: false };
    });

    const { PredictionForm } = await import(
      '@/components/forms/prediction-form'
    );
    render(<PredictionForm setResults={mockSetResults} />);

    await selectOption(/current medication/i, 'Warfarin');
    await selectOption(/new medication being considered/i, 'Aspirin');

    const submitButton = screen.getByRole('button', { name: /predict/i });
    await userEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/generating alerts/i)).toBeInTheDocument();
      expect(submitButton).toBeDisabled();
    });
  });

  it('should parse comorbidities correctly as array in body', async () => {
    const { PredictionForm } = await import(
      '@/components/forms/prediction-form'
    );
    render(<PredictionForm setResults={mockSetResults} />);

    await selectOption(/current medication/i, 'Warfarin');
    await selectOption(/new medication being considered/i, 'Aspirin');

    // Select multiple comorbidities
    await selectOption(/comorbidities/i, 'Hypertension');
    await selectOption(/comorbidities/i, 'Diabetes');
    await selectOption(/comorbidities/i, 'COPD');

    await userEvent.click(screen.getByRole('button', { name: /predict/i }));

    await waitFor(() => {
      // Find the POST call specifically
      const postCall = mockFetch.mock.calls.find(
        (call: any) => call[1]?.method === 'POST'
      );
      expect(postCall).toBeDefined();

      const requestBody = JSON.parse(postCall[1].body);
      expect(requestBody.Comorbidities).toEqual([
        'Hypertension',
        'Diabetes',
        'COPD',
      ]);
    });
  });
});

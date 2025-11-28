/// <reference types="@testing-library/jest-dom" />
import { describe, expect, it, jest, beforeEach } from '@jest/globals';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';

// Mock scrollIntoView which is not implemented in jsdom
Element.prototype.scrollIntoView = jest.fn();

const mockSetUser = jest.fn();
const mockSetResults = jest.fn();
const mockGetApiBaseUrl = jest.fn(() => 'http://localhost:8000');
const mockFetch = jest.fn();

// Setup global fetch mock
global.fetch = mockFetch as any;

// Mock the hooks and dependencies
jest.mock('@/hooks/useUser', () => ({
  useUser: () => ({
    setUser: mockSetUser,
  }),
}));

jest.mock('@/utils/api', () => ({
  getApiBaseUrl: mockGetApiBaseUrl,
}));

describe('PredictionForm Component', () => {
  beforeEach(() => {
    mockSetUser.mockClear();
    mockSetResults.mockClear();
    mockGetApiBaseUrl.mockClear();
    mockFetch.mockClear();
  });

  it('should render prediction form with all required fields', async () => {
    const { PredictionForm } = await import('@/components/forms/prediction-form');
    render(<PredictionForm setResults={mockSetResults} />);
    
    expect(screen.getByLabelText(/age/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/sex/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/current medication/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/new medication being considered/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/comorbidities/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/overlap start/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/overlap stop/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /predict/i })).toBeInTheDocument();
  });

  it('should submit form with valid data and display results', async () => {
    const mockResponse = {
      alert_level: 'high',
      interaction_description: 'Severe interaction detected',
      recommendations: ['Monitor patient closely'],
    };

    mockFetch.mockResolvedValueOnce({
      status: 200,
      ok: true,
      json: async () => mockResponse,
    });

    const { PredictionForm } = await import('@/components/forms/prediction-form');
    render(<PredictionForm setResults={mockSetResults} />);
    
    const ageInput = screen.getByLabelText(/age/i) as HTMLInputElement;
    const sexSelect = screen.getByLabelText(/sex/i) as HTMLSelectElement;
    const currentDrugInput = screen.getByLabelText(/current medication/i) as HTMLInputElement;
    const newDrugInput = screen.getByLabelText(/new medication being considered/i) as HTMLInputElement;
    const comorbiditiesInput = screen.getByLabelText(/comorbidities/i) as HTMLTextAreaElement;
    const submitButton = screen.getByRole('button', { name: /predict/i });

    await userEvent.type(ageInput, '65');
    await userEvent.selectOptions(sexSelect, 'M');
    await userEvent.type(currentDrugInput, 'Warfarin');
    await userEvent.type(newDrugInput, 'Aspirin');
    await userEvent.type(comorbiditiesInput, 'Hypertension, Diabetes');
    await userEvent.click(submitButton);

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/predict',
        expect.objectContaining({
          method: 'POST',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
          },
          body: expect.any(String),
        })
      );
    });

    expect(mockSetResults).toHaveBeenCalledWith(mockResponse);
  });

  it('should display error message when API returns 401', async () => {
    mockFetch.mockResolvedValueOnce({
      status: 401,
      ok: false,
      json: async () => ({ detail: 'Unauthorized' }),
    });

    const { PredictionForm } = await import('@/components/forms/prediction-form');
    render(<PredictionForm setResults={mockSetResults} />);
    
    const currentDrugInput = screen.getByLabelText(/current medication/i) as HTMLInputElement;
    const newDrugInput = screen.getByLabelText(/new medication being considered/i) as HTMLInputElement;
    const submitButton = screen.getByRole('button', { name: /predict/i });

    await userEvent.type(currentDrugInput, 'Warfarin');
    await userEvent.type(newDrugInput, 'Aspirin');
    await userEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/unauthenticated request/i)).toBeInTheDocument();
    });

    expect(mockSetUser).toHaveBeenCalledWith(null);
  });

  it('should display error message when API returns client error', async () => {
    const errorMessage = 'Invalid drug name provided';
    
    mockFetch.mockResolvedValueOnce({
      status: 400,
      ok: false,
      json: async () => ({ detail: errorMessage }),
    });

    const { PredictionForm } = await import('@/components/forms/prediction-form');
    render(<PredictionForm setResults={mockSetResults} />);
    
    const currentDrugInput = screen.getByLabelText(/current medication/i) as HTMLInputElement;
    const newDrugInput = screen.getByLabelText(/new medication being considered/i) as HTMLInputElement;
    const submitButton = screen.getByRole('button', { name: /predict/i });

    await userEvent.type(currentDrugInput, 'InvalidDrug');
    await userEvent.type(newDrugInput, 'Aspirin');
    await userEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(errorMessage)).toBeInTheDocument();
    });
  });

  it('should display generic error message when API request fails', async () => {
    mockFetch.mockResolvedValueOnce({
      status: 500,
      ok: false,
      json: async () => ({}),
    });

    const { PredictionForm } = await import('@/components/forms/prediction-form');
    render(<PredictionForm setResults={mockSetResults} />);
    
    const currentDrugInput = screen.getByLabelText(/current medication/i) as HTMLInputElement;
    const newDrugInput = screen.getByLabelText(/new medication being considered/i) as HTMLInputElement;
    const submitButton = screen.getByRole('button', { name: /predict/i });

    await userEvent.type(currentDrugInput, 'Warfarin');
    await userEvent.type(newDrugInput, 'Aspirin');
    await userEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/request failed/i)).toBeInTheDocument();
    });
  });

  it('should display error message when network error occurs', async () => {
    // Suppress console.error
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    
    mockFetch.mockRejectedValueOnce(new Error('Network error'));

    const { PredictionForm } = await import('@/components/forms/prediction-form');
    render(<PredictionForm setResults={mockSetResults} />);
    
    const currentDrugInput = screen.getByLabelText(/current medication/i) as HTMLInputElement;
    const newDrugInput = screen.getByLabelText(/new medication being considered/i) as HTMLInputElement;
    const submitButton = screen.getByRole('button', { name: /predict/i });

    await userEvent.type(currentDrugInput, 'Warfarin');
    await userEvent.type(newDrugInput, 'Aspirin');
    await userEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/an unexpected error occurred/i)).toBeInTheDocument();
    });

    // Assert the error was handled/logged internally
    expect(consoleSpy).toHaveBeenCalled();
    // Restore console.error to avoid hiding real errors in other tests
    consoleSpy.mockRestore();
  });

  it('should show loading state when form is submitting', async () => {
    mockFetch.mockImplementation(() => new Promise(() => {})); // Never resolves

    const { PredictionForm } = await import('@/components/forms/prediction-form');
    render(<PredictionForm setResults={mockSetResults} />);
    
    const currentDrugInput = screen.getByLabelText(/current medication/i) as HTMLInputElement;
    const newDrugInput = screen.getByLabelText(/new medication being considered/i) as HTMLInputElement;
    const submitButton = screen.getByRole('button', { name: /predict/i });

    await userEvent.type(currentDrugInput, 'Warfarin');
    await userEvent.type(newDrugInput, 'Aspirin');
    await userEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/generating alerts/i)).toBeInTheDocument();
      expect(submitButton).toBeDisabled();
    });
  });

  it('should parse comorbidities correctly as comma-separated values', async () => {
    const mockResponse = {
      alert_level: 'moderate',
      interaction_description: 'Moderate interaction',
      recommendations: [],
    };

    mockFetch.mockResolvedValueOnce({
      status: 200,
      ok: true,
      json: async () => mockResponse,
    });

    const { PredictionForm } = await import('@/components/forms/prediction-form');
    render(<PredictionForm setResults={mockSetResults} />);
    
    const currentDrugInput = screen.getByLabelText(/current medication/i) as HTMLInputElement;
    const newDrugInput = screen.getByLabelText(/new medication being considered/i) as HTMLInputElement;
    const comorbiditiesInput = screen.getByLabelText(/comorbidities/i) as HTMLTextAreaElement;
    const submitButton = screen.getByRole('button', { name: /predict/i });

    await userEvent.type(currentDrugInput, 'Warfarin');
    await userEvent.type(newDrugInput, 'Aspirin');
    await userEvent.type(comorbiditiesInput, 'Hypertension, Diabetes, COPD');
    await userEvent.click(submitButton);

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalled();
    });

    const fetchCall = mockFetch.mock.calls[0];
    const requestBody = JSON.parse(fetchCall[1].body);
    expect(requestBody.Comorbidities).toEqual(['Hypertension', 'Diabetes', 'COPD']);
  });
});

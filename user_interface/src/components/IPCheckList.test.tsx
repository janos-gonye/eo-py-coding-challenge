import { render, screen, waitFor, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { IPCheckList } from './IPCheckList';

// Mock apiUtils to avoid dependence on environment constants
vi.mock('../utils/apiUtils', () => ({
  getServerUrl: () => 'http://localhost:8000',
}));

describe('IPCheckList Component', () => {
  const mockChecks = [
    {
      id: '1',
      ip_address: '192.168.1.1',
      verdict: null,
      task_status: 'pending',
      created_at: '2023-10-27T10:00:00Z',
    },
    {
      id: '2',
      ip_address: '8.8.8.8',
      verdict: 'The IP is safe.',
      task_status: 'success',
      created_at: '2023-10-27T10:05:00Z',
    },
  ];

  beforeEach(() => {
    vi.spyOn(globalThis, 'fetch').mockImplementation(() =>
      Promise.resolve(new Response(JSON.stringify(mockChecks), { status: 200 }))
    );
  });

  afterEach(() => {
    vi.restoreAllMocks();
    vi.useRealTimers();
  });

  it('shows loading state initially', async () => {
    render(<IPCheckList />);
    expect(screen.getByText(/loading checks.../i)).toBeInTheDocument();
  });

  it('renders a list of checks with correct statuses', async () => {
    render(<IPCheckList />);

    await waitFor(() => {
      expect(screen.queryByText(/loading checks.../i)).not.toBeInTheDocument();
    });

    expect(screen.getByText('192.168.1.1')).toBeInTheDocument();
    expect(screen.getByText('8.8.8.8')).toBeInTheDocument();
    expect(screen.getByText('Pending')).toBeInTheDocument();
    expect(screen.getByText('Success')).toBeInTheDocument();
  });

  it('shows empty state when no checks are available', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(
      new Response(JSON.stringify([]), { status: 200 })
    );

    render(<IPCheckList />);

    await waitFor(() => {
      expect(screen.getByText(/no ip checks yet/i)).toBeInTheDocument();
    });
  });

  it('polls for updates every second', async () => {
    // Enable fake timers BEFORE render so setInterval is captured
    vi.useFakeTimers();
    const fetchSpy = vi.spyOn(globalThis, 'fetch');

    render(<IPCheckList />);

    // Initial fetch happens on mount. We need to flush the microtasks.
    await vi.runAllTicks();

    expect(fetchSpy).toHaveBeenCalledTimes(1);

    // Advance time by one second AND flush microtasks
    await act(async () => {
      await vi.advanceTimersByTimeAsync(1000);
    });

    expect(fetchSpy).toHaveBeenCalledTimes(2);

    // Advance time by another second
    await act(async () => {
      await vi.advanceTimersByTimeAsync(1000);
    });

    expect(fetchSpy).toHaveBeenCalledTimes(3);
  });

  it('handles fetch errors gracefully', async () => {
    vi.spyOn(globalThis, 'fetch').mockRejectedValueOnce(new Error('API error'));
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => { });

    render(<IPCheckList />);

    await waitFor(() => {
      expect(consoleSpy).toHaveBeenCalledWith('Failed to fetch IP checks:', expect.any(Error));
    });

    consoleSpy.mockRestore();
  });
});

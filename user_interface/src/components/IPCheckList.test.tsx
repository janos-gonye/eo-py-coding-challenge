import { render, screen, waitFor, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { IPCheckList } from './IPCheckList';

// Mock apiUtils to include getWebSocketUrl
vi.mock('../utils/apiUtils', () => ({
  getServerUrl: () => 'http://localhost:8000',
  getWebSocketUrl: () => 'ws://localhost:8000/ws',
}));

// Mock WebSocket
class MockWebSocket {
  onmessage: ((event: MessageEvent) => void) | null = null;
  onclose: (() => void) | null = null;
  onerror: ((error: Event) => void) | null = null;
  send = vi.fn();
  close = vi.fn();
  url: string;
  constructor(url: string) {
    this.url = url;
    MockWebSocket.instances.push(this);
  }
  static instances: MockWebSocket[] = [];
}

vi.stubGlobal('WebSocket', MockWebSocket);

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
    MockWebSocket.instances = [];
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
    expect(screen.getByText('192.168.1.1').getAttribute('title')).toBe('192.168.1.1');
    expect(screen.getByText('8.8.8.8').getAttribute('title')).toBe('8.8.8.8');
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

  it('reconnects after 3 seconds when connection is closed', async () => {
    vi.useFakeTimers();
    render(<IPCheckList />);

    // Initial connection should happen immediately in useEffect
    expect(MockWebSocket.instances.length).toBe(1);
    const firstInstance = MockWebSocket.instances[0];

    // Simulate close
    act(() => {
      if (firstInstance.onclose) firstInstance.onclose();
    });

    // Should not have reconnected immediately
    expect(MockWebSocket.instances.length).toBe(1);

    // Advance time by 3 seconds
    act(() => {
      vi.advanceTimersByTime(3000);
    });

    // Should have reconnected
    expect(MockWebSocket.instances.length).toBe(2);
    vi.useRealTimers();
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

  it('adds a new item received via WebSocket if not already in the list', async () => {
    // Initial fetch returns empty list
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(
      new Response(JSON.stringify([]), { status: 200 })
    );

    render(<IPCheckList />);

    // Wait for loading to finish and show empty state
    await waitFor(() => {
      expect(screen.getByText(/no ip checks yet/i)).toBeInTheDocument();
    });

    // Simulate receiving a new item via WebSocket
    const newItem = {
      id: 'new-id',
      ip_address: '1.2.3.4',
      verdict: null,
      task_status: 'pending',
      created_at: new Date().toISOString(),
    };

    act(() => {
      const socketInstance = MockWebSocket.instances[0];
      if (socketInstance.onmessage) {
        socketInstance.onmessage(new MessageEvent('message', { data: JSON.stringify(newItem) }));
      }
    });

    // Verify it appears in the list
    expect(screen.getByText('1.2.3.4')).toBeInTheDocument();
    expect(screen.queryByText(/no ip checks yet/i)).not.toBeInTheDocument();
  });
});

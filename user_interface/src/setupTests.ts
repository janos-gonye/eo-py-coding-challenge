import '@testing-library/jest-dom';
import { vi } from 'vitest';

// Global mocks for browser APIs not perfectly simulated in JSDOM
class MockWebSocket {
  onmessage: ((event: MessageEvent) => void) | null = null;
  onclose: (() => void) | null = null;
  onerror: ((event: Event) => void) | null = null;
  send = vi.fn();
  close = vi.fn();
  static instances: MockWebSocket[] = [];
  constructor() {
    MockWebSocket.instances.push(this);
  }
}

vi.stubGlobal('WebSocket', MockWebSocket);

// Default fetch mock to prevent ECONNREFUSED noise
if (!globalThis.fetch) {
  vi.spyOn(globalThis, 'fetch').mockImplementation(() =>
    Promise.resolve(new Response(JSON.stringify([]), { status: 200 }))
  );
}

import { describe, it, expect } from 'vitest';
import { getServerUrl, getWebSocketUrl } from './apiUtils';

describe('apiUtils', () => {
  describe('getServerUrl', () => {
    it('returns the correct server URL from constants', () => {
      expect(getServerUrl()).toBe('http://localhost:8000');
    });

    it('returns a string', () => {
      expect(typeof getServerUrl()).toBe('string');
    });
  });

  describe('getWebSocketUrl', () => {
    it('returns the correct WebSocket URL from constants', () => {
      expect(getWebSocketUrl()).toBe('ws://localhost:8000/ws');
    });

    it('returns a string', () => {
      expect(typeof getWebSocketUrl()).toBe('string');
    });
  });
});

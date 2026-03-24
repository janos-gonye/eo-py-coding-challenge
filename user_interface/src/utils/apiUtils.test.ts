import { describe, it, expect } from 'vitest';
import { getServerUrl } from './apiUtils';

describe('getServerUrl', () => {
  it('returns the correct server URL from constants', () => {
    expect(getServerUrl()).toBe('http://localhost:8000');
  });

  it('returns a string', () => {
    expect(typeof getServerUrl()).toBe('string');
  });
});

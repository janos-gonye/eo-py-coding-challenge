import { PROTOCOL, SERVER, PORT } from '../constants/api';

export function getServerUrl(): string {
  return `${PROTOCOL}://${SERVER}:${PORT}`;
}

export function getWebSocketUrl(): string {
  const isHttps = (PROTOCOL as string) === 'https';
  const wsProtocol = isHttps ? 'wss' : 'ws';
  return `${wsProtocol}://${SERVER}:${PORT}/ws`;
}

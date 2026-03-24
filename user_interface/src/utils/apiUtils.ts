import { PROTOCOL, SERVER, PORT } from '../constants/api';

export function getServerUrl(): string {
  return `${PROTOCOL}://${SERVER}:${PORT}`;
}

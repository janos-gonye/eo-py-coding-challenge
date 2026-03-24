import { useState } from 'react';
import type { ChangeEvent } from 'react';
import './index.css';

const IPv4_REGEX = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
const IPv6_REGEX = /^(?:(?:(?:[a-fA-F0-9]{1,4}:){6}|::(?:[a-fA-F0-9]{1,4}:){5}|(?:[a-fA-F0-9]{1,4})?::(?:[a-fA-F0-9]{1,4}:){4}|(?:(?:[a-fA-F0-9]{1,4}:){0,1}[a-fA-F0-9]{1,4})?::(?:[a-fA-F0-9]{1,4}:){3}|(?:(?:[a-fA-F0-9]{1,4}:){0,2}[a-fA-F0-9]{1,4})?::(?:[a-fA-F0-9]{1,4}:){2}|(?:(?:[a-fA-F0-9]{1,4}:){0,3}[a-fA-F0-9]{1,4})?::[a-fA-F0-9]{1,4}:|(?:(?:[a-fA-F0-9]{1,4}:){0,4}[a-fA-F0-9]{1,4})?::)(?:[a-fA-F0-9]{1,4}:[a-fA-F0-9]{1,4}|(?:(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.){3}(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d))|(?:(?:[a-fA-F0-9]{1,4}:){0,5}[a-fA-F0-9]{1,4})?::[a-fA-F0-9]{1,4}|(?:(?:[a-fA-F0-9]{1,4}:){0,6}[a-fA-F0-9]{1,4})?::)$/;

function isValidIP(ip: string): boolean {
  return IPv4_REGEX.test(ip) || IPv6_REGEX.test(ip);
}

function App() {
  const [ipAddress, setIpAddress] = useState<string>('');
  const [touched, setTouched] = useState<boolean>(false);

  const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    setIpAddress(e.target.value);
    setTouched(true);
  };

  const valid = isValidIP(ipAddress);

  return (
    <div className="app-container">
      <div className="glass-card">
        <h1 className="title">IP checker</h1>
        <p className="subtitle">Enter an IP address to check</p>

        <div className="input-group">
          <input
            type="text"
            className={`ip-input ${touched ? (valid ? 'valid' : 'invalid') : ''}`}
            placeholder="IP address"
            value={ipAddress}
            onChange={handleInputChange}
          />
          <div className="icon-container">
            {touched && ipAddress !== '' && (
              valid ? (
                <svg className="icon success" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                </svg>
              ) : (
                <svg className="icon error" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M6 18L18 6M6 6l12 12" />
                </svg>
              )
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;

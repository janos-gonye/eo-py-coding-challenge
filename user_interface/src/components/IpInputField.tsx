import { useState } from 'react';
import type { ChangeEvent } from 'react';
import { getServerUrl } from '../utils/apiUtils';
import { isValidIP } from '../utils/ipUtils';
import { Popup } from './Popup';
import './IpInputField.css';



interface PopupState {
  message: string;
  type: 'success' | 'error';
}

export function IpInputField() {
  const [ipAddress, setIpAddress] = useState<string>('');
  const [touched, setTouched] = useState<boolean>(false);
  const [popup, setPopup] = useState<PopupState | null>(null);

  const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    setIpAddress(e.target.value);
    setTouched(true);
  };

  const valid = isValidIP(ipAddress);

  const handleSendRequest = async () => {
    if (!valid) return;
    try {
      const url = `${getServerUrl()}/ip/check`;
      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ip_address: ipAddress }),
      });
      const data = await response.json();
      if (response.ok) {
        setPopup({ type: 'success', message: 'IP address check started successfully.' });
        setIpAddress('');
        setTouched(false);
      } else {
        const detail = Array.isArray(data.detail)
          ? data.detail.map((d: { msg: string }) => d.msg).join(' ')
          : (data.detail ?? 'An error occurred.');
        setPopup({ type: 'error', message: detail });
      }
    } catch {
      setPopup({ type: 'error', message: 'Could not reach the server. Please try again.' });
    }
  };

  return (
    <>
      {popup && (
        <Popup
          type={popup.type}
          message={popup.message}
          onClose={() => setPopup(null)}
        />
      )}
      <div className="input-row">
        <div className="input-wrapper">
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
        <button
          type="button"
          onClick={handleSendRequest}
          disabled={!valid || ipAddress === ''}
          className="send-button"
        >
          <svg className="send-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
          <span>Send</span>
        </button>
      </div>
    </>
  );
}

import { useState, useEffect, useCallback } from 'react';
import { getServerUrl } from '../utils/apiUtils';
import './IPCheckList.css';

interface IPCheckItem {
  id: string;
  ip_address: string;
  verdict: string | null;
  task_status: 'pending' | 'processing' | 'success' | 'failed';
  created_at: string;
}

export function IPCheckList() {
  const [checks, setChecks] = useState<IPCheckItem[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchChecks = useCallback(async () => {
    try {
      const response = await fetch(`${getServerUrl()}/ip/list`);
      if (response.ok) {
        const data = await response.json();
        setChecks(data);
      }
    } catch (error) {
      console.error('Failed to fetch IP checks:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchChecks();
    const interval = setInterval(fetchChecks, 1000);
    return () => clearInterval(interval);
  }, [fetchChecks]);

  const getStatusIcon = (status: IPCheckItem['task_status']) => {
    switch (status) {
      case 'pending':
        return (
          <svg className="status-icon pending" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
      case 'processing':
        return (
          <svg className="status-icon processing" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        );
      case 'success':
        return (
          <svg className="status-icon success" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
          </svg>
        );
      case 'failed':
        return (
          <svg className="status-icon failed" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M6 18L18 6M6 6l12 12" />
          </svg>
        );
    }
  };

  const getStatusText = (status: IPCheckItem['task_status']) => {
    switch (status) {
      case 'pending': return 'Pending';
      case 'processing': return 'Processing';
      case 'success': return 'Success';
      case 'failed': return 'Failed';
      default: return status;
    }
  };

  if (loading && checks.length === 0) {
    return <div className="ip-check-list-loading">Loading checks...</div>;
  }

  return (
    <div className="ip-check-list">
      {checks.map((check) => (
        <div
          key={check.id}
          className={`ip-check-item ${check.task_status === 'success' ? 'item-success' : ''}`}
        >
          <div className="item-header">
            <span className="ip-address" title={check.ip_address}>{check.ip_address}</span>
            <div className={`status-badge badge-${check.task_status}`}>
              {getStatusIcon(check.task_status)}
              <span>{getStatusText(check.task_status)}</span>
            </div>
          </div>

          <div className="ip-date">
            Checked on {new Date(check.created_at).toLocaleString(undefined, {
              dateStyle: 'medium',
              timeStyle: 'short'
            })}
          </div>

          {check.task_status === 'success' && check.verdict && (
            <div className="verdict-container">
              <span className="verdict-label">Technical Verdict</span>
              <p className="verdict-text">{check.verdict}</p>
            </div>
          )}
        </div>
      ))}
      {checks.length === 0 && !loading && (
        <div className="no-checks-message">No IP checks yet.</div>
      )}
    </div>
  );
}

import './Popup.css';

interface PopupProps {
  message: string;
  type: 'success' | 'error';
  onClose: () => void;
}

export function Popup({ message, type, onClose }: PopupProps) {
  return (
    <div className="popup-overlay" onClick={onClose}>
      <div
        className={`popup-card popup-${type}`}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="popup-icon-wrap">
          {type === 'success' ? (
            <svg className="popup-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
            </svg>
          ) : (
            <svg className="popup-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M6 18L18 6M6 6l12 12" />
            </svg>
          )}
        </div>
        <p className="popup-message">{message}</p>
        <button className="popup-close" onClick={onClose}>
          Close
        </button>
      </div>
    </div>
  );
}

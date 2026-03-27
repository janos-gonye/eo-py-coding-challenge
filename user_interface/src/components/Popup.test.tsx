import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { Popup } from './Popup';

describe('Popup', () => {
  it('renders the message', () => {
    render(<Popup type="success" message="All good!" onClose={() => {}} />);
    expect(screen.getByText('All good!')).toBeInTheDocument();
  });

  it('renders a Close button', () => {
    render(<Popup type="success" message="All good!" onClose={() => {}} />);
    expect(screen.getByRole('button', { name: /close/i })).toBeInTheDocument();
  });

  it('applies the popup-success class for type success', () => {
    const { container } = render(<Popup type="success" message="OK" onClose={() => {}} />);
    expect(container.querySelector('.popup-success')).toBeInTheDocument();
    expect(container.querySelector('.popup-error')).not.toBeInTheDocument();
  });

  it('applies the popup-error class for type error', () => {
    const { container } = render(<Popup type="error" message="Oops" onClose={() => {}} />);
    expect(container.querySelector('.popup-error')).toBeInTheDocument();
    expect(container.querySelector('.popup-success')).not.toBeInTheDocument();
  });

  it('calls onClose when the Close button is clicked', () => {
    const onClose = vi.fn();
    render(<Popup type="success" message="OK" onClose={onClose} />);
    fireEvent.click(screen.getByRole('button', { name: /close/i }));
    expect(onClose).toHaveBeenCalledOnce();
  });

  it('calls onClose when the overlay is clicked', () => {
    const onClose = vi.fn();
    const { container } = render(<Popup type="success" message="OK" onClose={onClose} />);
    fireEvent.click(container.querySelector('.popup-overlay')!);
    expect(onClose).toHaveBeenCalledOnce();
  });

  it('does not call onClose when the card itself is clicked', () => {
    const onClose = vi.fn();
    const { container } = render(<Popup type="success" message="OK" onClose={onClose} />);
    fireEvent.click(container.querySelector('.popup-card')!);
    expect(onClose).not.toHaveBeenCalled();
  });

  it('calls onClose when the Enter key is pressed', () => {
    const onClose = vi.fn();
    render(<Popup type="success" message="OK" onClose={onClose} />);
    fireEvent.keyDown(window, { key: 'Enter' });
    expect(onClose).toHaveBeenCalledOnce();
  });
});

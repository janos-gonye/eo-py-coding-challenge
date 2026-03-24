import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import App from './App';

describe('App IP Validation', () => {
  it('renders the initial layout without icons', () => {
    const { container } = render(<App />);
    const input = screen.getByPlaceholderText('IP address');
    expect(input).toBeInTheDocument();

    // initially, there should be no icon
    const iconContainer = container.querySelector('.icon-container');
    expect(iconContainer?.children.length).toBe(0);
  });

  it('displays a green checkmark icon when a correct IPv4 address is provided', () => {
    const { container } = render(<App />);
    const input = screen.getByPlaceholderText('IP address');

    fireEvent.change(input, { target: { value: '192.168.1.1' } });

    const svg = container.querySelector('svg');
    expect(svg).toBeInTheDocument();
    expect(svg).toHaveClass('success');
    expect(svg).not.toHaveClass('error');

    expect(input).toHaveClass('valid');
    expect(input).not.toHaveClass('invalid');
  });

  it('displays a red x icon when an incorrect IPv4 address is provided', () => {
    const { container } = render(<App />);
    const input = screen.getByPlaceholderText('IP address');

    fireEvent.change(input, { target: { value: '256.256.256.256' } });

    const svg = container.querySelector('svg');
    expect(svg).toBeInTheDocument();
    expect(svg).toHaveClass('error');
    expect(svg).not.toHaveClass('success');

    expect(input).toHaveClass('invalid');
    expect(input).not.toHaveClass('valid');
  });

  it('displays a green checkmark icon when a correct IPv6 address is provided', () => {
    const { container } = render(<App />);
    const input = screen.getByPlaceholderText('IP address');

    // Standard IPv6
    fireEvent.change(input, { target: { value: '2001:0db8:85a3:0000:0000:8a2e:0370:7334' } });

    const svg = container.querySelector('svg');
    expect(svg).toBeInTheDocument();
    expect(svg).toHaveClass('success');
  });

  it('displays a red x icon when an incorrect IPv6 address is provided', () => {
    const { container } = render(<App />);
    const input = screen.getByPlaceholderText('IP address');

    // Invalid IPv6 containing invalid characters
    fireEvent.change(input, { target: { value: '2001:0db8:85a3:000z::1' } });

    const svg = container.querySelector('svg');
    expect(svg).toBeInTheDocument();
    expect(svg).toHaveClass('error');
  });
});

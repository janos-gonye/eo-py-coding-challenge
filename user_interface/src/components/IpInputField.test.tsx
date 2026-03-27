import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, afterEach } from 'vitest';
import { IpInputField } from './IpInputField';

describe('IpInputField Validation', () => {
  it('renders the initial layout without icons', () => {
    const { container } = render(<IpInputField />);
    const input = screen.getByPlaceholderText('IP address');
    expect(input).toBeInTheDocument();

    const iconContainer = container.querySelector('.icon-container');
    expect(iconContainer?.children.length).toBe(0);

    const button = screen.getByRole('button', { name: /send/i });
    expect(button).toBeDisabled();
  });

  it('displays a green checkmark icon and enables button when a correct IPv4 address is provided', () => {
    const { container } = render(<IpInputField />);
    const input = screen.getByPlaceholderText('IP address');
    const button = screen.getByRole('button', { name: /send/i });

    fireEvent.change(input, { target: { value: '192.168.1.1' } });

    const svg = container.querySelector('svg');
    expect(svg).toBeInTheDocument();
    expect(svg).toHaveClass('success');
    expect(svg).not.toHaveClass('error');

    expect(input).toHaveClass('valid');
    expect(input).not.toHaveClass('invalid');
    expect(button).toBeEnabled();
  });

  it('displays a red x icon and disables button when an incorrect IPv4 address is provided', () => {
    const { container } = render(<IpInputField />);
    const input = screen.getByPlaceholderText('IP address');
    const button = screen.getByRole('button', { name: /send/i });

    fireEvent.change(input, { target: { value: '256.256.256.256' } });

    const svg = container.querySelector('svg');
    expect(svg).toBeInTheDocument();
    expect(svg).toHaveClass('error');
    expect(svg).not.toHaveClass('success');

    expect(input).toHaveClass('invalid');
    expect(input).not.toHaveClass('valid');
    expect(button).toBeDisabled();
  });

  it('displays a green checkmark icon when a correct IPv6 address is provided', () => {
    const { container } = render(<IpInputField />);
    const input = screen.getByPlaceholderText('IP address');

    fireEvent.change(input, { target: { value: '2001:0db8:85a3:0000:0000:8a2e:0370:7334' } });

    const svg = container.querySelector('svg');
    expect(svg).toBeInTheDocument();
    expect(svg).toHaveClass('success');
  });

  it('displays a red x icon when an incorrect IPv6 address is provided', () => {
    const { container } = render(<IpInputField />);
    const input = screen.getByPlaceholderText('IP address');

    fireEvent.change(input, { target: { value: '2001:0db8:85a3:000z::1' } });

    const svg = container.querySelector('svg');
    expect(svg).toBeInTheDocument();
    expect(svg).toHaveClass('error');
  });

  it('removes the invalid class when the input is cleared after being touched', () => {
    render(<IpInputField />);
    const input = screen.getByPlaceholderText('IP address');

    // Type something to make it touched and invalid
    fireEvent.change(input, { target: { value: 'a' } });
    expect(input).toHaveClass('invalid');

    // Clear the input
    fireEvent.change(input, { target: { value: '' } });
    
    // It should NO LONGER have the invalid class
    expect(input).not.toHaveClass('invalid');
    expect(input).not.toHaveClass('valid');
  });
});

describe('IpInputField Server Requests', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('shows a success popup and clears the input when the server responds with ok', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(
      new Response(JSON.stringify({ task_status: 'processing' }), { status: 202 }),
    );

    const { container } = render(<IpInputField />);
    const input = screen.getByPlaceholderText('IP address');
    fireEvent.change(input, { target: { value: '192.168.1.1' } });

    const button = screen.getByRole('button', { name: /send/i });
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText('IP address check started successfully.')).toBeInTheDocument();
    });

    expect(input).toHaveValue('');
    const iconContainer = container.querySelector('.icon-container');
    expect(iconContainer?.children.length).toBe(0);
  });

  it('shows an error popup when the server responds with a non-ok status', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(
      new Response(JSON.stringify({ detail: 'Invalid IP address.' }), { status: 422 }),
    );

    render(<IpInputField />);
    const input = screen.getByPlaceholderText('IP address');
    fireEvent.change(input, { target: { value: '10.0.0.1' } });

    const button = screen.getByRole('button', { name: /send/i });
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText('Invalid IP address.')).toBeInTheDocument();
    });
  });

  it('shows a network error popup when the fetch call rejects', async () => {
    vi.spyOn(globalThis, 'fetch').mockRejectedValueOnce(new Error('Network Error'));

    render(<IpInputField />);
    const input = screen.getByPlaceholderText('IP address');
    fireEvent.change(input, { target: { value: '10.0.0.1' } });

    const button = screen.getByRole('button', { name: /send/i });
    fireEvent.click(button);

    await waitFor(() => {
      expect(
        screen.getByText('Could not reach the server. Please try again.'),
      ).toBeInTheDocument();
    });
  });

  it('does not call fetch when the IP address is invalid', () => {
    const fetchSpy = vi.spyOn(globalThis, 'fetch');

    render(<IpInputField />);
    const input = screen.getByPlaceholderText('IP address');
    fireEvent.change(input, { target: { value: '999.999.999.999' } });

    const button = screen.getByRole('button', { name: /send/i });
    // Button is disabled — clicking it should not trigger fetch
    fireEvent.click(button);

    expect(fetchSpy).not.toHaveBeenCalled();
  });

  it('submits the form when Enter key is pressed in the input field', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(
      new Response(JSON.stringify({ task_status: 'processing' }), { status: 202 }),
    );

    render(<IpInputField />);
    const input = screen.getByPlaceholderText('IP address');
    fireEvent.change(input, { target: { value: '192.168.1.1' } });

    // Simulate pressing Enter on the input
    fireEvent.submit(input);

    await waitFor(() => {
      expect(screen.getByText('IP address check started successfully.')).toBeInTheDocument();
    });
  });
});

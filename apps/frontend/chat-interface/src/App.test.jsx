import { render, screen } from '@testing-library/react';
import App from './App';
import '@testing-library/jest-dom';

describe('App', () => {
  test('renders App component', () => {
    render(<App />);
    expect(screen.getByText(/Chat Integration App/i)).toBeInTheDocument();
  });
});



import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import CodeViewer from './CodeViewer';

describe('CodeViewer', () => {
  const mockCode = `import os
def main():
    print("Hello World")`;

  it('renders code content', () => {
    render(<CodeViewer code={mockCode} language="python" />);
    
    expect(screen.getByText('import os')).toBeInTheDocument();
    expect(screen.getByText('def main():')).toBeInTheDocument();
    expect(screen.getByText('print("Hello World")')).toBeInTheDocument();
  });

  it('renders line numbers', () => {
    render(<CodeViewer code={mockCode} language="python" />);
    
    expect(screen.getByText('1')).toBeInTheDocument();
    expect(screen.getByText('2')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument();
  });

  it('displays the language', () => {
    render(<CodeViewer code={mockCode} language="python" />);
    expect(screen.getByText('python')).toBeInTheDocument();
  });

  it('highlights specific lines', () => {
    const highlights = [
      { line: 2, type: 'foreground' as const, message: 'Test Highlight' }
    ];
    
    render(<CodeViewer code={mockCode} language="python" highlights={highlights} />);
    
    // Find the line content 'def main():'
    const lineContent = screen.getByText('def main():');
    const row = lineContent.closest('div')?.parentElement as HTMLElement | null;
    expect(row).not.toBeNull();
    
    // Check for highlight class
    expect(row).toHaveClass('bg-emerald-500/10');
    
    // Check for tooltip message (it's in the DOM but might be hidden/opacity 0)
    expect(screen.getByText('Test Highlight')).toBeInTheDocument();
  });
});

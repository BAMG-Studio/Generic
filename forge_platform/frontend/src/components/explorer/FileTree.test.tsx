import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import FileTree from './FileTree';

describe('FileTree', () => {
  const mockOnSelectFile = vi.fn();

  it('renders the file tree structure', () => {
    render(<FileTree onSelectFile={mockOnSelectFile} selectedFileId={null} />);
    
    expect(screen.getByText('Explorer')).toBeInTheDocument();
    expect(screen.getByText('forge-trace-core')).toBeInTheDocument();
    expect(screen.getByText('src')).toBeInTheDocument();
    expect(screen.getByText('lib')).toBeInTheDocument();
  });

  it('expands folders when clicked', () => {
    render(<FileTree onSelectFile={mockOnSelectFile} selectedFileId={null} />);
    
    // 'src' should be visible initially (based on mock data structure implementation)
    const srcFolder = screen.getByText('src');
    expect(srcFolder).toBeInTheDocument();
    
    // Children are expanded by default, then collapse and re-expand
    expect(screen.getByText('engine')).toBeInTheDocument();
    
    fireEvent.click(srcFolder);
    expect(screen.queryByText('engine')).not.toBeInTheDocument();

    fireEvent.click(srcFolder);
    expect(screen.getByText('engine')).toBeInTheDocument();
  });

  it('calls onSelectFile when a file is clicked', () => {
    render(<FileTree onSelectFile={mockOnSelectFile} selectedFileId={null} />);
    
    // 'gpl_snippet.c' is a file in 'lib' folder which is at root level
    const file = screen.getByText('gpl_snippet.c');
    fireEvent.click(file);
    
    expect(mockOnSelectFile).toHaveBeenCalledWith('f4');
  });

  it('highlights the selected file', () => {
    render(<FileTree onSelectFile={mockOnSelectFile} selectedFileId="f4" />);
    
    const file = screen.getByText('gpl_snippet.c');
    // The parent div has the highlight class. 
    // We can check if the element or its parent has the class.
    // In the component: className={clsx(..., isSelected && "bg-brand/10 border-l-2 border-brand")}
    
    // We can look for the class on the container.
    // The text is inside a span, inside a div.
    const row = file.closest('div');
    expect(row).toHaveClass('bg-brand/10');
    expect(row).toHaveClass('border-brand');
  });
});

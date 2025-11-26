import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import IPDonutChart from './IPDonutChart';
import { ReactNode } from 'react';

// Mock Recharts since it uses SVG and can be tricky to test in JSDOM without full support
vi.mock('recharts', () => {
  const OriginalModule = vi.importActual('recharts');
  return {
    ...OriginalModule,
    ResponsiveContainer: ({ children }: { children: ReactNode }) => <div data-testid="responsive-container">{children}</div>,
    PieChart: ({ children }: { children: ReactNode }) => <div data-testid="pie-chart">{children}</div>,
    Pie: ({ data }: { data: any[] }) => (
      <div data-testid="pie">
        {data.map((entry, index) => (
          <div key={index} data-testid="pie-cell">
            {entry.name}: {entry.value}
          </div>
        ))}
      </div>
    ),
    Cell: () => <div data-testid="cell" />,
    Tooltip: () => <div data-testid="tooltip" />,
    Legend: () => <div data-testid="legend" />,
  };
});

describe('IPDonutChart', () => {
  const mockData = {
    foreground: 60,
    third_party: 30,
    background: 10,
  };

  it('renders the chart with correct data', () => {
    render(<IPDonutChart data={mockData} />);
    
    expect(screen.getByText('60%')).toBeInTheDocument();
    expect(screen.getByText('Owned')).toBeInTheDocument();
    
    // Check if mock pie cells are rendered with correct values
    expect(screen.getByText('Foreground (Proprietary): 60')).toBeInTheDocument();
    expect(screen.getByText('Third-Party (OSS): 30')).toBeInTheDocument();
    expect(screen.getByText('Background (Legacy): 10')).toBeInTheDocument();
  });
});

import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';

interface IPDonutChartProps {
  data: {
    foreground: number;
    third_party: number;
    background: number;
  };
}

const IPDonutChart: React.FC<IPDonutChartProps> = ({ data }) => {
  const chartData = [
    { name: 'Foreground (Proprietary)', value: data.foreground, color: '#10B981' }, // Emerald-500
    { name: 'Third-Party (OSS)', value: data.third_party, color: '#F59E0B' },      // Amber-500
    { name: 'Background (Legacy)', value: data.background, color: '#64748B' },     // Slate-500
  ];

  return (
    <div className="h-64 w-full relative">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={80}
            paddingAngle={5}
            dataKey="value"
            stroke="none"
          >
            {chartData.map((entry, index) => (
              <Cell 
                key={`cell-${index}`} 
                fill={entry.color} 
                className="stroke-canvas-panel stroke-2"
              />
            ))}
          </Pie>
          <Tooltip 
            contentStyle={{ 
              backgroundColor: '#1E293B', 
              borderColor: '#334155',
              borderRadius: '0.5rem',
              color: '#F8FAFC'
            }}
            itemStyle={{ color: '#E2E8F0' }}
          />
          <Legend 
            verticalAlign="bottom" 
            height={36}
            iconType="circle"
            formatter={(value) => <span className="text-slate-300 text-sm ml-1">{value}</span>}
          />
        </PieChart>
      </ResponsiveContainer>
      
      {/* Center Text */}
      <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none pb-8">
        <span className="text-3xl font-bold text-white">{data.foreground}%</span>
        <span className="text-xs text-slate-400 uppercase tracking-wider">Owned</span>
      </div>
    </div>
  );
};

export default IPDonutChart;

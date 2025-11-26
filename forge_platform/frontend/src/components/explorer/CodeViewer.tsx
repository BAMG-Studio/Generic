import React from 'react';
import clsx from 'clsx';

interface CodeViewerProps {
  code: string;
  language: string;
  highlights?: {
    line: number;
    type: 'foreground' | 'third_party' | 'background' | 'risk';
    message?: string;
  }[];
}

const CodeViewer: React.FC<CodeViewerProps> = ({ code, language, highlights = [] }) => {
  const lines = code.split('\n');

  const getHighlightClass = (type?: string) => {
    switch (type) {
      case 'foreground': return 'bg-emerald-500/10 border-l-2 border-emerald-500';
      case 'third_party': return 'bg-amber-500/10 border-l-2 border-amber-500';
      case 'background': return 'bg-slate-500/10 border-l-2 border-slate-500';
      case 'risk': return 'bg-red-500/10 border-l-2 border-red-500';
      default: return '';
    }
  };

  return (
    <div className="font-mono text-sm bg-[#0d1117] text-slate-300 overflow-auto h-full rounded-lg border border-canvas-border">
      <div className="flex border-b border-canvas-border bg-canvas-panel px-4 py-2 items-center justify-between sticky top-0 z-10">
        <span className="text-xs text-slate-400 uppercase">{language}</span>
        <div className="flex space-x-2">
          <div className="flex items-center text-xs text-emerald-400">
            <div className="w-2 h-2 bg-emerald-500 rounded-full mr-1"></div>
            Foreground
          </div>
          <div className="flex items-center text-xs text-amber-400">
            <div className="w-2 h-2 bg-amber-500 rounded-full mr-1"></div>
            3rd Party
          </div>
        </div>
      </div>
      
      <div className="py-4">
        {lines.map((line, i) => {
          const lineNumber = i + 1;
          const highlight = highlights.find(h => h.line === lineNumber);
          
          return (
            <div 
              key={i} 
              className={clsx(
                "flex hover:bg-slate-800/30 group relative",
                highlight && getHighlightClass(highlight.type)
              )}
            >
              {/* Line Number */}
              <div className="w-12 text-right pr-4 text-slate-600 select-none text-xs pt-0.5">
                {lineNumber}
              </div>
              
              {/* Code Content */}
              <div className="flex-1 pl-2 pr-4 whitespace-pre overflow-x-auto">
                {line}
              </div>

              {/* Tooltip for Highlight */}
              {highlight && highlight.message && (
                <div className="absolute right-4 top-0 bottom-0 flex items-center">
                  <span className="text-xs px-2 py-0.5 rounded bg-slate-800 border border-slate-600 text-slate-300 opacity-0 group-hover:opacity-100 transition-opacity">
                    {highlight.message}
                  </span>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default CodeViewer;

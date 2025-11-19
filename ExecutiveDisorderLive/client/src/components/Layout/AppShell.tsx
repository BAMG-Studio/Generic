import React from 'react';

interface AppShellProps {
  children: React.ReactNode;
}

export default function AppShell({ children }: AppShellProps) {
  return (
    <div className="fixed inset-0 w-screen h-screen overflow-hidden bg-black flex items-center justify-center">
      {/* Responsive container that scales to fit viewport while maintaining 16:9 ratio */}
      <div 
        className="relative w-full h-full max-w-screen-2xl"
        style={{
          aspectRatio: '16 / 9',
          maxWidth: 'min(100vw, calc(100vh * 16 / 9))',
          maxHeight: 'min(100vh, calc(100vw * 9 / 16))'
        }}
      >
        {/* Game content */}
        <div className="absolute inset-0 overflow-hidden shadow-2xl">
          {children}
        </div>
      </div>
    </div>
  );
}

import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  FileCode, 
  CheckSquare, 
  Settings, 
  Menu, 
  X,
  ShieldAlert
} from 'lucide-react';
import clsx from 'clsx';

interface AppLayoutProps {
  children: React.ReactNode;
}

const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const location = useLocation();

  const navItems = [
    { name: 'Mission Control', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Code DNA', path: '/explorer', icon: FileCode },
    { name: 'Review Queue', path: '/review', icon: CheckSquare },
    { name: 'Settings', path: '/settings', icon: Settings },
  ];

  return (
    <div className="flex h-screen bg-canvas text-slate-200 font-sans overflow-hidden">
      {/* Sidebar */}
      <aside 
        className={clsx(
          "bg-canvas-panel border-r border-canvas-border transition-all duration-300 flex flex-col",
          isSidebarOpen ? "w-64" : "w-20"
        )}
      >
        <div className="h-16 flex items-center justify-between px-4 border-b border-canvas-border">
          {isSidebarOpen && (
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-brand rounded-lg flex items-center justify-center shadow-neon">
                <ShieldAlert className="w-5 h-5 text-white" />
              </div>
              <span className="font-bold text-lg tracking-tight text-white">ForgeTrace</span>
            </div>
          )}
          <button 
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            className="p-2 hover:bg-slate-700 rounded-md transition-colors"
          >
            {isSidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>

        <nav className="flex-1 py-6 space-y-2 px-3">
          {navItems.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={clsx(
                  "flex items-center px-3 py-3 rounded-lg transition-all duration-200 group",
                  isActive 
                    ? "bg-brand/10 text-brand border border-brand/20 shadow-[0_0_15px_rgba(99,102,241,0.15)]" 
                    : "text-slate-400 hover:bg-slate-800 hover:text-slate-100"
                )}
              >
                <item.icon 
                  size={22} 
                  className={clsx(
                    "transition-colors",
                    isActive ? "text-brand" : "text-slate-400 group-hover:text-slate-100"
                  )} 
                />
                {isSidebarOpen && (
                  <span className="ml-3 font-medium">{item.name}</span>
                )}
              </Link>
            );
          })}
        </nav>

        <div className="p-4 border-t border-canvas-border">
          {isSidebarOpen ? (
            <div className="bg-slate-900/50 rounded-lg p-3 border border-slate-700">
              <div className="text-xs text-slate-500 uppercase font-bold mb-1">Current Repo</div>
              <div className="text-sm font-mono text-emerald-400 truncate">forge-trace-core</div>
              <div className="text-xs text-slate-400 mt-1 flex items-center">
                <span className="w-2 h-2 bg-emerald-500 rounded-full mr-2 animate-pulse"></span>
                Online
              </div>
            </div>
          ) : (
            <div className="flex justify-center">
              <div className="w-3 h-3 bg-emerald-500 rounded-full shadow-[0_0_8px_#10B981]"></div>
            </div>
          )}
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top Bar */}
        <header className="h-16 bg-canvas/50 backdrop-blur-md border-b border-canvas-border flex items-center justify-between px-6 z-10">
          <div className="flex items-center space-x-4">
            <h1 className="text-xl font-semibold text-white">
              {navItems.find(i => i.path === location.pathname)?.name || 'Dashboard'}
            </h1>
          </div>
          <div className="flex items-center space-x-4">
            <div className="px-3 py-1 rounded-full bg-slate-800 border border-slate-700 text-xs font-mono text-slate-400">
              v1.2.0-beta
            </div>
            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-brand to-purple-500 border border-white/10"></div>
          </div>
        </header>

        {/* Scrollable Content Area */}
        <div className="flex-1 overflow-y-auto p-6 bg-canvas relative">
          {/* Grid Background Effect */}
          <div className="absolute inset-0 bg-[linear-gradient(to_right,#1e293b_1px,transparent_1px),linear-gradient(to_bottom,#1e293b_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] pointer-events-none opacity-20"></div>
          
          <div className="relative z-10 max-w-7xl mx-auto">
            {children}
          </div>
        </div>
      </main>
    </div>
  );
};

export default AppLayout;

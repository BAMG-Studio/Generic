import React from 'react';
import { 
  DollarSign, 
  Activity,
  GitCommit,
  Shield,
  FileText
} from 'lucide-react';
import IPDonutChart from '../components/dashboard/IPDonutChart';
import { MOCK_REPO_STATS } from '../api/mock_data';

const StatCard: React.FC<{
  title: string;
  value: string | number;
  icon: React.ElementType;
  trend?: string;
  trendUp?: boolean;
  color?: string;
}> = ({ title, value, icon: Icon, trend, trendUp, color = "text-slate-400" }) => (
  <div className="bg-canvas-panel border border-canvas-border rounded-xl p-5 shadow-sm hover:shadow-md transition-shadow">
    <div className="flex justify-between items-start mb-4">
      <div>
        <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">{title}</p>
        <h3 className="text-2xl font-bold text-white mt-1">{value}</h3>
      </div>
      <div className={`p-2 rounded-lg bg-slate-800/50 ${color}`}>
        <Icon size={20} />
      </div>
    </div>
    {trend && (
      <div className="flex items-center text-xs">
        <span className={trendUp ? "text-emerald-400" : "text-rose-400"}>
          {trendUp ? "+" : "-"}{trend}
        </span>
        <span className="text-slate-500 ml-2">vs last scan</span>
      </div>
    )}
  </div>
);

const Dashboard: React.FC = () => {
  return (
    <div className="space-y-6">
      {/* Header Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard 
          title="Risk Score" 
          value={MOCK_REPO_STATS.overall_risk} 
          icon={Shield} 
          color="text-amber-400"
        />
        <StatCard 
          title="Rewrite Cost" 
          value={MOCK_REPO_STATS.rewrite_cost_estimate} 
          icon={DollarSign} 
          color="text-emerald-400"
          trend="12%"
          trendUp={false}
        />
        <StatCard 
          title="Total Files" 
          value={MOCK_REPO_STATS.total_files} 
          icon={FileText} 
          color="text-brand"
        />
        <StatCard 
          title="Active Scans" 
          value="3" 
          icon={Activity} 
          color="text-blue-400"
          trend="Running"
          trendUp={true}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* IP Ownership Chart */}
        <div className="lg:col-span-1 bg-canvas-panel border border-canvas-border rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-6 flex items-center">
            <span className="w-1 h-6 bg-brand rounded-full mr-3"></span>
            IP Ownership Split
          </h3>
          <IPDonutChart data={MOCK_REPO_STATS.ip_split} />
          
          <div className="mt-6 space-y-3">
            <div className="flex justify-between items-center text-sm">
              <div className="flex items-center text-slate-400">
                <div className="w-3 h-3 rounded-full bg-emerald-500 mr-2"></div>
                Foreground (Proprietary)
              </div>
              <span className="text-white font-mono">{MOCK_REPO_STATS.ip_split.foreground}%</span>
            </div>
            <div className="flex justify-between items-center text-sm">
              <div className="flex items-center text-slate-400">
                <div className="w-3 h-3 rounded-full bg-amber-500 mr-2"></div>
                Third-Party (OSS)
              </div>
              <span className="text-white font-mono">{MOCK_REPO_STATS.ip_split.third_party}%</span>
            </div>
            <div className="flex justify-between items-center text-sm">
              <div className="flex items-center text-slate-400">
                <div className="w-3 h-3 rounded-full bg-slate-500 mr-2"></div>
                Background (Legacy)
              </div>
              <span className="text-white font-mono">{MOCK_REPO_STATS.ip_split.background}%</span>
            </div>
          </div>
        </div>

        {/* Recent Activity / Trends */}
        <div className="lg:col-span-2 bg-canvas-panel border border-canvas-border rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-6 flex items-center">
            <span className="w-1 h-6 bg-emerald-500 rounded-full mr-3"></span>
            Recent Activity
          </h3>
          
          <div className="space-y-4">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="flex items-center justify-between p-4 rounded-lg bg-slate-800/30 border border-slate-700/50 hover:border-slate-600 transition-colors">
                <div className="flex items-center space-x-4">
                  <div className="p-2 rounded-full bg-slate-800 text-slate-400">
                    <GitCommit size={18} />
                  </div>
                  <div>
                    <div className="text-sm font-medium text-slate-200">
                      Scan triggered by <span className="text-brand font-mono">commit 8a2b9c</span>
                    </div>
                    <div className="text-xs text-slate-500">
                      2 hours ago • branch: <span className="text-slate-400">feature/auth-v2</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="text-right">
                    <div className="text-xs text-slate-500">New IP Detected</div>
                    <div className="text-sm font-mono text-emerald-400">+12 Files</div>
                  </div>
                  <div className="h-2 w-2 rounded-full bg-emerald-500"></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

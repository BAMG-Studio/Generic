import React, { useState } from 'react';
import { useAuditStore } from '../store/useAuditStore';
import { Sliders, Database, Github } from 'lucide-react';

const Settings: React.FC = () => {
  const { confidenceThreshold, setConfidenceThreshold } = useAuditStore();
  const [localThreshold, setLocalThreshold] = useState(confidenceThreshold * 100);

  const handleThresholdChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = parseInt(e.target.value);
    setLocalThreshold(val);
    setConfidenceThreshold(val / 100);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-white mb-2">Settings & Policy</h2>
        <p className="text-slate-400">Configure the ForgeTrace analysis engine and integration parameters.</p>
      </div>

      {/* ML Thresholds */}
      <div className="bg-canvas-panel border border-canvas-border rounded-xl p-6">
        <div className="flex items-center space-x-3 mb-6">
          <div className="p-2 bg-brand/10 rounded-lg text-brand">
            <Sliders size={20} />
          </div>
          <h3 className="text-lg font-semibold text-white">Analysis Thresholds</h3>
        </div>

        <div className="space-y-8">
          <div>
            <div className="flex justify-between mb-2">
              <label className="text-sm font-medium text-slate-300">Confidence Threshold</label>
              <span className="text-sm font-mono text-brand">{localThreshold}%</span>
            </div>
            <input 
              type="range" 
              min="50" 
              max="99" 
              value={localThreshold} 
              onChange={handleThresholdChange}
              className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-brand"
            />
            <p className="text-xs text-slate-500 mt-2">
              Predictions below this confidence level will automatically be sent to the Review Queue.
              Lowering this value increases automation but may increase false positives.
            </p>
          </div>

          <div className="p-4 bg-slate-800/50 rounded-lg border border-slate-700">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm font-medium text-white">Strict License Enforcement</div>
                <div className="text-xs text-slate-400">Automatically flag any GPL-family licenses as High Risk</div>
              </div>
              <div className="relative inline-block w-12 h-6 transition duration-200 ease-in-out rounded-full cursor-pointer bg-brand">
                <span className="absolute left-0 inline-block w-6 h-6 bg-white border border-gray-300 rounded-full shadow transform translate-x-6 transition-transform duration-200 ease-in-out"></span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Integrations */}
      <div className="bg-canvas-panel border border-canvas-border rounded-xl p-6">
        <div className="flex items-center space-x-3 mb-6">
          <div className="p-2 bg-blue-500/10 rounded-lg text-blue-500">
            <Database size={20} />
          </div>
          <h3 className="text-lg font-semibold text-white">Integrations</h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 border border-slate-700 rounded-lg bg-slate-800/30 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Github size={24} className="text-white" />
              <div>
                <div className="text-sm font-medium text-white">GitHub Enterprise</div>
                <div className="text-xs text-emerald-400 flex items-center">
                  <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full mr-1.5"></span>
                  Connected
                </div>
              </div>
            </div>
            <button className="text-xs text-slate-400 hover:text-white border border-slate-600 px-3 py-1 rounded">Configure</button>
          </div>

          <div className="p-4 border border-slate-700 rounded-lg bg-slate-800/30 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-6 h-6 bg-blue-500 rounded flex items-center justify-center text-xs font-bold text-white">ML</div>
              <div>
                <div className="text-sm font-medium text-white">MLflow Registry</div>
                <div className="text-xs text-emerald-400 flex items-center">
                  <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full mr-1.5"></span>
                  v2.1.0 Active
                </div>
              </div>
            </div>
            <button className="text-xs text-slate-400 hover:text-white border border-slate-600 px-3 py-1 rounded">Manage</button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;

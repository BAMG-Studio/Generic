import React, { useState } from 'react';
import { useAuditStore } from '../store/useAuditStore';
import { Sliders, Database, Github, Shield, HardDrive } from 'lucide-react';
import { Card, CardHeader, CardContent, Badge, Button } from '../components/ui';

const Settings: React.FC = () => {
  const { confidenceThreshold, setConfidenceThreshold } = useAuditStore();
  const [localThreshold, setLocalThreshold] = useState(confidenceThreshold * 100);

  const handleThresholdChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = parseInt(e.target.value);
    setLocalThreshold(val);
    setConfidenceThreshold(val / 100);
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-white mb-2">Settings & Policy</h2>
        <p className="text-slate-400">Configure the ForgeTrace analysis engine and integration parameters.</p>
      </div>

      {/* Analysis Thresholds Card */}
      <Card>
        <CardHeader 
          icon={<Sliders size={20} />}
          title="Analysis Thresholds"
          description="Configure confidence levels and automated decision boundaries"
        />
        <CardContent>
          <div>
            <div className="flex justify-between items-center mb-3">
              <div>
                <label className="text-sm font-medium text-slate-300 block">Confidence Threshold</label>
                <p className="text-xs text-slate-500 mt-1">
                  Predictions below this level are sent to Review Queue
                </p>
              </div>
              <span className="text-lg font-mono font-bold text-brand">{localThreshold}%</span>
            </div>
            <input 
              type="range" 
              min="50" 
              max="99" 
              value={localThreshold} 
              onChange={handleThresholdChange}
              className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-brand hover:accent-brand-light transition-colors"
              aria-label="Confidence threshold slider"
            />
            <div className="flex justify-between text-xs text-slate-600 mt-1">
              <span>50% (More automation)</span>
              <span>99% (Higher precision)</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Policy Enforcement Card */}
      <Card>
        <CardHeader 
          icon={<Shield size={20} />}
          title="Policy Enforcement"
          description="Automated rules for license and compliance checks"
        />
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-slate-800/30 rounded-lg border border-slate-700 hover:border-slate-600 transition-colors">
              <div className="flex-1">
                <div className="text-sm font-medium text-white mb-1">Strict License Enforcement</div>
                <div className="text-xs text-slate-400">
                  Automatically flag GPL-family licenses as High Risk
                </div>
              </div>
              <div className="relative inline-block w-12 h-6 transition duration-200 ease-in-out rounded-full cursor-pointer bg-brand">
                <span className="absolute left-0 inline-block w-6 h-6 bg-white border border-gray-300 rounded-full shadow transform translate-x-6 transition-transform duration-200 ease-in-out"></span>
              </div>
            </div>

            <div className="flex items-center justify-between p-4 bg-slate-800/30 rounded-lg border border-slate-700">
              <div className="flex-1">
                <div className="text-sm font-medium text-white mb-1">Auto-approve Low Risk</div>
                <div className="text-xs text-slate-400">
                  Skip manual review for files with &gt;95% confidence and permissive licenses
                </div>
              </div>
              <div className="relative inline-block w-12 h-6 transition duration-200 ease-in-out rounded-full cursor-pointer bg-slate-600">
                <span className="absolute left-0 inline-block w-6 h-6 bg-white border border-gray-300 rounded-full shadow transition-transform duration-200 ease-in-out"></span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Integrations Card */}
      <Card>
        <CardHeader 
          icon={<Database size={20} />}
          title="Integrations"
          description="Connect ForgeTrace to your development tools and platforms"
        />
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 border border-slate-700 rounded-lg bg-slate-800/30 hover:border-slate-600 transition-colors">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-3">
                  <Github size={24} className="text-white" />
                  <div>
                    <div className="text-sm font-medium text-white">GitHub Enterprise</div>
                    <Badge variant="success" dot className="mt-1">Connected</Badge>
                  </div>
                </div>
              </div>
              <Button variant="secondary" size="sm" className="w-full">Configure</Button>
            </div>

            <div className="p-4 border border-slate-700 rounded-lg bg-slate-800/30 hover:border-slate-600 transition-colors">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-3">
                  <div className="w-6 h-6 bg-blue-500 rounded flex items-center justify-center text-xs font-bold text-white">ML</div>
                  <div>
                    <div className="text-sm font-medium text-white">MLflow Registry</div>
                    <Badge variant="success" dot className="mt-1">v2.1.0 Active</Badge>
                  </div>
                </div>
              </div>
              <Button variant="secondary" size="sm" className="w-full">Manage</Button>
            </div>

            <div className="p-4 border border-dashed border-slate-700 rounded-lg bg-slate-800/10 hover:border-slate-600 transition-colors flex items-center justify-center">
              <Button variant="ghost" size="sm">+ Add Integration</Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Data Retention Card */}
      <Card>
        <CardHeader 
          icon={<HardDrive size={20} />}
          title="Data & Storage"
          description="Manage audit history and retention policies"
        />
        <CardContent>
          <div className="space-y-4">
            <div className="flex justify-between items-center p-4 bg-slate-800/30 rounded-lg border border-slate-700">
              <div>
                <div className="text-sm font-medium text-white">Audit History Retention</div>
                <div className="text-xs text-slate-400 mt-1">Keep audit reports for 90 days</div>
              </div>
              <select className="bg-slate-700 border border-slate-600 rounded px-3 py-1.5 text-sm text-white focus:ring-2 focus:ring-brand focus:outline-none">
                <option>30 days</option>
                <option selected>90 days</option>
                <option>180 days</option>
                <option>1 year</option>
                <option>Forever</option>
              </select>
            </div>

            <div className="flex justify-between items-center p-4 bg-slate-800/30 rounded-lg border border-slate-700">
              <div>
                <div className="text-sm font-medium text-white">Storage Used</div>
                <div className="text-xs text-slate-400 mt-1">Across all audits and artifacts</div>
              </div>
              <div className="text-right">
                <div className="text-sm font-mono text-brand">4.2 GB</div>
                <div className="text-xs text-slate-500">of 100 GB</div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Settings;

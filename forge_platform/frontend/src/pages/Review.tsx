import React from 'react';
import { Check, X, AlertCircle } from 'lucide-react';
import { MOCK_FILES } from '../api/mock_data';

const Review: React.FC = () => {
  // Filter for low confidence files
  const reviewQueue = MOCK_FILES.filter(f => f.confidence < 0.8 || f.risk_score > 20);

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-white mb-2">Review Queue</h2>
        <p className="text-slate-400">
          ForgeTrace has flagged {reviewQueue.length} files for human verification due to low confidence or high risk.
        </p>
      </div>

      <div className="space-y-4">
        {reviewQueue.map((file) => (
          <div key={file.id} className="bg-canvas-panel border border-canvas-border rounded-xl p-6 flex items-center justify-between group hover:border-slate-600 transition-colors">
            <div className="flex-1">
              <div className="flex items-center space-x-3 mb-2">
                <h3 className="text-lg font-mono font-medium text-white">{file.name}</h3>
                <span className="px-2 py-0.5 rounded text-xs font-medium bg-slate-800 text-slate-400 border border-slate-700">
                  {file.path}
                </span>
              </div>
              
              <div className="flex items-center space-x-6 text-sm">
                <div className="flex items-center space-x-2">
                  <span className="text-slate-500">ForgeTrace Prediction:</span>
                  <span className={`font-medium ${
                    file.classification === 'foreground' ? 'text-emerald-400' :
                    file.classification === 'third_party' ? 'text-amber-400' : 'text-slate-400'
                  }`}>
                    {file.classification.replace('_', ' ').toUpperCase()}
                  </span>
                </div>
                
                <div className="flex items-center space-x-2">
                  <span className="text-slate-500">Confidence:</span>
                  <span className={`font-mono ${file.confidence < 0.7 ? 'text-rose-400' : 'text-slate-300'}`}>
                    {Math.round(file.confidence * 100)}%
                  </span>
                </div>

                {file.risk_score > 0 && (
                  <div className="flex items-center space-x-1 text-rose-400">
                    <AlertCircle size={14} />
                    <span>Risk Score: {file.risk_score}</span>
                  </div>
                )}
              </div>
            </div>

            <div className="flex items-center space-x-3 pl-6 border-l border-slate-700">
              <button className="p-2 rounded-lg bg-slate-800 hover:bg-rose-500/20 hover:text-rose-400 text-slate-400 transition-colors" title="Reject / Reclassify">
                <X size={20} />
              </button>
              <button className="p-2 rounded-lg bg-slate-800 hover:bg-emerald-500/20 hover:text-emerald-400 text-slate-400 transition-colors" title="Confirm Prediction">
                <Check size={20} />
              </button>
            </div>
          </div>
        ))}

        {reviewQueue.length === 0 && (
          <div className="text-center py-20 bg-canvas-panel border border-canvas-border rounded-xl border-dashed">
            <div className="w-16 h-16 bg-emerald-500/10 rounded-full flex items-center justify-center mx-auto mb-4">
              <Check size={32} className="text-emerald-500" />
            </div>
            <h3 className="text-xl font-medium text-white">All Caught Up!</h3>
            <p className="text-slate-400 mt-2">No files currently require manual review.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Review;

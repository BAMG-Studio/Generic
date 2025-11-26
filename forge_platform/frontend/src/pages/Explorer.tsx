import React, { useState } from 'react';
import FileTree from '../components/explorer/FileTree';
import CodeViewer from '../components/explorer/CodeViewer';
import { MOCK_FILES } from '../api/mock_data';
import { AlertTriangle, Info } from 'lucide-react';
import clsx from 'clsx';

const Explorer: React.FC = () => {
  const [selectedFileId, setSelectedFileId] = useState<string | null>('f1');

  const selectedFile = MOCK_FILES.find(f => f.id === selectedFileId);

  // Mock code content based on file type
  const getMockCode = (file: typeof selectedFile) => {
    if (!file) return '';
    if (file.name.endsWith('.py')) {
      return `import os
import sys
from typing import List, Dict

class Analyzer:
    """
    Core analysis engine for ForgeTrace.
    Determines IP classification based on entropy and structure.
    """
    def __init__(self, config: Dict):
        self.config = config
        self.threshold = 0.75

    def analyze_file(self, content: str) -> str:
        # Calculate entropy
        entropy = self._calculate_entropy(content)
        
        if entropy > 5.0:
            return "foreground"
        else:
            return "background"

    def _calculate_entropy(self, text: str) -> float:
        # Complex proprietary logic here
        pass
`;
    }
    if (file.name.endsWith('.js')) {
      return `/**
 * Custom Lodash build
 * License: MIT
 */
(function() {
  var root = typeof self == 'object' && self.self === self && self ||
            typeof global == 'object' && global.global === global && global ||
            this || {};

  // ... 4000 lines of library code ...
  
  function baseGet(object, path) {
    path = castPath(path, object);
    var index = 0,
        length = path.length;

    while (object != null && index < length) {
      object = object[toKey(path[index++])];
    }
    return (index && index == length) ? object : undefined;
  }
})();`;
    }
    return `// Content for ${file.name}\n// ...`;
  };

  return (
    <div className="flex h-[calc(100vh-8rem)] bg-canvas-panel border border-canvas-border rounded-xl overflow-hidden">
      {/* Left Pane: File Tree */}
      <div className="w-64 flex-shrink-0 border-r border-canvas-border bg-canvas-panel">
        <FileTree 
          onSelectFile={setSelectedFileId} 
          selectedFileId={selectedFileId} 
        />
      </div>

      {/* Middle Pane: Code Viewer */}
      <div className="flex-1 flex flex-col min-w-0">
        {selectedFile ? (
          <>
            {/* File Header */}
            <div className="h-14 border-b border-canvas-border flex items-center justify-between px-4 bg-canvas-panel">
              <div className="flex items-center space-x-3">
                <div className="font-mono text-sm text-slate-200">{selectedFile.path}</div>
                <div className={clsx(
                  "px-2 py-0.5 rounded text-xs font-medium border",
                  selectedFile.classification === 'foreground' && "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
                  selectedFile.classification === 'third_party' && "bg-amber-500/10 text-amber-400 border-amber-500/20",
                  selectedFile.classification === 'background' && "bg-slate-500/10 text-slate-400 border-slate-500/20",
                )}>
                  {selectedFile.classification.replace('_', ' ').toUpperCase()}
                </div>
              </div>
              <div className="flex items-center space-x-4 text-xs text-slate-400">
                <div>Confidence: <span className="text-white">{Math.round(selectedFile.confidence * 100)}%</span></div>
                <div>Size: <span className="text-white">{selectedFile.size_kb} KB</span></div>
              </div>
            </div>

            {/* Code Area */}
            <div className="flex-1 overflow-hidden p-0">
              <CodeViewer 
                code={getMockCode(selectedFile)} 
                language={selectedFile.name.split('.').pop() || 'text'}
                highlights={[
                  // Mock highlights
                  { line: 12, type: 'foreground', message: 'High Entropy Block' },
                  { line: 15, type: 'foreground', message: 'Custom Logic Detected' }
                ]}
              />
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center text-slate-500">
            Select a file to view analysis
          </div>
        )}
      </div>

      {/* Right Pane: ML Insights */}
      <div className="w-72 flex-shrink-0 border-l border-canvas-border bg-canvas-panel p-4 overflow-y-auto">
        <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-4">
          ML Insights
        </h3>

        {selectedFile && (
          <div className="space-y-6">
            {/* Classification Score */}
            <div>
              <div className="text-xs text-slate-500 mb-1">Classification Confidence</div>
              <div className="flex items-end space-x-2">
                <span className="text-3xl font-bold text-white">
                  {Math.round(selectedFile.confidence * 100)}%
                </span>
                <span className="text-sm text-slate-400 mb-1">certainty</span>
              </div>
              <div className="w-full bg-slate-700 h-1.5 rounded-full mt-2 overflow-hidden">
                <div 
                  className="h-full bg-brand" 
                  style={{ width: `${selectedFile.confidence * 100}%` }}
                ></div>
              </div>
            </div>

            {/* Feature Contribution */}
            <div>
              <div className="text-xs text-slate-500 mb-3">Feature Contribution</div>
              <div className="space-y-3">
                <div className="flex justify-between items-center text-sm">
                  <span className="text-slate-300">Language Entropy</span>
                  <span className="font-mono text-emerald-400">{selectedFile.features.language_entropy}</span>
                </div>
                <div className="w-full bg-slate-700 h-1 rounded-full">
                  <div className="h-full bg-emerald-500" style={{ width: '80%' }}></div>
                </div>

                <div className="flex justify-between items-center text-sm">
                  <span className="text-slate-300">Template Indicator</span>
                  <span className="font-mono text-blue-400">{selectedFile.features.template_indicator}</span>
                </div>
                <div className="w-full bg-slate-700 h-1 rounded-full">
                  <div className="h-full bg-blue-500" style={{ width: '20%' }}></div>
                </div>
              </div>
            </div>

            {/* License Info */}
            <div className="p-3 rounded-lg bg-slate-800/50 border border-slate-700">
              <div className="flex items-center space-x-2 mb-2">
                <Info size={16} className="text-slate-400" />
                <span className="text-sm font-medium text-slate-200">License Detected</span>
              </div>
              <div className="text-lg font-mono text-white">
                {selectedFile.license || 'None'}
              </div>
            </div>

            {/* Risk Assessment */}
            {selectedFile.risk_score > 0 && (
              <div className={clsx(
                "p-3 rounded-lg border",
                selectedFile.risk_score > 50 
                  ? "bg-red-500/10 border-red-500/30" 
                  : "bg-amber-500/10 border-amber-500/30"
              )}>
                <div className="flex items-center space-x-2 mb-1">
                  <AlertTriangle size={16} className={selectedFile.risk_score > 50 ? "text-red-400" : "text-amber-400"} />
                  <span className={clsx("text-sm font-medium", selectedFile.risk_score > 50 ? "text-red-400" : "text-amber-400")}>
                    Risk Detected
                  </span>
                </div>
                <p className="text-xs text-slate-400 mt-1">
                  This file contains patterns associated with restrictive licensing or known vulnerabilities.
                </p>
              </div>
            )}

            {/* Actions */}
            <div className="pt-4 border-t border-slate-700">
              <button className="w-full py-2 px-4 bg-slate-700 hover:bg-slate-600 text-slate-200 rounded-lg text-sm font-medium transition-colors mb-2">
                Override Classification
              </button>
              <button className="w-full py-2 px-4 bg-transparent border border-slate-600 hover:border-slate-500 text-slate-400 hover:text-slate-300 rounded-lg text-sm font-medium transition-colors">
                View Raw Analysis
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Explorer;

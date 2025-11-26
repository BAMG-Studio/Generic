import React, { useState } from 'react';
import { Folder, FileText, ChevronRight, ChevronDown, AlertTriangle } from 'lucide-react';
import clsx from 'clsx';
import { AuditFile } from '../../api/mock_data';

// Mock tree structure for demonstration
// In a real app, you'd parse the flat file list into a tree
interface TreeNode {
  id: string;
  name: string;
  type: 'folder' | 'file';
  children?: TreeNode[];
  fileData?: AuditFile;
  classification?: 'foreground' | 'third_party' | 'background';
}

const MOCK_TREE: TreeNode = {
  id: 'root',
  name: 'forge-trace-core',
  type: 'folder',
  children: [
    {
      id: 'src',
      name: 'src',
      type: 'folder',
      classification: 'foreground',
      children: [
        {
          id: 'engine',
          name: 'engine',
          type: 'folder',
          classification: 'foreground',
          children: [
            { id: 'f1', name: 'analyzer.py', type: 'file', classification: 'foreground' }
          ]
        },
        {
          id: 'utils',
          name: 'utils',
          type: 'folder',
          classification: 'third_party',
          children: [
            { id: 'f2', name: 'lodash_custom.js', type: 'file', classification: 'third_party' }
          ]
        },
        {
          id: 'legacy',
          name: 'legacy',
          type: 'folder',
          classification: 'background',
          children: [
            { id: 'f3', name: 'payment_gateway_v1.php', type: 'file', classification: 'background' }
          ]
        }
      ]
    },
    {
      id: 'lib',
      name: 'lib',
      type: 'folder',
      classification: 'third_party',
      children: [
        { id: 'f4', name: 'gpl_snippet.c', type: 'file', classification: 'third_party' }
      ]
    }
  ]
};

interface FileTreeProps {
  onSelectFile: (fileId: string) => void;
  selectedFileId: string | null;
}

const FileTreeNode: React.FC<{ 
  node: TreeNode; 
  level: number; 
  onSelect: (id: string) => void;
  selectedId: string | null;
}> = ({ node, level, onSelect, selectedId }) => {
  const [isOpen, setIsOpen] = useState(true);

  const getIconColor = (classification?: string) => {
    switch (classification) {
      case 'foreground': return 'text-emerald-500';
      case 'third_party': return 'text-amber-500';
      case 'background': return 'text-slate-500';
      default: return 'text-slate-400';
    }
  };

  const isSelected = node.id === selectedId;

  return (
    <div>
      <div 
        className={clsx(
          "flex items-center py-1 px-2 cursor-pointer hover:bg-slate-800/50 transition-colors select-none",
          isSelected && "bg-brand/10 border-l-2 border-brand"
        )}
        style={{ paddingLeft: `${level * 12 + 8}px` }}
        onClick={() => {
          if (node.type === 'folder') setIsOpen(!isOpen);
          else onSelect(node.id);
        }}
      >
        <span className="mr-1 text-slate-500">
          {node.type === 'folder' && (
            isOpen ? <ChevronDown size={14} /> : <ChevronRight size={14} />
          )}
          {node.type === 'file' && <span className="w-3.5" />} {/* Spacer */}
        </span>
        
        <span className={clsx("mr-2", getIconColor(node.classification))}>
          {node.type === 'folder' ? <Folder size={16} /> : <FileText size={16} />}
        </span>
        
        <span className={clsx(
          "text-sm truncate",
          isSelected ? "text-white font-medium" : "text-slate-400"
        )}>
          {node.name}
        </span>

        {/* Risk Indicator */}
        {node.name === 'gpl_snippet.c' && (
          <AlertTriangle size={12} className="ml-auto text-red-500" />
        )}
      </div>

      {node.type === 'folder' && isOpen && node.children && (
        <div>
          {node.children.map(child => (
            <FileTreeNode 
              key={child.id} 
              node={child} 
              level={level + 1} 
              onSelect={onSelect}
              selectedId={selectedId}
            />
          ))}
        </div>
      )}
    </div>
  );
};

const FileTree: React.FC<FileTreeProps> = ({ onSelectFile, selectedFileId }) => {
  return (
    <div className="h-full overflow-y-auto bg-canvas-panel border-r border-canvas-border py-2">
      <div className="px-4 py-2 text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">
        Explorer
      </div>
      <FileTreeNode 
        node={MOCK_TREE} 
        level={0} 
        onSelect={onSelectFile}
        selectedId={selectedFileId}
      />
    </div>
  );
};

export default FileTree;

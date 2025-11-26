import { create } from 'zustand';
import { AuditFile } from '../api/mock_data';

interface AuditState {
  selectedFile: AuditFile | null;
  confidenceThreshold: number;
  filterClassification: 'all' | 'foreground' | 'third_party' | 'background';
  
  setSelectedFile: (file: AuditFile | null) => void;
  setConfidenceThreshold: (threshold: number) => void;
  setFilterClassification: (classification: 'all' | 'foreground' | 'third_party' | 'background') => void;
}

export const useAuditStore = create<AuditState>((set) => ({
  selectedFile: null,
  confidenceThreshold: 0.7,
  filterClassification: 'all',

  setSelectedFile: (file) => set({ selectedFile: file }),
  setConfidenceThreshold: (threshold) => set({ confidenceThreshold: threshold }),
  setFilterClassification: (classification) => set({ filterClassification: classification }),
}));

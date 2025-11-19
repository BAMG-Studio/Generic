import { create } from "zustand";
import { subscribeWithSelector } from "zustand/middleware";

interface ResourceState {
  resources: {
    popularity: number;
    stability: number;
    media: number;
    economy: number;
  };
  
  // Actions
  updateResources: (changes: Partial<ResourceState['resources']>) => void;
  setResources: (resources: ResourceState['resources']) => void;
  resetResources: () => void;
  getResourceTotal: () => number;
}

const defaultResources = {
  popularity: 50,
  stability: 50,
  media: 50,
  economy: 50
};

export const useResources = create<ResourceState>()(
  subscribeWithSelector((set, get) => ({
    resources: { ...defaultResources },
    
    updateResources: (changes) => {
      const { resources } = get();
      const newResources = { ...resources };
      
      Object.entries(changes).forEach(([resource, change]) => {
        if (resource in newResources && typeof change === 'number') {
          const key = resource as keyof ResourceState['resources'];
          newResources[key] = Math.max(0, Math.min(100, newResources[key] + change));
        }
      });
      
      console.log('Resources updated:', newResources);
      set({ resources: newResources });
    },
    
    setResources: (resources) => {
      console.log('Resources set to:', resources);
      set({ resources });
    },
    
    resetResources: () => {
      console.log('Resources reset to defaults');
      set({ resources: { ...defaultResources } });
    },
    
    getResourceTotal: () => {
      const { resources } = get();
      return Object.values(resources).reduce((sum, val) => sum + val, 0);
    }
  }))
);

// Monitor for game-ending conditions
useResources.subscribe(
  (state) => state.resources,
  (resources) => {
    const totalResources = Object.values(resources).reduce((sum, val) => sum + val, 0);
    const criticalResources = Object.values(resources).filter(val => val <= 10);
    
    if (totalResources <= 80 || criticalResources.length >= 2) {
      console.warn('Critical resource levels detected!');
    }
  }
);

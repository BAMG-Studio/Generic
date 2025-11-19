import { create } from 'zustand';
import { useGameState } from './useGameState';
import { useCharacters } from './useCharacters';
import { useResources } from './useResources';

interface SaveGame {
  id: string;
  name: string;
  timestamp: Date;
  gameState: any;
  character: any;
  resources: any;
  turn: number;
  score: number;
}

interface SaveGameStore {
  saves: SaveGame[];
  currentSaveId: string | null;
  
  // Actions
  saveGame: (name?: string) => void;
  loadGame: (id: string) => void;
  deleteSave: (id: string) => void;
  getSaves: () => SaveGame[];
  autoSave: () => void;
}

export const useSaveGame = create<SaveGameStore>((set, get) => ({
  saves: [],
  currentSaveId: null,
  
  saveGame: (name = 'Autosave') => {
    const gameState = useGameState.getState();
    const character = useCharacters.getState();
    const resources = useResources.getState();
    
    const save: SaveGame = {
      id: Date.now().toString(),
      name,
      timestamp: new Date(),
      gameState: {
        gamePhase: gameState.gamePhase,
        turn: gameState.turn,
        timeOfDay: gameState.timeOfDay
      },
      character: character.selectedCharacter,
      resources: resources.resources,
      turn: gameState.turn,
      score: 0 // Calculate based on game state
    };
    
    // Save to localStorage
    const existingSaves = JSON.parse(localStorage.getItem('executiveDisorderSaves') || '[]');
    const updatedSaves = [...existingSaves, save].slice(-10); // Keep only last 10 saves
    localStorage.setItem('executiveDisorderSaves', JSON.stringify(updatedSaves));
    
    set({ 
      saves: updatedSaves,
      currentSaveId: save.id 
    });
    
    console.log('Game saved:', save.name);
  },
  
  loadGame: (id: string) => {
    const saves = JSON.parse(localStorage.getItem('executiveDisorderSaves') || '[]');
    const save = saves.find((s: SaveGame) => s.id === id);
    
    if (save) {
      // Restore game state
      useGameState.setState({
        gamePhase: save.gameState.gamePhase,
        turn: save.gameState.turn,
        timeOfDay: save.gameState.timeOfDay
      });
      
      // Restore character
      useCharacters.setState({
        selectedCharacter: save.character
      });
      
      // Restore resources
      useResources.setState({
        resources: save.resources
      });
      
      set({ currentSaveId: id });
      console.log('Game loaded:', save.name);
    }
  },
  
  deleteSave: (id: string) => {
    const saves = JSON.parse(localStorage.getItem('executiveDisorderSaves') || '[]');
    const updatedSaves = saves.filter((s: SaveGame) => s.id !== id);
    localStorage.setItem('executiveDisorderSaves', JSON.stringify(updatedSaves));
    
    set({ saves: updatedSaves });
    console.log('Save deleted:', id);
  },
  
  getSaves: () => {
    const saves = JSON.parse(localStorage.getItem('executiveDisorderSaves') || '[]');
    set({ saves });
    return saves;
  },
  
  autoSave: () => {
    const gameState = useGameState.getState();
    
    // Only autosave during gameplay
    if (gameState.gamePhase === 'playing') {
      get().saveGame('Autosave');
    }
  }
}));

// Auto-save every 30 seconds during gameplay
if (typeof window !== 'undefined') {
  setInterval(() => {
    const gameState = useGameState.getState();
    if (gameState.gamePhase === 'playing') {
      useSaveGame.getState().autoSave();
    }
  }, 30000);
}
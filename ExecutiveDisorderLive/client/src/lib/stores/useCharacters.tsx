import { create } from "zustand";
import { characters } from "../../data/characters";

interface CharacterState {
  selectedCharacter: any | null;
  availableCharacters: any[];
  
  // Actions
  setSelectedCharacter: (character: any | null) => void;
  getCharacterById: (id: string) => any | null;
}

export const useCharacters = create<CharacterState>((set, get) => ({
  selectedCharacter: null,
  availableCharacters: characters,
  
  setSelectedCharacter: (character) => {
    console.log('Selected character changed to:', character?.name || 'none');
    set({ selectedCharacter: character });
  },
  
  getCharacterById: (id) => {
    const { availableCharacters } = get();
    return availableCharacters.find(char => char.id === id) || null;
  }
}));

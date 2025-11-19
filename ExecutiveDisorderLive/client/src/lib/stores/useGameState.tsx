import { create } from "zustand";
import { subscribeWithSelector } from "zustand/middleware";
import type { PoliticalCharacter } from "../../data/characters";
import { decisionCards } from "../../data/cards";

export type GamePhase = "title_screen" | "main_menu" | "menu" | "character_selection" | "playing" | "ended";
export type TimeOfDay = "morning" | "afternoon" | "night";

interface GameState {
  gamePhase: GamePhase;
  timeOfDay: TimeOfDay;
  turn: number;
  isLoading: boolean;
  selectedCharacter: PoliticalCharacter | null;
  resources: {
    popularity: number;
    stability: number;
    media: number;
    economy: number;
  };
  
  // Actions
  setGamePhase: (phase: GamePhase) => void;
  setTimeOfDay: (time: TimeOfDay) => void;
  nextTurn: () => void;
  resetGame: () => void;
  endGame: () => void;
  setLoading: (loading: boolean) => void;
  setSelectedCharacter: (character: PoliticalCharacter) => void;
  startGame: () => void;
  makeDecision: (cardId: string, optionIndex: number) => void;
}

export const useGameState = create<GameState>()(
  subscribeWithSelector((set, get) => ({
    gamePhase: "title_screen",
    timeOfDay: "morning",
    turn: 1,
    isLoading: false,
    selectedCharacter: null,
    resources: {
      popularity: 50,
      stability: 50,
      media: 50,
      economy: 50,
    },
    
    setGamePhase: (phase) => {
      console.log('Game phase changed to:', phase);
      set({ gamePhase: phase });
    },
    
    setTimeOfDay: (time) => {
      console.log('Time of day changed to:', time);
      set({ timeOfDay: time });
    },
    
    nextTurn: () => {
      const { turn, timeOfDay } = get();
      const newTurn = turn + 1;
      
      // Change time of day every few turns
      let newTimeOfDay = timeOfDay;
      if (newTurn % 10 === 0) {
        if (timeOfDay === "morning") newTimeOfDay = "afternoon";
        else if (timeOfDay === "afternoon") newTimeOfDay = "night";
        else newTimeOfDay = "morning";
      }
      
      set({ turn: newTurn, timeOfDay: newTimeOfDay });
      console.log(`Turn ${newTurn}, Time: ${newTimeOfDay}`);
    },
    
    resetGame: () => {
      set({
        gamePhase: "menu",
        timeOfDay: "morning",
        turn: 1,
        isLoading: false,
        selectedCharacter: null,
        resources: {
          popularity: 50,
          stability: 50,
          media: 50,
          economy: 50,
        },
      });
      console.log('Game reset');
    },
    
    endGame: () => {
      set({ gamePhase: "ended" });
      console.log('Game ended');
    },
    
    setLoading: (loading) => {
      set({ isLoading: loading });
    },
    
    setSelectedCharacter: (character) => {
      set({ 
        selectedCharacter: character,
        resources: { ...character.startingStats }
      });
      console.log('Selected character:', character.name);
    },
    
    startGame: () => {
      set({ gamePhase: "playing" });
      console.log('Game started');
    },
    
    makeDecision: (cardId, optionIndex) => {
      const card = decisionCards.find(c => c.id === cardId);
      
      if (card && card.options[optionIndex]) {
        const effects = card.options[optionIndex].effects;
        
        // Use functional setter to avoid stale state from rapid clicks
        set((state) => {
          const newResources = {
            popularity: Math.max(0, Math.min(100, state.resources.popularity + effects.popularity)),
            stability: Math.max(0, Math.min(100, state.resources.stability + effects.stability)),
            media: Math.max(0, Math.min(100, state.resources.media + effects.media)),
            economy: Math.max(0, Math.min(100, state.resources.economy + effects.economy)),
          };
          
          return { resources: newResources };
        });
        
        console.log(`Decision made: ${cardId}, option: ${optionIndex}`, effects);
      }
      
      // Advance the turn
      get().nextTurn();
      
      // Check game over conditions after turn advance
      const state = get();
      const { resources, turn } = state;
      
      // Game over if any resource hits 0 (immediate)
      if (resources.popularity <= 0 || resources.stability <= 0 || 
          resources.media <= 0 || resources.economy <= 0) {
        console.log('GAME OVER: A critical resource has reached zero!', resources);
        get().endGame();
      }
      
      // Game complete if reached turn 20 (immediate)
      else if (turn >= 20) {
        console.log('GAME COMPLETE: Reached final turn 20!');
        get().endGame();
      }
    }
  }))
);

// Auto-advance turns during gameplay
useGameState.subscribe(
  (state) => state.gamePhase,
  (gamePhase) => {
    if (gamePhase === "playing") {
      // This could be extended to auto-advance turns or trigger events
      console.log('Entered gameplay phase');
    }
  }
);

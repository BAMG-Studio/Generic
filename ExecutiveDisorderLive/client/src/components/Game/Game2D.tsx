import React from "react";
import TitleScreen from "./TitleScreen";
import EnhancedMainMenu from "./EnhancedMainMenu";
import MainMenu from "./MainMenu";
import CharacterSelection2D from "./CharacterSelection2D.tsx";
import EnhancedGameplay from "./EnhancedGameplay";
import EnhancedGameEnding from "./EnhancedGameEnding";
import { useGameState } from "../../lib/stores/useGameState";

export default function Game2D() {
  const { gamePhase } = useGameState();

  return (
    <div className="w-full h-full bg-gradient-to-br from-gray-900 to-gray-800">
      {gamePhase === 'title_screen' && <TitleScreen />}
      {gamePhase === 'main_menu' && <EnhancedMainMenu />}
      {gamePhase === 'menu' && <MainMenu />}
      {gamePhase === 'character_selection' && <CharacterSelection2D />}
      {gamePhase === 'playing' && <EnhancedGameplay />}
      {gamePhase === 'ended' && <EnhancedGameEnding />}
    </div>
  );
}

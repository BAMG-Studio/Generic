import React from "react";
import { useGameState } from "../../lib/stores/useGameState";
import { useCharacters } from "../../lib/stores/useCharacters";
import { useResources } from "../../lib/stores/useResources";
import { gameConfig } from "../../data/gameConfig";
import { Button } from "../ui/button";
import { Card } from "../ui/card";

export default function GameEnding() {
  const { turn, resetGame } = useGameState();
  const { selectedCharacter } = useCharacters();
  const { resources } = useResources();

  if (!selectedCharacter) return null;

  // Calculate total score
  const totalScore = Object.values(resources).reduce((sum, val) => sum + val, 0);

  // Determine ending based on score
  const getEnding = () => {
    const endings = Object.entries(gameConfig.endings).sort((a, b) => b[1].threshold - a[1].threshold);
    for (const [key, ending] of endings) {
      if (totalScore >= ending.threshold) {
        return ending;
      }
    }
    return gameConfig.endings.disaster;
  };

  const ending = getEnding();
  const endingColor = totalScore >= 240 ? '#10b981' : totalScore >= 160 ? '#f59e0b' : '#ef4444';

  return (
    <div className="w-full h-full flex items-center justify-center p-8" style={{
      backgroundImage: 'url(/ending-background.png)',
      backgroundSize: 'cover',
      backgroundPosition: 'center',
      backgroundRepeat: 'no-repeat',
      minHeight: '100vh'
    }}>
      <Card className="bg-gray-900/95 backdrop-blur-md p-8 max-w-4xl w-full shadow-2xl">
        {/* Logo */}
        <img src="/logo.png" alt="Executive Disorder" className="h-24 w-auto mx-auto mb-6 drop-shadow-2xl" />
        
        {/* Character Portrait */}
        <div className="flex justify-center mb-6">
          <div
            className="w-32 h-32 rounded-full overflow-hidden shadow-lg border-4 border-gray-700"
            style={{ backgroundColor: selectedCharacter.themeColor }}
          >
            <img 
              src={`/characters/${selectedCharacter.id}.png`} 
              alt={selectedCharacter.name}
              className="w-full h-full object-cover"
            />
          </div>
        </div>

        {/* Ending Title */}
        <h1 className="text-4xl font-bold text-center mb-4" style={{ color: endingColor }}>
          {ending.title}
        </h1>

        {/* Ending Description */}
        <p className="text-xl text-gray-300 text-center mb-8 max-w-2xl mx-auto">
          {ending.description}
        </p>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div className="text-center">
            <p className="text-3xl font-bold text-white">{Math.round(resources.popularity)}</p>
            <p className="text-gray-400">Popularity</p>
          </div>
          <div className="text-center">
            <p className="text-3xl font-bold text-white">{Math.round(resources.stability)}</p>
            <p className="text-gray-400">Stability</p>
          </div>
          <div className="text-center">
            <p className="text-3xl font-bold text-white">{Math.round(resources.media)}</p>
            <p className="text-gray-400">Media</p>
          </div>
          <div className="text-center">
            <p className="text-3xl font-bold text-white">{Math.round(resources.economy)}</p>
            <p className="text-gray-400">Economy</p>
          </div>
        </div>

        {/* Final Score */}
        <div className="text-center mb-8">
          <p className="text-2xl text-gray-400 mb-2">Final Score</p>
          <p className="text-6xl font-bold" style={{ color: endingColor }}>{Math.round(totalScore)}</p>
          <p className="text-gray-400 mt-2">Completed in {turn} turns</p>
        </div>

        {/* Character Summary */}
        <Card className="bg-gray-800/80 p-4 mb-8">
          <p className="text-center text-gray-300">
            Playing as <span className="font-bold text-white">{selectedCharacter.name}</span> - {selectedCharacter.title}
          </p>
        </Card>

        {/* Action Buttons */}
        <div className="flex gap-4 justify-center">
          <Button
            onClick={resetGame}
            className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3"
          >
            Play Again
          </Button>
          <Button
            onClick={() => window.location.reload()}
            className="bg-gray-600 hover:bg-gray-700 text-white px-8 py-3"
          >
            Main Menu
          </Button>
        </div>
      </Card>
    </div>
  );
}
import React from "react";
import { useGameState } from "../../lib/stores/useGameState";
import { useResources } from "../../lib/stores/useResources";
import { useCharacters } from "../../lib/stores/useCharacters";
import { Button } from "../ui/button";
import { Card } from "../ui/card";

export default function GameUI() {
  const { gamePhase, turn, setGamePhase } = useGameState();
  const { resources, resetResources } = useResources();
  const { selectedCharacter, setSelectedCharacter } = useCharacters();

  if (gamePhase === 'character_selection') {
    return (
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-4 left-4 text-white">
          <h1 className="text-3xl font-bold mb-2">Executive Disorder</h1>
          <p className="text-gray-300">Choose your political leader</p>
        </div>

        <div className="absolute top-4 right-4 pointer-events-auto">
          <Button
            variant="secondary"
            onClick={() => setGamePhase('menu')}
            className="bg-gray-800 text-white hover:bg-gray-700"
          >
            Back to Menu
          </Button>
        </div>

        {selectedCharacter && (
          <div className="absolute bottom-4 left-4 right-4 pointer-events-none">
            <Card className="bg-black/80 text-white p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-xl font-bold mb-2">{selectedCharacter.name}</h3>
                  <p className="text-gray-300 mb-4">{selectedCharacter.fullBio}</p>
                </div>
                <div>
                  <h4 className="text-lg font-semibold mb-2">Starting Stats</h4>
                  <div className="grid grid-cols-2 gap-2">
                    {Object.entries(selectedCharacter.startingStats).map(([stat, value]) => (
                      <div key={stat} className="flex justify-between">
                        <span className="capitalize">{stat}:</span>
                        <span className="font-mono">{String(value)}</span>
                      </div>
                    ))}
                  </div>
                  
                  <h4 className="text-lg font-semibold mt-4 mb-2">Special Abilities</h4>
                  <ul className="text-sm text-gray-300">
                    {selectedCharacter.abilities.map((ability: string, index: number) => (
                      <li key={index} className="mb-1">{`• ${ability}`}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </Card>
          </div>
        )}
      </div>
    );
  }

  if (gamePhase === 'playing') {
    return (
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-4 left-4 text-white">
          <h2 className="text-xl font-bold">{selectedCharacter?.name}</h2>
          <p className="text-gray-300">Turn {turn}</p>
        </div>

        <div className="absolute top-4 right-4 pointer-events-auto space-x-2">
          <Button
            variant="secondary"
            onClick={() => {
              setGamePhase('character_selection');
              setSelectedCharacter(null);
              resetResources();
            }}
            className="bg-gray-800 text-white hover:bg-gray-700"
          >
            New Game
          </Button>
        </div>

        <div className="absolute bottom-4 left-4 right-4 pointer-events-none">
          <Card className="bg-black/80 text-white p-4">
            <div className="flex justify-between items-center">
              <div>
                <h4 className="font-semibold mb-2">Current Resources</h4>
                <div className="flex space-x-6">
                  {Object.entries(resources).map(([resource, value]) => (
                    <div key={resource} className="text-center">
                      <div className="text-lg font-mono">{Math.round(value)}</div>
                      <div className="text-xs text-gray-300 capitalize">{resource}</div>
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="text-right">
                <div className="text-sm text-gray-300">Average Score</div>
                <div className="text-2xl font-bold">
                  {Math.round(Object.values(resources).reduce((sum: number, val: number) => sum + val, 0) / 4)}
                </div>
              </div>
            </div>
          </Card>
        </div>
      </div>
    );
  }

  if (gamePhase === 'ended') {
    const averageScore = Math.round(Object.values(resources).reduce((sum: number, val: number) => sum + val, 0) / 4);
    let outcome = "Political Disaster";
    if (averageScore > 70) outcome = "Triumphant Victory";
    else if (averageScore > 50) outcome = "Moderate Success";
    else if (averageScore > 30) outcome = "Controversial Term";

    return (
      <div className="absolute inset-0 bg-black/90 flex items-center justify-center pointer-events-auto">
        <Card className="bg-gray-900 text-white p-8 max-w-md w-full mx-4">
          <h2 className="text-3xl font-bold text-center mb-4">Game Over</h2>
          
          <div className="text-center mb-6">
            <h3 className="text-xl font-semibold text-yellow-400 mb-2">{outcome}</h3>
            <p className="text-gray-300">
              {selectedCharacter?.name} completed {turn} turns as leader
            </p>
          </div>

          <div className="mb-6">
            <h4 className="font-semibold mb-3">Final Resources</h4>
            {Object.entries(resources).map(([resource, value]) => (
              <div key={resource} className="flex justify-between mb-2">
                <span className="capitalize">{resource}:</span>
                <span className={`font-mono ${value > 50 ? 'text-green-400' : value > 25 ? 'text-yellow-400' : 'text-red-400'}`}>
                  {Math.round(value)}
                </span>
              </div>
            ))}
          </div>

          <div className="space-y-2">
            <Button
              onClick={() => {
                setGamePhase('character_selection');
                setSelectedCharacter(null);
                resetResources();
              }}
              className="w-full bg-blue-600 hover:bg-blue-700"
            >
              Play Again
            </Button>
            
            <Button
              variant="secondary"
              onClick={() => setGamePhase('menu')}
              className="w-full bg-gray-700 hover:bg-gray-600"
            >
              Main Menu
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  // Menu screen
  return (
    <div className="absolute inset-0 bg-gradient-to-br from-blue-900 to-purple-900 flex items-center justify-center pointer-events-auto">
      <Card className="bg-black/80 text-white p-8 max-w-md w-full mx-4">
        <h1 className="text-4xl font-bold text-center mb-2">Executive Disorder</h1>
        <p className="text-gray-300 text-center mb-8">A Satirical Political Card Game</p>
        
        <div className="space-y-4">
          <Button
            onClick={() => setGamePhase('character_selection')}
            className="w-full bg-green-600 hover:bg-green-700 text-lg py-3"
          >
            Start New Game
          </Button>
          
          <div className="text-center text-sm text-gray-400">
            <p>Balance resources • Make decisions • Survive the chaos</p>
          </div>
        </div>
      </Card>
    </div>
  );
}

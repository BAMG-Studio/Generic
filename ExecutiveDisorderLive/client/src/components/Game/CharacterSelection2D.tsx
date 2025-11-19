import React from "react";
import { useCharacters } from "../../lib/stores/useCharacters";
import { useGameState } from "../../lib/stores/useGameState";
import { characters } from "../../data/characters";
import { Card } from "../ui/card";
import { Button } from "../ui/button";

export default function CharacterSelection2D() {
  const { selectedCharacter, setSelectedCharacter } = useCharacters();
  const { setGamePhase } = useGameState();

  const handleStartGame = () => {
    if (selectedCharacter) {
      console.log('Starting game with:', selectedCharacter.name);
      setGamePhase('playing');
    }
  };

  return (
    <div className="relative w-full min-h-screen overflow-auto">
      {/* Dynamic Animated Background */}
      <div className="fixed inset-0 -z-10">
        <div className="absolute inset-0 bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900" />
        <div className="absolute inset-0 opacity-30">
          <div className="absolute inset-0 bg-gradient-to-t from-blue-600/30 via-transparent to-red-600/30 animate-pulse" />
        </div>
        <video
          src="/videos/replay-loops/campaign-headquarters.mp4"
          autoPlay
          muted
          loop
          playsInline
          className="absolute inset-0 w-full h-full object-cover mix-blend-overlay opacity-30"
        />
        <div className="absolute inset-0 bg-black/20" />
      </div>
      
      <div className="relative z-10 p-8">
      <div className="flex flex-col items-center mb-8">
        <img src="/logo.png" alt="Executive Disorder" className="h-24 sm:h-32 w-auto mb-6 drop-shadow-2xl" />
        <h1 className="text-3xl sm:text-4xl md:text-5xl font-black text-white text-center mb-3 drop-shadow-lg uppercase tracking-tight bg-gradient-to-r from-yellow-400 to-orange-500 bg-clip-text text-transparent">
          Choose Your Leader
        </h1>
        <p className="text-yellow-300 text-center text-base sm:text-lg drop-shadow-md font-bold uppercase tracking-wide">
          Select Your Political Avatar
        </p>
      </div>
      
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3 sm:gap-4 mb-8">
        {characters.map((character) => (
          <Card
            key={character.id}
            className={`cursor-pointer transition-all transform hover:scale-105 backdrop-blur-md ${
              selectedCharacter?.id === character.id
                ? 'ring-4 ring-yellow-400 bg-white/20 shadow-2xl shadow-yellow-500/50 scale-105'
                : 'bg-white/10 hover:bg-white/15 border border-white/20'
            }`}
            onClick={() => setSelectedCharacter(character)}
          >
            <div className="p-3 sm:p-4">
              <div
                className="w-full aspect-square rounded-lg mb-3 overflow-hidden border-2 border-white/20"
                style={{ backgroundColor: character.themeColor }}
              >
                <img 
                  src={`/characters/${character.id}.png`} 
                  alt={character.name}
                  className="w-full h-full object-cover"
                />
              </div>
              
              <h3 className="text-white font-black text-xs sm:text-sm mb-1 truncate uppercase">{character.name}</h3>
              <p className="text-yellow-400 text-xs mb-2 truncate font-bold">{character.title}</p>
              
              <div className="grid grid-cols-2 gap-1 text-xs">
                {Object.entries(character.startingStats).map(([stat, value]) => (
                  <div key={stat} className="flex justify-between bg-black/30 rounded px-1 py-0.5">
                    <span className="text-gray-300 capitalize font-bold">{stat.slice(0, 3)}:</span>
                    <span className="text-yellow-400 font-black">{value}</span>
                  </div>
                ))}
              </div>
            </div>
          </Card>
        ))}
      </div>

      {selectedCharacter && (
        <Card className="backdrop-blur-xl bg-gradient-to-br from-white/20 to-white/10 p-4 sm:p-6 max-w-5xl mx-auto shadow-2xl border-2 border-yellow-400/50">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
            <div>
              <div
                className="w-40 h-40 sm:w-48 sm:h-48 rounded-lg mx-auto mb-4 overflow-hidden border-4 border-white/20"
                style={{ backgroundColor: selectedCharacter.themeColor }}
              >
                <img 
                  src={`/characters/${selectedCharacter.id}.png`} 
                  alt={selectedCharacter.name}
                  className="w-full h-full object-cover"
                />
              </div>
            </div>
            
            <div className="flex flex-col">
              <h2 className="text-2xl sm:text-3xl font-black text-white mb-2 uppercase tracking-tight bg-gradient-to-r from-yellow-400 to-orange-500 bg-clip-text text-transparent">
                {selectedCharacter.name}
              </h2>
              <p className="text-gray-300 mb-4 text-sm sm:text-base leading-relaxed line-clamp-3">
                {selectedCharacter.fullBio}
              </p>
              
              <h3 className="text-base sm:text-lg font-black text-yellow-400 mb-2 uppercase tracking-wide">
                Special Abilities
              </h3>
              <ul className="text-xs sm:text-sm text-gray-300 mb-6 space-y-1">
                {selectedCharacter.abilities.map((ability: string, index: number) => (
                  <li key={index} className="flex items-start">
                    <span className="text-yellow-400 mr-2">★</span>
                    <span className="line-clamp-2">{ability}</span>
                  </li>
                ))}
              </ul>
              
              <Button
                onClick={handleStartGame}
                className="w-full bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white font-black text-base sm:text-lg py-5 sm:py-6 uppercase tracking-wide shadow-lg hover:shadow-green-500/50 transition-all mt-auto"
              >
                🎮 Start Campaign
              </Button>
            </div>
          </div>
        </Card>
      )}
      </div>
    </div>
  );
}

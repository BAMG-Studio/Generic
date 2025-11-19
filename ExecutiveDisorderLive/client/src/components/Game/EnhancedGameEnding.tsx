import React, { useEffect, useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Trophy, RefreshCw, Home, Share2, Star, TrendingUp } from 'lucide-react';
import { useGameState } from '../../lib/stores/useGameState';
import { useCharacters } from '../../lib/stores/useCharacters';
import { useResources } from '../../lib/stores/useResources';
import { expandedEndings, type GameEnding } from '../../data/expandedEndings';

export default function EnhancedGameEnding() {
  const { resetGame, setGamePhase, turn } = useGameState();
  const { selectedCharacter } = useCharacters();
  const { resources } = useResources();
  const [ending, setEnding] = useState<GameEnding | null>(null);
  const [showStats, setShowStats] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);
  
  useEffect(() => {
    // Load game state from localStorage (passed from gameplay)
    const savedState = localStorage.getItem('endingGameState');
    const gameState = savedState ? JSON.parse(savedState) : {
      resources,
      turn,
      chaos: 0,
      cardHistory: [],
      absurdCards: 0,
      crisisCards: 0,
      cascades: 0,
      streak: 0
    };
    
    // Check each ending condition
    let selectedEnding: GameEnding | null = null;
    
    // Check special/combo endings first (highest priority)
    for (const e of expandedEndings) {
      if (e.trigger.type === 'special' || e.trigger.type === 'combo') {
        if (checkCondition(e, gameState)) {
          selectedEnding = e;
          break;
        }
      }
    }
    
    // If no special ending, check resource-based endings
    if (!selectedEnding) {
      for (const e of expandedEndings) {
        if (e.trigger.type === 'resources') {
          if (checkCondition(e, gameState)) {
            selectedEnding = e;
            break;
          }
        }
      }
    }
    
    // Check turn-based endings
    if (!selectedEnding) {
      for (const e of expandedEndings) {
        if (e.trigger.type === 'turn') {
          if (checkCondition(e, gameState)) {
            selectedEnding = e;
            break;
          }
        }
      }
    }
    
    // Default to balanced victory if survived to end
    if (!selectedEnding) {
      selectedEnding = expandedEndings[1]; // balanced-victory
    }
    
    setEnding(selectedEnding);
    
    // Clear saved state
    localStorage.removeItem('endingGameState');
    
    // Show stats after video plays
    setTimeout(() => {
      setShowStats(true);
    }, 10000); // After 10 second video
  }, [resources, turn]);
  
  const checkCondition = (ending: GameEnding, state: any): boolean => {
    const { resources, turn: currentTurn, chaos, absurdCards: absurdCount, crisisCards: crisisCount, cascades: cascadeCount } = state;
    const { type, conditions } = ending.trigger;
    
    if (type === 'resources') {
      // Check for "all above threshold"
      if (conditions.all !== undefined) {
        return Object.values(resources).every((v: any) => v >= conditions.all);
      }
      
      // Check for "all below threshold"
      if (conditions.allBelow !== undefined) {
        return Object.values(resources).every((v: any) => v <= conditions.allBelow);
      }
      
      // Check individual resource conditions (assume >= for victory, <= for disaster)
      return Object.entries(conditions).every(([key, value]) => {
        const resourceValue = resources[key];
        const threshold = value as number;
        
        // If it's a high value (>50), check if resource is above threshold
        // If it's a low value (<50), check if resource is below threshold
        if (threshold >= 50) {
          return resourceValue >= threshold;
        } else {
          return resourceValue <= threshold;
        }
      });
    }
    
    if (type === 'turn') {
      return currentTurn >= conditions.turns;
    }
    
    if (type === 'special') {
      // Check special conditions like chaos, absurd cards, etc.
      if (conditions.chaos !== undefined) {
        return chaos >= conditions.chaos;
      }
      if (conditions.absurdCards !== undefined) {
        return absurdCount >= conditions.absurdCards;
      }
      if (conditions.crisisCards !== undefined) {
        return crisisCount >= conditions.crisisCards;
      }
      if (conditions.cascades !== undefined) {
        return cascadeCount >= conditions.cascades;
      }
      return false;
    }
    
    if (type === 'combo') {
      return Object.entries(conditions).every(([key, value]) => {
        const numValue = value as number;
        
        if (key === 'allBelow') {
          return Object.values(resources).every((v: any) => v <= numValue);
        }
        
        if (resources[key] !== undefined) {
          // Use same logic as resources: high values check >=, low values check <=
          if (numValue >= 50) {
            return resources[key] >= numValue;
          } else {
            return resources[key] <= numValue;
          }
        }
        
        return true;
      });
    }
    
    return false;
  };
  
  const handlePlayAgain = () => {
    resetGame();
    setGamePhase('character_selection');
  };
  
  const handleMainMenu = () => {
    resetGame();
    setGamePhase('menu');
  };
  
  const getRankColor = () => {
    if (!ending) return 'from-gray-400 to-gray-600';
    
    switch(ending.rank) {
      case 'S': return 'from-yellow-400 to-yellow-600';
      case 'A': return 'from-purple-400 to-purple-600';
      case 'B': return 'from-blue-400 to-blue-600';
      case 'C': return 'from-green-400 to-green-600';
      case 'D': return 'from-orange-400 to-orange-600';
      case 'F': return 'from-red-400 to-red-600';
      default: return 'from-gray-400 to-gray-600';
    }
  };
  
  return (
    <div className="relative w-full h-full overflow-hidden bg-black">
      {/* Ending Video */}
      <AnimatePresence>
        {!showStats && ending && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 z-10"
          >
            <video
              ref={videoRef}
              src={ending.video}
              autoPlay
              muted={false}
              onEnded={() => setShowStats(true)}
              className="w-full h-full object-cover"
            />
            
            {/* Ending Title Overlay */}
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
              <motion.h1
                initial={{ scale: 0, rotate: -180 }}
                animate={{ scale: 1, rotate: 0 }}
                transition={{ delay: 1, type: "spring", stiffness: 100 }}
                className="text-7xl md:text-9xl font-black text-white drop-shadow-2xl text-center px-4"
                style={{ textShadow: '0 0 60px rgba(0,0,0,0.9)' }}
              >
                {ending.name.toUpperCase()}
              </motion.h1>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
      
      {/* Stats Screen */}
      <AnimatePresence>
        {showStats && ending && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="absolute inset-0 z-20 bg-gradient-to-br from-gray-900 to-black flex items-center justify-center p-8"
          >
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: 0.2 }}
              className="max-w-4xl w-full bg-black/80 backdrop-blur-xl rounded-3xl p-8 md:p-12 border-2 border-white/10"
            >
              {/* Rank Display */}
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.4, type: "spring", stiffness: 100 }}
                className="flex justify-center mb-8"
              >
                <div className={`w-40 h-40 rounded-full bg-gradient-to-br ${getRankColor()} flex items-center justify-center shadow-2xl`}>
                  <span className="text-7xl font-black text-white">{ending.rank}</span>
                </div>
              </motion.div>
              
              {/* Rank Title */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6 }}
                className="text-center mb-8"
              >
                <h2 className="text-4xl font-black text-white mb-2">{ending.name}</h2>
                <p className="text-xl text-gray-400">Final Score: {ending.score.toLocaleString()}</p>
                <div className="mt-2 inline-block px-4 py-1 bg-white/10 rounded-full">
                  <span className="text-sm text-gray-300 font-bold uppercase">{ending.category}</span>
                </div>
              </motion.div>
              
              {/* Ending Message */}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.8 }}
                className="bg-gradient-to-r from-purple-600/20 to-pink-600/20 rounded-2xl p-6 mb-8 border border-purple-500/30"
              >
                <p className="text-lg text-purple-200 text-center leading-relaxed">
                  {ending.description}
                </p>
              </motion.div>
              
              {/* Game Stats */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1 }}
                className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8"
              >
                <div className="bg-white/5 rounded-xl p-4 text-center">
                  <p className="text-gray-400 text-sm mb-1">Character</p>
                  <p className="text-white font-bold">{selectedCharacter?.name}</p>
                </div>
                <div className="bg-white/5 rounded-xl p-4 text-center">
                  <p className="text-gray-400 text-sm mb-1">Turns Survived</p>
                  <p className="text-white font-bold text-2xl">{turn}</p>
                </div>
                <div className="bg-white/5 rounded-xl p-4 text-center">
                  <p className="text-gray-400 text-sm mb-1">Final Popularity</p>
                  <p className="text-white font-bold text-2xl">{resources.popularity}%</p>
                </div>
                <div className="bg-white/5 rounded-xl p-4 text-center">
                  <p className="text-gray-400 text-sm mb-1">Final Economy</p>
                  <p className="text-white font-bold text-2xl">{resources.economy}%</p>
                </div>
              </motion.div>
              
              {/* Achievement Badges */}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 1.2 }}
                className="flex justify-center gap-4 mb-8"
              >
                {turn > 50 && (
                  <div className="bg-yellow-500/20 rounded-full p-3 border border-yellow-500/50">
                    <Star className="w-8 h-8 text-yellow-400" />
                  </div>
                )}
                {resources.popularity > 70 && (
                  <div className="bg-blue-500/20 rounded-full p-3 border border-blue-500/50">
                    <Trophy className="w-8 h-8 text-blue-400" />
                  </div>
                )}
                {ending.category === 'victory' && (
                  <div className="bg-green-500/20 rounded-full p-3 border border-green-500/50">
                    <TrendingUp className="w-8 h-8 text-green-400" />
                  </div>
                )}
              </motion.div>
              
              {/* Action Buttons */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1.4 }}
                className="flex flex-col md:flex-row gap-4"
              >
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={handlePlayAgain}
                  className="flex-1 bg-gradient-to-r from-green-600 to-emerald-600 text-white text-xl font-bold py-4 px-8 rounded-xl shadow-xl hover:shadow-green-500/50 transition-all flex items-center justify-center gap-3"
                >
                  <RefreshCw className="w-6 h-6" />
                  PLAY AGAIN
                </motion.button>
                
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={handleMainMenu}
                  className="flex-1 bg-gradient-to-r from-purple-600 to-pink-600 text-white text-xl font-bold py-4 px-8 rounded-xl shadow-xl hover:shadow-purple-500/50 transition-all flex items-center justify-center gap-3"
                >
                  <Home className="w-6 h-6" />
                  MAIN MENU
                </motion.button>
                
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="flex-1 bg-gradient-to-r from-blue-600 to-cyan-600 text-white text-xl font-bold py-4 px-8 rounded-xl shadow-xl hover:shadow-blue-500/50 transition-all flex items-center justify-center gap-3"
                >
                  <Share2 className="w-6 h-6" />
                  SHARE
                </motion.button>
              </motion.div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
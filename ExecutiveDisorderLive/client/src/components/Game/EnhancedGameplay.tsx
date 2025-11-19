import React, { useState, useEffect, useRef } from 'react';
import { useGameState } from '../../lib/stores/useGameState';
import { useCharacters } from '../../lib/stores/useCharacters';
import { useResources } from '../../lib/stores/useResources';
import { expandedDecisionCards, crisisCards as crisisCardData, cascadeEffects, characterModifiers } from '../../data/expandedCards';
import { motion, AnimatePresence } from 'framer-motion';
import { Volume2, VolumeX, AlertTriangle, TrendingUp, TrendingDown, Zap, Star, Skull } from 'lucide-react';

export default function EnhancedGameplay() {
  const { gamePhase, turn, nextTurn, endGame } = useGameState();
  const { selectedCharacter } = useCharacters();
  const { resources, updateResources, setResources } = useResources();
  
  const [currentCard, setCurrentCard] = useState<any>(null);
  const [cardHistory, setCardHistory] = useState<string[]>([]);
  const [showCrisis, setShowCrisis] = useState(false);
  const [cascadeMessage, setCascadeMessage] = useState<string | null>(null);
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [backgroundVideo, setBackgroundVideo] = useState<string>('/videos/replay-loops/government-office-ambient.mp4');
  const [showEnding, setShowEnding] = useState(false);
  const [endingType, setEndingType] = useState<string>('');
  const [isDeciding, setIsDeciding] = useState(false);
  const [streak, setStreak] = useState(0);
  const [chaos, setChaos] = useState(0);
  
  const audioRef = useRef<HTMLAudioElement | null>(null);

  // Initialize character stats
  useEffect(() => {
    if (selectedCharacter && gamePhase === 'playing') {
      // Set starting resources from character
      setResources(selectedCharacter.startingStats);
    }
  }, [selectedCharacter, gamePhase]);

  // Determine background video based on resource state
  useEffect(() => {
    if (!resources) return;
    
    const { popularity, stability, media, economy } = resources;
    
    // Critical states get priority
    if (stability < 30) {
      setBackgroundVideo('/videos/replay-loops/protest-demonstration.mp4');
    } else if (economy < 30) {
      setBackgroundVideo('/videos/replay-loops/stock-market-displays.mp4');
    } else if (media < 30) {
      setBackgroundVideo('/videos/replay-loops/media-circus-exterior.mp4');
    } else if (popularity > 70) {
      setBackgroundVideo('/videos/replay-loops/political-rally-crowd.mp4');
    } else if (turn % 10 === 0) {
      // Change video every 10 turns for variety
      const videos = [
        'government-office-ambient',
        'capitol-building-exterior',
        'press-conference-room',
        'campaign-headquarters',
        'breaking-news-ticker'
      ];
      const randomVideo = videos[Math.floor(Math.random() * videos.length)];
      setBackgroundVideo(`/videos/replay-loops/${randomVideo}.mp4`);
    }
  }, [resources, turn]);

  // Check for cascade effects
  useEffect(() => {
    if (!resources) return;
    
    const { popularity, stability, media, economy } = resources;
    
    // Check for cascades
    if (economy < cascadeEffects.economicCollapse.threshold) {
      triggerCascade(cascadeEffects.economicCollapse);
    } else if (stability < cascadeEffects.civilUnrest.threshold) {
      triggerCascade(cascadeEffects.civilUnrest);
    } else if (media < cascadeEffects.mediaScandal.threshold) {
      triggerCascade(cascadeEffects.mediaScandal);
    } else if (popularity > cascadeEffects.popularityBoost.threshold && streak > 3) {
      triggerCascade(cascadeEffects.popularityBoost);
    }
  }, [resources, streak]);

  // Trigger cascade effect
  const triggerCascade = (cascade: any) => {
    if (cascadeMessage) return; // Prevent multiple cascades
    
    setCascadeMessage(cascade.message);
    updateResources(cascade.effects);
    setChaos(prev => prev + 10);
    setCascades(prev => prev + 1); // Track cascade count
    playSound('alert');
    
    setTimeout(() => {
      setCascadeMessage(null);
    }, 5000);
  };

  // Store game state for ending detection
  const [absurdCards, setAbsurdCards] = useState(0);
  const [crisisCards, setCrisisCards] = useState(0);
  const [cascades, setCascades] = useState(0);
  
  // Check for game ending conditions
  useEffect(() => {
    if (!resources || gamePhase !== 'playing') return;
    
    const { popularity, stability, media, economy } = resources;
    
    // Check ending conditions based on expanded endings
    if (popularity < 20 && stability < 20 && media < 20 && economy < 20) {
      triggerEnding('ending-nuclear-catastrophe');
    } else if (economy < 15) {
      triggerEnding('ending-economic-collapse');
    } else if (stability < 15) {
      triggerEnding('ending-revolution-uprising');
    } else if ((media < 25 || popularity < 25) && turn > 30) {
      triggerEnding('ending-scandal-impeachment');
    } else if (popularity > 85 && stability > 85 && media > 85 && economy > 85) {
      triggerEnding('ending-victory-triumph');
    } else if (turn >= 100) {
      // Save game state to localStorage for ending screen
      localStorage.setItem('endingGameState', JSON.stringify({
        resources,
        turn,
        chaos,
        cardHistory,
        absurdCards,
        crisisCards,
        cascades,
        streak
      }));
      endGame();
    }
  }, [resources, turn, gamePhase]);

  // Trigger ending
  const triggerEnding = (type: string) => {
    setEndingType(type);
    setShowEnding(true);
    playSound('dramatic');
    
    // Play ending video after delay
    setTimeout(() => {
      endGame();
    }, 2000);
  };

  // Determine ending based on resources
  const determineEnding = () => {
    const { popularity, stability, media, economy } = resources;
    const total = popularity + stability + media + economy;
    
    if (total > 280) return 'ending-victory-triumph';
    if (total < 100) return 'ending-nuclear-catastrophe';
    if (economy < 20) return 'ending-economic-collapse';
    if (stability < 20) return 'ending-revolution-uprising';
    return 'ending-scandal-impeachment';
  };

  // Get next decision card
  const getNextCard = () => {
    // Increase chaos over time
    setChaos(prev => Math.min(100, prev + 1));
    
    // Crisis chance increases with chaos
    const crisisChance = chaos / 200;
    if (Math.random() < crisisChance) {
      setShowCrisis(true);
      setCrisisCards(prev => prev + 1); // Track crisis count
      return crisisCardData[Math.floor(Math.random() * crisisCardData.length)];
    }
    
    // Get random card that hasn't been used recently
    let availableCards = expandedDecisionCards.filter(
      card => !cardHistory.slice(-10).includes(card.id) // Don't repeat last 10 cards
    );
    
    if (availableCards.length === 0) {
      availableCards = expandedDecisionCards;
    }
    
    const selectedCard = availableCards[Math.floor(Math.random() * availableCards.length)];
    
    // Track card types
    if (selectedCard.category === 'absurd') {
      setAbsurdCards(prev => prev + 1);
    }
    
    setShowCrisis(false);
    return selectedCard;
  };

  // Handle decision selection
  const handleDecision = (option: any) => {
    if (!selectedCharacter || !currentCard || isDeciding) return;
    
    setIsDeciding(true);
    
    // Apply character modifiers
    let modifiedEffects = { ...option.effects };
    const modifierId = selectedCharacter.id as keyof typeof characterModifiers;
    const modifier = characterModifiers[modifierId];
    
    if (modifier) {
      Object.keys(modifiedEffects).forEach(resource => {
        const key = resource as keyof typeof modifier.modifier;
        if (modifier.modifier[key]) {
          modifiedEffects[resource as keyof typeof modifiedEffects] = Math.round(
            modifiedEffects[resource as keyof typeof modifiedEffects] * modifier.modifier[key]
          );
        }
      });
    }
    
    // Calculate total change for sound and streak
    const totalChange = Object.values(modifiedEffects).reduce((sum: number, val) => sum + (val as number), 0) as number;
    
    // Update streak
    if (totalChange > 0) {
      setStreak(prev => prev + 1);
      playSound('success');
    } else if (totalChange < -20) {
      setStreak(0);
      playSound('disaster');
      setChaos(prev => Math.min(100, prev + 5));
    } else {
      playSound('neutral');
    }
    
    // Apply effects with animation
    updateResources(modifiedEffects);
    
    // Add to history
    setCardHistory(prev => [...prev.slice(-20), currentCard.id]);
    
    // Advance turn
    nextTurn();
    
    // Get next card after delay
    setTimeout(() => {
      setCurrentCard(getNextCard());
      setIsDeciding(false);
    }, 1500);
  };

  // Play sound effect
  const playSound = (type: string) => {
    if (!soundEnabled || !audioRef.current) return;
    
    const sounds: { [key: string]: string } = {
      success: '/audio/music/victory_fanfare.mp3',
      disaster: '/audio/music/economic_disaster.mp3',
      neutral: '/audio/music/diplomatic_tension.mp3',
      alert: '/audio/music/crisis_mode.mp3',
      dramatic: '/audio/music/defeat_theme.mp3',
      click: '/audio/music/main_theme.mp3'
    };
    
    audioRef.current.src = sounds[type] || sounds.click;
    audioRef.current.volume = 0.3;
    audioRef.current.play().catch(() => {
      // Silently fail if audio can't play
    });
  };

  // Initialize game
  useEffect(() => {
    if (gamePhase === 'playing' && !currentCard) {
      setCurrentCard(getNextCard());
    }
  }, [gamePhase]);

  if (!selectedCharacter) return null;

  return (
    <div className="relative w-full h-full overflow-hidden bg-black">
      {/* Background Video Layer */}
      <div className="absolute inset-0 z-0">
        <video
          src={backgroundVideo}
          autoPlay
          muted
          loop
          playsInline
          className="w-full h-full object-cover opacity-40"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black via-black/60 to-transparent" />
      </div>

      {/* Ending Overlay */}
      <AnimatePresence>
        {showEnding && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 bg-black flex items-center justify-center"
          >
            <video
              src={`/videos/ending-cinematics/${endingType}.mp4`}
              autoPlay
              muted={!soundEnabled}
              onEnded={() => endGame()}
              className="absolute inset-0 w-full h-full object-cover"
            />
            <div className="relative z-10 text-center">
              <motion.h1
                initial={{ scale: 0, rotate: -180 }}
                animate={{ scale: 1, rotate: 0 }}
                transition={{ delay: 0.5, type: "spring", stiffness: 100 }}
                className="text-8xl font-black text-white mb-4 drop-shadow-2xl"
              >
                {endingType.includes('victory') ? '🎉 VICTORY! 🎉' : 
                 endingType.includes('scandal') ? '📰 SCANDAL! 📰' :
                 endingType.includes('economic') ? '💸 BANKRUPTCY! 💸' :
                 endingType.includes('revolution') ? '✊ REVOLUTION! ✊' :
                 '☢️ CATASTROPHE! ☢️'}
              </motion.h1>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Cascade Effect Overlay */}
      <AnimatePresence>
        {cascadeMessage && (
          <motion.div
            initial={{ scale: 0, rotate: -10 }}
            animate={{ scale: 1, rotate: 0 }}
            exit={{ scale: 0, rotate: 10 }}
            className="fixed top-24 left-1/2 transform -translate-x-1/2 z-40"
          >
            <div className="bg-gradient-to-r from-red-600 to-orange-600 text-white px-8 py-6 rounded-2xl shadow-2xl">
              <div className="flex items-center gap-4">
                <AlertTriangle className="w-10 h-10 animate-bounce" />
                <div>
                  <h3 className="font-black text-2xl">CASCADE EFFECT!</h3>
                  <p className="text-lg">{cascadeMessage}</p>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Game HUD with Glassmorphic Design */}
      <div className="absolute top-0 left-0 right-0 z-30 p-4">
        <div className="backdrop-blur-xl bg-gradient-to-br from-white/10 to-white/5 rounded-2xl p-6 shadow-2xl border border-white/20">
          
          {/* Character & Turn Info */}
          <div className="flex justify-between items-center mb-4">
            <div className="flex items-center gap-2 sm:gap-4">
              <div className="w-12 h-12 sm:w-16 sm:h-16 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center">
                <span className="text-xl sm:text-2xl">👤</span>
              </div>
              <div>
                <h2 className="text-base sm:text-xl md:text-2xl font-black text-white uppercase truncate max-w-[200px] sm:max-w-none">{selectedCharacter.name}</h2>
                <p className="text-xs sm:text-sm text-purple-400 font-bold truncate">{selectedCharacter.title}</p>
              </div>
            </div>
            
            <div className="flex items-center gap-6">
              {/* Chaos Meter */}
              <div className="flex items-center gap-2">
                <Skull className="w-5 h-5 text-red-500" />
                <div className="w-32 h-3 bg-gray-700 rounded-full overflow-hidden">
                  <motion.div
                    animate={{ width: `${chaos}%` }}
                    className="h-full bg-gradient-to-r from-orange-500 to-red-500"
                  />
                </div>
                <span className="text-sm text-red-400 font-bold">{chaos}%</span>
              </div>
              
              {/* Streak Counter */}
              {streak > 0 && (
                <div className="flex items-center gap-2 animate-pulse">
                  <Zap className="w-5 h-5 text-yellow-400" />
                  <span className="text-yellow-400 font-bold">{streak}x Streak!</span>
                </div>
              )}
              
              {/* Turn Counter */}
              <div className="text-center">
                <p className="text-xs text-gray-400">TURN</p>
                <p className="text-3xl font-black text-white">{turn}/100</p>
              </div>
              
              {/* Sound Toggle */}
              <button
                onClick={() => setSoundEnabled(!soundEnabled)}
                className="p-3 rounded-xl bg-white/10 hover:bg-white/20 transition-all"
              >
                {soundEnabled ? (
                  <Volume2 className="w-5 h-5 text-white" />
                ) : (
                  <VolumeX className="w-5 h-5 text-white" />
                )}
              </button>
            </div>
          </div>
          
          {/* Resource Bars */}
          <div className="grid grid-cols-4 gap-4">
            {Object.entries(resources).map(([key, value]) => {
              const numValue = value as number;
              const icons: {[key: string]: string} = {
                popularity: '👥',
                stability: '🛡️',
                media: '📺',
                economy: '💰'
              };
              
              return (
                <div key={key} className="relative">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span className="text-lg">{icons[key]}</span>
                      <span className="text-sm font-bold text-white capitalize">{key}</span>
                    </div>
                    <span className="text-lg font-black text-white">{numValue}%</span>
                  </div>
                  <div className="h-4 bg-gray-800 rounded-full overflow-hidden shadow-inner">
                    <motion.div
                      initial={false}
                      animate={{ width: `${numValue}%` }}
                      transition={{ type: "spring", stiffness: 100, damping: 15 }}
                      className={`h-full rounded-full relative overflow-hidden ${
                        numValue < 30 ? 'bg-gradient-to-r from-red-600 to-red-500' : 
                        numValue < 50 ? 'bg-gradient-to-r from-yellow-600 to-yellow-500' : 
                        numValue < 70 ? 'bg-gradient-to-r from-blue-600 to-blue-500' : 
                        'bg-gradient-to-r from-green-600 to-green-500'
                      }`}
                    >
                      <div className="absolute inset-0 bg-white/20 animate-pulse" />
                    </motion.div>
                  </div>
                  {numValue < 30 && (
                    <TrendingDown className="absolute -right-8 top-0 w-5 h-5 text-red-500 animate-bounce" />
                  )}
                  {numValue > 80 && (
                    <TrendingUp className="absolute -right-8 top-0 w-5 h-5 text-green-500 animate-bounce" />
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Decision Card */}
      {currentCard && !showEnding && (
        <div className="absolute inset-x-0 bottom-0 z-30 p-2 sm:p-4 md:p-6">
          <motion.div
            initial={{ y: 100, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            className="max-w-7xl mx-auto"
          >
            <div className="backdrop-blur-xl bg-gradient-to-br from-white/15 to-white/5 rounded-2xl sm:rounded-3xl p-4 sm:p-6 md:p-8 shadow-2xl border-2 border-white/30">
              
              {/* Card Header */}
              <div className="mb-4 sm:mb-6">
                <div className="flex items-center justify-between mb-2 sm:mb-3">
                  <span className={`text-xs sm:text-sm font-black uppercase tracking-wider ${
                    showCrisis ? 'text-red-500 animate-pulse' : 'text-yellow-400'
                  }`}>
                    {showCrisis ? '⚠️ CRISIS EVENT ⚠️' : currentCard.category}
                  </span>
                  {showCrisis && (
                    <Star className="w-5 h-5 sm:w-6 sm:h-6 text-red-500 animate-spin" />
                  )}
                </div>
                <h2 className="text-xl sm:text-2xl md:text-3xl lg:text-4xl font-black text-white mb-2 sm:mb-4 leading-tight uppercase tracking-tight">
                  {currentCard.title}
                </h2>
                <p className="text-sm sm:text-base md:text-lg lg:text-xl text-gray-300 leading-relaxed line-clamp-2 sm:line-clamp-none">
                  {currentCard.description}
                </p>
              </div>
              
              {/* Decision Options */}
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2 sm:gap-3 md:gap-4">
                {currentCard.options.map((option: any, index: number) => (
                  <motion.button
                    key={index}
                    whileHover={{ scale: 1.03, rotate: 0.5 }}
                    whileTap={{ scale: 0.97 }}
                    onClick={() => handleDecision(option)}
                    disabled={isDeciding}
                    className={`relative p-3 sm:p-4 md:p-6 rounded-xl sm:rounded-2xl transition-all group backdrop-blur-md ${
                      isDeciding ? 'opacity-50 cursor-not-allowed' : 'hover:shadow-2xl hover:scale-[1.02]'
                    } bg-gradient-to-br ${
                      index === 0 ? 'from-blue-500/25 to-purple-500/25 border-2 border-blue-400/60' :
                      index === 1 ? 'from-green-500/25 to-teal-500/25 border-2 border-green-400/60' :
                      'from-orange-500/25 to-red-500/25 border-2 border-orange-400/60'
                    } shadow-lg`}
                  >
                    <p className="text-white font-black text-sm sm:text-base md:text-lg mb-2 sm:mb-4 leading-tight uppercase tracking-tight">
                      {option.text}
                    </p>
                    
                    {/* Effects Preview */}
                    <div className="grid grid-cols-2 gap-2">
                      {Object.entries(option.effects).map(([resource, value]) => {
                        const numValue = value as number;
                        return (
                          <div key={resource} className="flex items-center gap-2 bg-black/30 rounded-lg px-2 py-1">
                            <span className="text-xs opacity-80 capitalize text-gray-300">
                              {resource}:
                            </span>
                            <span className={`text-sm font-black ${
                              numValue > 0 ? 'text-green-400' : 
                              numValue < 0 ? 'text-red-400' : 
                              'text-gray-400'
                            }`}>
                              {numValue > 0 ? '+' : ''}{numValue}
                            </span>
                          </div>
                        );
                      })}
                    </div>
                    
                    {/* Hover Effect */}
                    <div className="absolute inset-0 bg-gradient-to-br from-white/0 to-white/10 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
                  </motion.button>
                ))}
              </div>
              
              {/* Character Modifier */}
              {selectedCharacter && characterModifiers[selectedCharacter.id as keyof typeof characterModifiers] && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-6 p-4 bg-gradient-to-r from-purple-600/20 to-pink-600/20 rounded-xl border border-purple-500/30"
                >
                  <p className="text-purple-300 font-medium">
                    <span className="text-purple-400 font-bold">🎯 Character Ability:</span>{' '}
                    {characterModifiers[selectedCharacter.id as keyof typeof characterModifiers].description}
                  </p>
                </motion.div>
              )}
            </div>
          </motion.div>
        </div>
      )}

      {/* Audio Element */}
      <audio ref={audioRef} />
    </div>
  );
}
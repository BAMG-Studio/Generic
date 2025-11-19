import React, { useState, useEffect, useRef } from 'react';
import { useGameState } from '../../lib/stores/useGameState';
import { useCharacters } from '../../lib/stores/useCharacters';
import { useResources } from '../../lib/stores/useResources';
import { expandedDecisionCards, crisisCards, cascadeEffects, characterModifiers } from '../../data/expandedCards';
import { motion, AnimatePresence } from 'framer-motion';
import { Volume2, VolumeX, AlertTriangle, TrendingUp, TrendingDown } from 'lucide-react';

interface GameManagerProps {
  children?: React.ReactNode;
}

type ResourceEffects = Record<string, number>;

export default function GameManager({ children }: GameManagerProps) {
  const { gamePhase, turn, nextTurn, endGame } = useGameState();
  const { selectedCharacter } = useCharacters();
  const { resources, updateResources } = useResources();
  
  const [currentCard, setCurrentCard] = useState<any>(null);
  const [cardHistory, setCardHistory] = useState<string[]>([]);
  const [showCrisis, setShowCrisis] = useState(false);
  const [cascadeMessage, setCascadeMessage] = useState<string | null>(null);
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [backgroundVideo, setBackgroundVideo] = useState<string>('/videos/replay-loops/government-office-ambient.mp4');
  const [showCinematic, setShowCinematic] = useState(false);
  const [cinematicType, setCinematicType] = useState<string>('');
  
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const cinematicRef = useRef<HTMLVideoElement | null>(null);

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
    
    // Check for economic collapse
    if (economy < cascadeEffects.economicCollapse.threshold && !cascadeMessage) {
      triggerCascade(cascadeEffects.economicCollapse);
    }
    // Check for civil unrest
    else if (stability < cascadeEffects.civilUnrest.threshold && !cascadeMessage) {
      triggerCascade(cascadeEffects.civilUnrest);
    }
    // Check for media scandal
    else if (media < cascadeEffects.mediaScandal.threshold && !cascadeMessage) {
      triggerCascade(cascadeEffects.mediaScandal);
    }
    // Check for popularity boost
    else if (popularity > cascadeEffects.popularityBoost.threshold && !cascadeMessage) {
      triggerCascade(cascadeEffects.popularityBoost);
    }
  }, [resources]);

  // Trigger cascade effect
  const triggerCascade = (cascade: any) => {
    setCascadeMessage(cascade.message);
    updateResources(cascade.effects);
    playSound('alert');
    
    setTimeout(() => {
      setCascadeMessage(null);
    }, 5000);
  };

  // Check for game ending conditions
  useEffect(() => {
    if (!resources || gamePhase !== 'playing') return;
    
    const { popularity, stability, media, economy } = resources;
    const total = popularity + stability + media + economy;
    
    // Determine ending type
    if (popularity < 25 && stability < 25 && media < 25 && economy < 25) {
      triggerEnding('ending-nuclear-catastrophe');
    } else if (economy < 20) {
      triggerEnding('ending-economic-collapse');
    } else if (stability < 20) {
      triggerEnding('ending-revolution-uprising');
    } else if (media < 30 || popularity < 30) {
      triggerEnding('ending-scandal-impeachment');
    } else if (popularity > 70 && stability > 70 && media > 70 && economy > 70) {
      triggerEnding('ending-victory-triumph');
    } else if (turn >= 100) {
      // Game ends after 100 turns
      triggerEnding(determineEnding());
    }
  }, [resources, turn, gamePhase]);

  // Trigger ending cinematic
  const triggerEnding = (endingType: string) => {
    setCinematicType(endingType);
    setShowCinematic(true);
    playSound('dramatic');
  };

  // Determine ending based on resources
  const determineEnding = () => {
    const { popularity, stability, media, economy } = resources;
    
    if (popularity > 70 && stability > 70 && media > 70 && economy > 70) {
      return 'ending-victory-triumph';
    } else if (economy < 20) {
      return 'ending-economic-collapse';
    } else if (stability < 20) {
      return 'ending-revolution-uprising';
    } else if (media < 30 || popularity < 30) {
      return 'ending-scandal-impeachment';
    } else {
      return 'ending-nuclear-catastrophe';
    }
  };

  // Get next decision card
  const getNextCard = () => {
    // Check if crisis should trigger
    const totalResources = Object.values(resources).reduce((sum, val) => sum + val, 0);
    if (totalResources < 150 && Math.random() < 0.3) {
      return crisisCards[Math.floor(Math.random() * crisisCards.length)];
    }
    
    // Get random card that hasn't been used recently
    let availableCards = expandedDecisionCards.filter(
      card => !cardHistory.includes(card.id)
    );
    
    if (availableCards.length === 0) {
      // Reset history if all cards have been used
      setCardHistory([]);
      availableCards = expandedDecisionCards;
    }
    
    return availableCards[Math.floor(Math.random() * availableCards.length)];
  };

  // Handle decision selection
  const handleDecision = (option: { effects: ResourceEffects }) => {
    if (!selectedCharacter || !currentCard) return;
    
    // Apply character modifiers if available
    let modifiedEffects: ResourceEffects = { ...option.effects };
    const modifierId = selectedCharacter.id as keyof typeof characterModifiers;
    const modifier = characterModifiers[modifierId];
    
    if (modifier) {
      Object.keys(modifiedEffects).forEach(resource => {
        const resourceKey = resource as keyof typeof modifier.modifier;
        if (modifier.modifier[resourceKey]) {
          modifiedEffects[resource as keyof typeof modifiedEffects] = Math.round(
            modifiedEffects[resource as keyof typeof modifiedEffects] * modifier.modifier[resourceKey]
          );
        }
      });
    }
    
    // Apply effects with dramatic flair
    updateResources(modifiedEffects);
    
    // Add to history
    setCardHistory([...cardHistory, currentCard.id]);
    
    // Play appropriate sound
    const totalChange = Object.values(modifiedEffects).reduce(
      (sum: number, val: number) => sum + val,
      0
    );
    if (totalChange > 0) {
      playSound('success');
    } else if (totalChange < -20) {
      playSound('disaster');
    } else {
      playSound('neutral');
    }
    
    // Advance turn
    nextTurn();
    
    // Get next card after a delay
    setTimeout(() => {
      setCurrentCard(getNextCard());
    }, 1000);
  };

  // Play sound effect
  const playSound = (type: string) => {
    if (!soundEnabled) return;
    
    const sounds: { [key: string]: string } = {
      success: '/sounds/success.mp3',
      disaster: '/sounds/disaster.mp3',
      neutral: '/sounds/neutral.mp3',
      alert: '/sounds/alert.mp3',
      dramatic: '/sounds/dramatic.mp3',
      click: '/sounds/click.mp3'
    };
    
    if (audioRef.current) {
      audioRef.current.src = sounds[type] || sounds.click;
      audioRef.current.play().catch(console.error);
    }
  };

  // Initialize game
  useEffect(() => {
    if (gamePhase === 'playing' && !currentCard) {
      setCurrentCard(getNextCard());
    }
  }, [gamePhase]);

  // Handle cinematic end
  const handleCinematicEnd = () => {
    setShowCinematic(false);
    endGame();
  };

  return (
    <div className="relative w-full h-full overflow-hidden">
      {/* Background Video Layer */}
      <div className="absolute inset-0 z-0">
        <video
          src={backgroundVideo}
          autoPlay
          muted
          loop
          playsInline
          className="w-full h-full object-cover opacity-30"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/50 to-transparent" />
      </div>

      {/* Ending Cinematic Overlay */}
      <AnimatePresence>
        {showCinematic && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 bg-black"
          >
            <video
              ref={cinematicRef}
              src={`/videos/ending-cinematics/${cinematicType}.mp4`}
              autoPlay
              muted={!soundEnabled}
              onEnded={handleCinematicEnd}
              className="w-full h-full object-cover"
            />
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center">
                <motion.h1
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 1, type: "spring" }}
                  className="text-6xl font-bold text-white mb-4 drop-shadow-2xl"
                >
                  {cinematicType.includes('victory') ? 'VICTORY!' : 
                   cinematicType.includes('scandal') ? 'SCANDAL!' :
                   cinematicType.includes('economic') ? 'ECONOMIC COLLAPSE!' :
                   cinematicType.includes('revolution') ? 'REVOLUTION!' :
                   'CATASTROPHE!'}
                </motion.h1>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Cascade Effect Overlay */}
      <AnimatePresence>
        {cascadeMessage && (
          <motion.div
            initial={{ y: -100, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: -100, opacity: 0 }}
            className="fixed top-20 left-1/2 transform -translate-x-1/2 z-40 bg-red-600 text-white px-8 py-4 rounded-lg shadow-2xl"
          >
            <div className="flex items-center gap-3">
              <AlertTriangle className="w-8 h-8 animate-pulse" />
              <div>
                <h3 className="font-bold text-lg">CASCADE EFFECT!</h3>
                <p className="text-sm">{cascadeMessage}</p>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Resource Bars */}
      <div className="absolute top-4 left-4 right-4 z-30">
        <div className="bg-black/80 backdrop-blur-lg rounded-lg p-4">
          <div className="grid grid-cols-4 gap-4">
            {Object.entries(resources).map(([key, value]) => {
              const numValue = value as number;
              return (
                <div key={key} className="relative">
                  <div className="flex justify-between mb-1">
                    <span className="text-xs font-bold text-white capitalize">{key}</span>
                    <span className="text-xs font-bold text-white">{numValue}%</span>
                  </div>
                  <div className="h-3 bg-gray-700 rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${numValue}%` }}
                      transition={{ type: "spring", stiffness: 50 }}
                      className={`h-full rounded-full ${
                        numValue < 30 ? 'bg-red-500' : 
                        numValue < 50 ? 'bg-yellow-500' : 
                        numValue < 70 ? 'bg-blue-500' : 
                        'bg-green-500'
                      }`}
                    />
                  </div>
                  {numValue < 30 && (
                    <TrendingDown className="absolute -right-6 top-0 w-4 h-4 text-red-500 animate-pulse" />
                  )}
                  {numValue > 70 && (
                    <TrendingUp className="absolute -right-6 top-0 w-4 h-4 text-green-500 animate-pulse" />
                  )}
                </div>
              );
            })}
          </div>
          <div className="mt-3 flex justify-between items-center">
            <div className="text-white">
              <span className="text-sm opacity-70">Turn</span>
              <span className="text-xl font-bold ml-2">{turn}/100</span>
            </div>
            {selectedCharacter && (
              <div className="text-white text-sm">
                <span className="opacity-70">Leader:</span>
                <span className="font-bold ml-2">{selectedCharacter.name}</span>
              </div>
            )}
            <button
              onClick={() => setSoundEnabled(!soundEnabled)}
              className="p-2 rounded-lg bg-white/10 hover:bg-white/20 transition-colors"
            >
              {soundEnabled ? (
                <Volume2 className="w-5 h-5 text-white" />
              ) : (
                <VolumeX className="w-5 h-5 text-white" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Decision Card */}
      {gamePhase === 'playing' && currentCard && (
        <div className="absolute inset-x-0 bottom-0 z-30 p-8">
          <motion.div
            initial={{ y: 100, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            className="max-w-4xl mx-auto"
          >
            <div className="bg-gradient-to-br from-gray-900/95 to-black/95 backdrop-blur-xl rounded-2xl p-8 shadow-2xl border border-white/10">
              <div className="mb-6">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-bold text-yellow-400 uppercase tracking-wide">
                    {currentCard.category}
                  </span>
                  {showCrisis && currentCard.category === 'crisis' && (
                    <span className="text-red-500 font-bold animate-pulse">CRISIS!</span>
                  )}
                </div>
                <h2 className="text-3xl font-bold text-white mb-3">{currentCard.title}</h2>
                <p className="text-lg text-gray-300 leading-relaxed">{currentCard.description}</p>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {currentCard.options.map((option: { text: string; effects: ResourceEffects }, index: number) => (
                  <motion.button
                    key={index}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => handleDecision(option)}
                    className="relative p-4 bg-gradient-to-br from-blue-600/20 to-purple-600/20 border border-white/20 rounded-xl hover:border-white/40 transition-all group"
                  >
                    <p className="text-white font-medium mb-3">{option.text}</p>
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      {Object.entries(option.effects).map(([resource, value]: [string, number]) => (
                        <div key={resource} className="flex items-center gap-1">
                          <span className="opacity-70 capitalize">{resource}:</span>
                          <span className={`font-bold ${
                            value > 0 ? 'text-green-400' : 
                            value < 0 ? 'text-red-400' : 
                            'text-gray-400'
                          }`}>
                            {value > 0 ? '+' : ''}{value}
                          </span>
                        </div>
                      ))}
                    </div>
                    <div className="absolute inset-0 bg-gradient-to-br from-white/0 to-white/10 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
                  </motion.button>
                ))}
              </div>
              
              {selectedCharacter && characterModifiers[selectedCharacter.id as keyof typeof characterModifiers] && (
                <div className="mt-4 p-3 bg-purple-600/20 rounded-lg border border-purple-500/30">
                  <p className="text-sm text-purple-300">
                    <span className="font-bold">Character Bonus:</span> {characterModifiers[selectedCharacter.id as keyof typeof characterModifiers].description}
                  </p>
                </div>
              )}
            </div>
          </motion.div>
        </div>
      )}

      {/* Audio Element */}
      <audio ref={audioRef} />

      {/* Children (other game components) */}
      <div className="relative z-20">
        {children}
      </div>
    </div>
  );
}
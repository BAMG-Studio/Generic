import { motion, AnimatePresence } from "framer-motion";
import { useState, useEffect, useMemo } from "react";
import { useLocation } from "wouter";
import { ArrowLeft, TrendingUp, TrendingDown } from "lucide-react";
import { useGameState } from "../lib/stores/useGameState";
import { decisionCards } from "../data/cards";
import { useDropboxCards } from "../hooks/useDropboxCards";
import CardDisplay from "../components/Game/CardDisplay";
import AudioSystem from "../components/Audio/AudioSystem";
import { useAudio } from "../lib/stores/useAudio";

interface StatChange {
  label: string;
  value: number;
  color: string;
}

// Fisher-Yates shuffle algorithm for random card selection
const shuffleArray = <T,>(array: T[]): T[] => {
  const shuffled = [...array];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
};

export default function GamePage() {
  const [, setLocation] = useLocation();
  const { selectedCharacter, resources, turn, makeDecision } = useGameState();
  const [statChanges, setStatChanges] = useState<StatChange[]>([]);
  const [previousResources, setPreviousResources] = useState(resources);
  const [showCrisis, setShowCrisis] = useState(false);
  const [crisisVideo, setCrisisVideo] = useState<string>("");
  
  // Load cards from Dropbox, fallback to local data
  const { data: dropboxCards, isLoading: cardsLoading } = useDropboxCards();
  const activeCards = useMemo(() => {
    return (dropboxCards && dropboxCards.length > 0) ? dropboxCards : decisionCards;
  }, [dropboxCards]);

  // Smart randomization: Shuffle cards and track history to prevent repetition
  const [shuffledDeck, setShuffledDeck] = useState<typeof decisionCards>([]);
  const [deckIndex, setDeckIndex] = useState(0);
  const [cardHistory, setCardHistory] = useState<string[]>([]);
  
  // Initialize shuffled deck on mount or when cards change
  useEffect(() => {
    if (activeCards.length > 0) {
      const shuffled = shuffleArray(activeCards);
      setShuffledDeck(shuffled);
      setDeckIndex(0);
      console.log(`Shuffled deck of ${shuffled.length} cards for dynamic gameplay`);
    }
  }, [activeCards]);
  
  // Re-shuffle when deck is exhausted
  useEffect(() => {
    if (deckIndex >= shuffledDeck.length && shuffledDeck.length > 0) {
      const reshuffled = shuffleArray(activeCards);
      setShuffledDeck(reshuffled);
      setDeckIndex(0);
      console.log('Deck exhausted - reshuffling for continued play');
    }
  }, [deckIndex, shuffledDeck.length, activeCards]);

  // Get current card with smart selection to avoid repeats
  const currentCard = useMemo(() => {
    if (shuffledDeck.length === 0) return activeCards[0];
    
    const safeIndex = deckIndex % shuffledDeck.length;
    let selectedCard = shuffledDeck[safeIndex];
    
    // Prevent immediate repeats using history
    if (cardHistory.length > 0 && cardHistory[cardHistory.length - 1] === selectedCard?.id) {
      const nextIndex = (safeIndex + 1) % shuffledDeck.length;
      selectedCard = shuffledDeck[nextIndex];
      console.log('Prevented immediate repeat, skipping to next card');
    }
    
    return selectedCard || activeCards[0];
  }, [shuffledDeck, deckIndex, activeCards, cardHistory]);

  // Track stat changes and show feedback
  useEffect(() => {
    const changes: StatChange[] = [];
    
    if (resources.popularity !== previousResources.popularity) {
      changes.push({
        label: "Popularity",
        value: resources.popularity - previousResources.popularity,
        color: "text-blue-400"
      });
    }
    if (resources.stability !== previousResources.stability) {
      changes.push({
        label: "Stability",
        value: resources.stability - previousResources.stability,
        color: "text-green-400"
      });
    }
    if (resources.media !== previousResources.media) {
      changes.push({
        label: "Media",
        value: resources.media - previousResources.media,
        color: "text-purple-400"
      });
    }
    if (resources.economy !== previousResources.economy) {
      changes.push({
        label: "Economy",
        value: resources.economy - previousResources.economy,
        color: "text-yellow-400"
      });
    }

    if (changes.length > 0) {
      setStatChanges(changes);
      // Clear changes after animation
      setTimeout(() => setStatChanges([]), 2000);
    }

    setPreviousResources(resources);
  }, [resources]);

  const handleChoice = (choiceIndex: number) => {
    makeDecision(currentCard.id, choiceIndex);
    setDeckIndex((prev) => prev + 1);
    setCardHistory((prev) => [...prev, currentCard.id].slice(-10)); // Keep last 10 cards in history
    
    // Trigger crisis news every 5 turns
    const nextTurn = turn + 1;
    if (nextTurn % 5 === 0) {
      const crisisVideos = [
        '/videos/crisis/crisis-economic-crash.mp4',
        '/videos/crisis/crisis-diplomatic-emergency.mp4',
        '/videos/crisis/crisis-cyber-attack.mp4',
        '/videos/crisis/crisis-health-emergency.mp4'
      ];
      const randomCrisis = crisisVideos[Math.floor(Math.random() * crisisVideos.length)];
      setCrisisVideo(randomCrisis);
      setShowCrisis(true);
      
      // Auto-dismiss after 5 seconds
      setTimeout(() => {
        setShowCrisis(false);
      }, 5000);
    }
  };

  // Select event video based on card category and game state
  const getEventVideo = () => {
    const category = currentCard.category.toLowerCase();
    
    if (category.includes('crisis')) {
      return '/videos/replay-loops/breaking-news-ticker.mp4';
    } else if (category.includes('scandal')) {
      return '/videos/replay-loops/media-circus-exterior.mp4';
    } else if (category.includes('economic')) {
      return '/videos/replay-loops/stock-market-displays.mp4';
    } else if (category.includes('policy') || category.includes('legislative')) {
      return '/videos/replay-loops/capitol-building-exterior.mp4';
    } else if (category.includes('military') || category.includes('defense')) {
      return '/videos/replay-loops/government-office-ambient.mp4';
    } else if (category.includes('rally') || category.includes('campaign')) {
      return '/videos/replay-loops/political-rally-crowd.mp4';
    } else if (category.includes('protest')) {
      return '/videos/replay-loops/protest-demonstration.mp4';
    } else {
      return '/videos/replay-loops/press-conference-room.mp4';
    }
  };

  const eventVideo = getEventVideo();

  // Redirect if no character selected (post-render)
  useEffect(() => {
    if (!selectedCharacter) {
      setLocation("/character-select");
    }
  }, [selectedCharacter, setLocation]);

  // Game ending logic - check for win/lose conditions
  useEffect(() => {
    const { popularity, stability, media, economy } = resources;
    
    // Lose condition: Any stat drops to 0 or below
    if (popularity <= 0 || stability <= 0 || media <= 0 || economy <= 0) {
      console.log('Game Over - Resource depletion detected');
      // Navigate to ending page with failure state
      setLocation('/ending?result=fail&reason=resource');
      return;
    }
    
    // Win condition: Turn 50 reached with balanced stats (all above 30)
    if (turn >= 50 && popularity > 30 && stability > 30 && media > 30 && economy > 30) {
      console.log('Victory - 50 turns completed with balanced governance');
      setLocation('/ending?result=win&rank=S');
      return;
    }
    
    // Alternative endings based on turn milestones
    if (turn >= 50) {
      // Calculate average stats to determine ranking
      const avgStats = (popularity + stability + media + economy) / 4;
      let rank = 'F';
      
      if (avgStats >= 70) rank = 'S';
      else if (avgStats >= 60) rank = 'A';
      else if (avgStats >= 50) rank = 'B';
      else if (avgStats >= 40) rank = 'C';
      else if (avgStats >= 30) rank = 'D';
      
      console.log(`Game Complete - Turn 50 reached with rank ${rank}`);
      setLocation(`/ending?result=complete&rank=${rank}`);
    }
  }, [resources, turn, setLocation]);

  if (!selectedCharacter) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-white">Redirecting to character selection...</p>
      </div>
    );
  }

  const stats = [
    { label: "Popularity", value: resources.popularity, color: "bg-blue-500" },
    { label: "Stability", value: resources.stability, color: "bg-green-500" },
    { label: "Media", value: resources.media, color: "bg-purple-500" },
    { label: "Economy", value: resources.economy, color: "bg-yellow-500" },
  ];

  return (
    <div className="relative w-full h-full overflow-hidden">
      {/* Background video */}
      <div className="absolute inset-0">
        <video
          key={eventVideo}
          autoPlay
          loop
          muted
          playsInline
          className="w-full h-full object-cover"
          onError={(e) => {
            console.error('Video playback error:', e);
          }}
        >
          <source src={eventVideo} type="video/mp4" />
        </video>
      </div>

      {/* Gradient overlay for depth */}
      <div className="absolute inset-0 bg-gradient-to-br from-slate-900/40 via-indigo-950/30 to-purple-950/40" />

      {/* Crisis News Overlay - Shows every 5 turns */}
      <AnimatePresence>
        {showCrisis && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            className="absolute inset-0 z-[100] flex items-center justify-center bg-black/80 backdrop-blur-md"
            onClick={() => setShowCrisis(false)}
          >
            <motion.div
              className="relative w-full max-w-5xl aspect-video rounded-3xl overflow-hidden border-4 border-red-500 shadow-2xl"
              initial={{ y: 100 }}
              animate={{ y: 0 }}
              exit={{ y: -100 }}
            >
              {/* Crisis video */}
              <video
                autoPlay
                muted
                playsInline
                className="w-full h-full object-cover"
                src={crisisVideo}
              />
              
              {/* Breaking News Banner */}
              <div className="absolute top-0 left-0 right-0 bg-red-600 py-3 px-6 flex items-center gap-4">
                <span className="animate-pulse text-white font-black text-2xl">🚨 BREAKING NEWS</span>
                <span className="text-white/90 font-semibold text-lg">Crisis Alert - Turn {turn + 1}</span>
              </div>
              
              {/* Click to dismiss hint */}
              <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 bg-black/70 backdrop-blur-sm px-6 py-2 rounded-full">
                <p className="text-white text-sm">Click anywhere to dismiss</p>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Stat change notifications */}
      <AnimatePresence>
        {statChanges.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: -50, scale: 0.8 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -50, scale: 0.8 }}
            className="absolute top-24 left-1/2 transform -translate-x-1/2 z-50 bg-black/80 backdrop-blur-xl rounded-2xl border-2 border-white/30 p-4 shadow-2xl"
          >
            <div className="flex items-center gap-4">
              {statChanges.map((change, index) => (
                <motion.div
                  key={index}
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-center gap-2"
                >
                  {change.value > 0 ? (
                    <TrendingUp className={`w-5 h-5 ${change.color}`} />
                  ) : (
                    <TrendingDown className={`w-5 h-5 ${change.color}`} />
                  )}
                  <span className={`font-bold ${change.color}`}>
                    {change.value > 0 ? '+' : ''}{change.value} {change.label}
                  </span>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Top HUD */}
      <div className="absolute top-0 left-0 right-0 bg-black/30 backdrop-blur-md border-b border-white/20 p-4 z-30">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <button
            onClick={() => setLocation("/menu")}
            className="flex items-center gap-2 text-white/80 hover:text-white transition-colors group"
          >
            <ArrowLeft className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
            <span>Exit to Menu</span>
          </button>

          {/* Character info */}
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-full overflow-hidden border-2 border-yellow-400">
              {selectedCharacter.portraitUrl ? (
                <img src={selectedCharacter.portraitUrl} alt={selectedCharacter.name} className="w-full h-full object-cover" />
              ) : (
                <div className="w-full h-full bg-gradient-to-br from-purple-600 to-pink-600" />
              )}
            </div>
            <div>
              <h3 className="text-white font-bold">{selectedCharacter.name}</h3>
              <p className="text-white/60 text-sm">Turn {turn}</p>
            </div>
          </div>

          {/* Stats with animations */}
          <div className="flex gap-6">
            {stats.map((stat) => {
              const change = statChanges.find(c => c.label === stat.label);
              const changeValue = change?.value ?? 0;
              
              return (
                <motion.div 
                  key={stat.label} 
                  className="text-center"
                  animate={{ scale: change ? [1, 1.1, 1] : 1 }}
                  transition={{ duration: 0.3 }}
                >
                  <div className="text-white/60 text-xs mb-1">{stat.label}</div>
                  <div className="flex items-center gap-2">
                    <div className="w-16 h-2 bg-white/20 rounded-full overflow-hidden">
                      <motion.div
                        className={`h-full ${stat.color}`}
                        initial={false}
                        animate={{ width: `${stat.value}%` }}
                        transition={{ type: "spring", stiffness: 100, damping: 15 }}
                      />
                    </div>
                    <motion.span 
                      className="text-white font-bold text-sm"
                      animate={{ 
                        scale: change ? [1, 1.2, 1] : 1,
                        color: changeValue > 0 
                          ? "#4ade80" 
                          : changeValue < 0
                          ? "#f87171"
                          : "#ffffff"
                      }}
                      transition={{ duration: 0.3 }}
                    >
                      {stat.value}
                    </motion.span>
                  </div>
                </motion.div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Audio System for narration */}
      <AudioSystem muted={isMuted} />

      {/* Main game area - Side by side layout */}
      <div className="relative z-10 h-full pt-20 pb-8 px-8">
        <div className="max-w-7xl mx-auto h-full flex items-center justify-center">
          {/* Card Display Component */}
          <CardDisplay 
            card={currentCard} 
            onSelect={handleDecision}
            disabled={false}
          />
              {/* Card visual - category-specific themes with image support */}
              <div className="absolute inset-0 flex items-center justify-center p-8">
                <div className={`relative w-full h-full rounded-2xl overflow-hidden border-4 shadow-2xl ${
                  currentCard.category === 'economic' ? 'border-green-400/30 bg-gradient-to-br from-green-600/15 via-emerald-600/15 to-teal-600/15' :
                  currentCard.category === 'domestic' ? 'border-blue-400/30 bg-gradient-to-br from-blue-600/15 via-indigo-600/15 to-violet-600/15' :
                  currentCard.category === 'foreign' ? 'border-red-400/30 bg-gradient-to-br from-red-600/15 via-rose-600/15 to-pink-600/15' :
                  currentCard.category === 'social' ? 'border-purple-400/30 bg-gradient-to-br from-purple-600/15 via-fuchsia-600/15 to-pink-600/15' :
                  'border-orange-400/30 bg-gradient-to-br from-orange-600/15 via-red-600/15 to-rose-600/15'
                } backdrop-blur-sm`}>
                  
                  {/* Card image if available */}
                  {currentCard.imageUrl ? (
                    <img 
                      src={currentCard.imageUrl} 
                      alt={currentCard.title}
                      className="absolute inset-0 w-full h-full object-cover"
                      onError={(e) => {
                        console.error('Card image failed to load:', currentCard.imageUrl);
                        (e.target as HTMLImageElement).style.display = 'none';
                      }}
                    />
                  ) : (
                    <>
                      {/* Animated gradient overlay - HIGHLY translucent */}
                      <motion.div 
                        className={`absolute inset-0 ${
                          currentCard.category === 'economic' ? 'bg-gradient-to-br from-green-500/20 via-emerald-500/20 to-teal-500/20' :
                          currentCard.category === 'domestic' ? 'bg-gradient-to-br from-blue-500/20 via-indigo-500/20 to-violet-500/20' :
                          currentCard.category === 'foreign' ? 'bg-gradient-to-br from-red-500/20 via-rose-500/20 to-pink-500/20' :
                          currentCard.category === 'social' ? 'bg-gradient-to-br from-purple-500/20 via-fuchsia-500/20 to-pink-500/20' :
                          'bg-gradient-to-br from-orange-500/20 via-red-500/20 to-rose-500/20'
                        }`}
                        animate={{
                          backgroundPosition: ['0% 0%', '100% 100%', '0% 0%'],
                        }}
                        transition={{
                          duration: 10,
                          repeat: Infinity,
                          ease: "easeInOut"
                        }}
                        style={{
                          backgroundSize: '200% 200%'
                        }}
                      />
                      
                      {/* Large category icon in center - highly transparent */}
                      <div className="absolute inset-0 flex items-center justify-center opacity-25">
                        <span className="text-[16rem] drop-shadow-2xl filter brightness-110">
                          {currentCard.category === 'economic' ? '💸' :
                           currentCard.category === 'domestic' ? '🏛️' :
                           currentCard.category === 'foreign' ? '🌍' :
                           currentCard.category === 'social' ? '👥' : '🚨'}
                        </span>
                      </div>
                    </>
                  )}
                  
                  {/* Category badge with icon */}
                  <div className={`absolute top-4 left-4 bg-black/80 backdrop-blur-md px-6 py-3 rounded-full border-2 z-10 shadow-lg flex items-center gap-2 ${
                    currentCard.category === 'economic' ? 'border-green-300/70' :
                    currentCard.category === 'domestic' ? 'border-blue-300/70' :
                    currentCard.category === 'foreign' ? 'border-red-300/70' :
                    currentCard.category === 'social' ? 'border-purple-300/70' :
                    'border-orange-300/70'
                  }`}>
                    <span className="text-2xl">
                      {currentCard.category === 'economic' ? '💰' :
                       currentCard.category === 'domestic' ? '🏛️' :
                       currentCard.category === 'foreign' ? '🌍' :
                       currentCard.category === 'social' ? '👥' : '🚨'}
                    </span>
                    <p className={`font-black text-base uppercase tracking-wider ${
                      currentCard.category === 'economic' ? 'text-green-200' :
                      currentCard.category === 'domestic' ? 'text-blue-200' :
                      currentCard.category === 'foreign' ? 'text-red-200' :
                      currentCard.category === 'social' ? 'text-purple-200' :
                      'text-orange-200'
                    }`}>{currentCard.category}</p>
                  </div>
                  
                  {/* Card number */}
                  <div className="absolute bottom-4 right-4 w-16 h-16 bg-yellow-400/30 backdrop-blur-md rounded-full flex items-center justify-center border-3 border-yellow-300/70 z-10 shadow-xl">
                    <span className="text-yellow-100 font-black text-2xl">#{turn}</span>
                  </div>
                  
                  {/* Loading indicator */}
                  {cardsLoading && (
                    <div className="absolute inset-0 flex items-center justify-center bg-black/70 backdrop-blur-md z-20">
                      <div className="text-white text-xl font-bold">Loading cards...</div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </motion.div>

          {/* Right: Decision card */}
          <motion.div
            initial={{ x: 100, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            className="flex flex-col justify-center"
          >
            <div className="bg-gradient-to-br from-slate-900/40 to-slate-950/60 backdrop-blur-xl rounded-3xl border-2 border-white/30 p-8 shadow-2xl">
              {/* Card header */}
              <div className="mb-6">
                <div className="flex items-center gap-3 mb-3">
                  <span className="text-4xl">📋</span>
                  <div className="flex-1">
                    <h2 className="text-3xl sm:text-4xl font-black text-transparent bg-gradient-to-r from-yellow-400 via-orange-400 to-red-500 bg-clip-text leading-tight">
                      {currentCard.title}
                    </h2>
                    <p className="text-purple-300 text-base sm:text-lg font-semibold capitalize mt-1">{currentCard.category}</p>
                  </div>
                </div>
              </div>

              {/* Card description */}
              <div className="bg-black/30 backdrop-blur-sm rounded-2xl p-6 mb-6 border-2 border-purple-500/30">
                <p className="text-white text-xl sm:text-2xl font-semibold leading-relaxed">{currentCard.description}</p>
              </div>

              {/* Options */}
              <div className="space-y-4">
                {currentCard.options.map((option, index) => {
                  const optionColors = [
                    "from-blue-600/30 to-cyan-600/30 hover:from-blue-500/50 hover:to-cyan-500/50 border-blue-400/40 hover:border-cyan-300",
                    "from-green-600/30 to-emerald-600/30 hover:from-green-500/50 hover:to-emerald-500/50 border-green-400/40 hover:border-emerald-300",
                    "from-amber-600/30 to-orange-600/30 hover:from-amber-500/50 hover:to-orange-500/50 border-amber-400/40 hover:border-orange-300"
                  ];
                  
                  return (
                    <motion.button
                      key={index}
                      onClick={() => handleChoice(index)}
                      className={`group w-full text-left bg-gradient-to-r ${optionColors[index % 3]} backdrop-blur-sm border-2 rounded-2xl p-6 transition-all duration-300`}
                      whileHover={{ scale: 1.03, x: 10 }}
                      whileTap={{ scale: 0.97 }}
                    >
                      <div className="flex items-start gap-4">
                        <div className="w-10 h-10 rounded-full bg-yellow-400/30 flex items-center justify-center flex-shrink-0 group-hover:bg-yellow-400/50 transition-colors border-2 border-yellow-400/50">
                          <span className="text-yellow-300 font-black text-lg">{String.fromCharCode(65 + index)}</span>
                        </div>
                        <div className="flex-1">
                          <p className="text-white text-xl sm:text-2xl font-bold mb-2 leading-tight">{option.text}</p>
                          <p className="text-yellow-300 text-base font-semibold">Click to decide</p>
                        </div>
                      </div>
                    </motion.button>
                  );
                })}
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}

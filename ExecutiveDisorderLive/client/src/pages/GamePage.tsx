import { motion, AnimatePresence } from "framer-motion";
import { useState, useEffect, useMemo, useRef } from "react";
import { useLocation } from "wouter";
import { ArrowLeft, TrendingUp, TrendingDown } from "lucide-react";
import { useGameState } from "../lib/stores/useGameState";
import { decisionCards } from "../data/cards";
import { satiricalCards } from "../data/satiricalCards";
import { useDropboxCards } from "../hooks/useDropboxCards";
import CardDisplay from "../components/Game/CardDisplay";
import AudioSystem from "../components/Audio/AudioSystem";
import { useAudio } from "../lib/stores/useAudio";
import VisualEffects, { useStatChangeEffects } from "../components/Effects/VisualEffects";
import ParticleEffect from "../components/Effects/ParticleEffect";

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
  const { isMuted } = useAudio();
  
  // Visual effects state - using trigger IDs instead of booleans
  const [screenShakeTrigger, setScreenShakeTrigger] = useState(0);
  const [crisisAlertTrigger, setCrisisAlertTrigger] = useState(0);
  const [showParticles, setShowParticles] = useState(false);
  const [particleType, setParticleType] = useState<'success' | 'danger' | 'warning' | 'info'>('info');
  const { statChanges: visualStatChanges, showStatChange } = useStatChangeEffects();
  
  // Refs to track timeouts for cleanup
  const particleTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const crisisTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  
  // Load cards from Dropbox, fallback to local data, plus satirical cards
  const { data: dropboxCards, isLoading: cardsLoading } = useDropboxCards();
  const activeCards = useMemo(() => {
    // Combine all card sources: Dropbox (185) + Satirical (40) + Local fallback
    const allCards = [
      ...((dropboxCards && dropboxCards.length > 0) ? dropboxCards : decisionCards),
      ...satiricalCards
    ];
    // Filter out any broken cards with missing or insufficient options
    const validCards = allCards.filter(card => card.options && card.options.length >= 2);
    console.log(`Active deck: ${validCards.length} valid cards from ${allCards.length} total (Dropbox: ${dropboxCards?.length || 0}, Satirical: ${satiricalCards.length})`);
    return validCards;
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
    
    // Safety check: ensure card has valid options
    if (!selectedCard || !selectedCard.options || selectedCard.options.length < 2) {
      console.error('⚠️ Broken card detected, using fallback card');
      return activeCards.find(card => card.options && card.options.length >= 2) || activeCards[0];
    }
    
    return selectedCard;
  }, [shuffledDeck, deckIndex, activeCards, cardHistory]);

  // Video backgrounds rotation based on turn
  const eventVideos = [
    "/videos/backgrounds/political-office-animated.mp4",
    "/videos/backgrounds/modern-campaign-rally.mp4",
    "/videos/backgrounds/historic-speech-podium.mp4",
    "/videos/backgrounds/elegant-debate-hall.mp4",
    "/videos/backgrounds/news-studio-broadcast.mp4",
    "/videos/backgrounds/executive-boardroom.mp4"
  ];
  const eventVideo = eventVideos[turn % eventVideos.length];
  
  // Crisis videos triggered every 5 turns
  const crisisVideos = [
    "/videos/events/economic-meltdown-news.mp4",
    "/videos/events/diplomatic-crisis-broadcast.mp4", 
    "/videos/events/social-unrest-coverage.mp4",
    "/videos/events/military-conflict-alert.mp4",
    "/videos/events/environmental-disaster-report.mp4"
  ];

  // Handle decision selection
  const handleDecision = (optionIndex: number) => {
    const option = currentCard.options[optionIndex];
    const changes: StatChange[] = [];
    
    // Determine if this is a critical decision (large stat changes)
    const totalChange = Math.abs(option.effects.popularity) + Math.abs(option.effects.stability) + 
                       Math.abs(option.effects.media) + Math.abs(option.effects.economy);
    const isCritical = totalChange >= 30;
    const isNegative = (option.effects.popularity + option.effects.stability + 
                       option.effects.media + option.effects.economy) < -10;
    
    // Trigger visual effects for critical decisions
    if (isCritical) {
      setScreenShakeTrigger(prev => prev + 1);  // Increment to trigger effect
    }
    
    // Show particles based on decision impact
    if (totalChange >= 20) {
      // Clear any existing particle timeout
      if (particleTimeoutRef.current) {
        clearTimeout(particleTimeoutRef.current);
      }
      
      setParticleType(isNegative ? 'danger' : 'success');
      setShowParticles(true);
      particleTimeoutRef.current = setTimeout(() => setShowParticles(false), 2000);
    }
    
    // Animate resource changes with floating indicators
    const centerX = window.innerWidth / 2;
    const baseY = window.innerHeight / 2;
    let offsetIndex = 0;
    
    if (option.effects.popularity !== 0) {
      changes.push({
        label: "Popularity",
        value: option.effects.popularity,
        color: option.effects.popularity > 0 ? "text-green-400" : "text-red-400"
      });
      showStatChange("Popularity", option.effects.popularity, centerX - 100, baseY + (offsetIndex++ * 40));
    }
    if (option.effects.stability !== 0) {
      changes.push({
        label: "Stability",
        value: option.effects.stability,
        color: option.effects.stability > 0 ? "text-blue-400" : "text-orange-400"
      });
      showStatChange("Stability", option.effects.stability, centerX + 100, baseY + (offsetIndex++ * 40));
    }
    if (option.effects.media !== 0) {
      changes.push({
        label: "Media",
        value: option.effects.media,
        color: option.effects.media > 0 ? "text-purple-400" : "text-pink-400"
      });
      showStatChange("Media", option.effects.media, centerX - 100, baseY + (offsetIndex++ * 40));
    }
    if (option.effects.economy !== 0) {
      changes.push({
        label: "Economy",
        value: option.effects.economy,
        color: option.effects.economy > 0 ? "text-yellow-400" : "text-gray-400"
      });
      showStatChange("Economy", option.effects.economy, centerX + 100, baseY + (offsetIndex++ * 40));
    }
    
    // Show stat changes briefly
    setStatChanges(changes);
    setTimeout(() => setStatChanges([]), 3000);
    
    // Update card history
    setCardHistory(prev => [...prev.slice(-4), currentCard.id]); // Keep last 5 cards
    
    // Apply decision and advance game
    makeDecision(currentCard.id, optionIndex);
    
    // Move to next card
    setDeckIndex(prev => prev + 1);
    
    console.log(`Decision made: ${option.text}, advancing to turn ${turn + 1}`);
  };

  // Check for crisis events every 5 turns
  useEffect(() => {
    if (turn > 0 && turn % 5 === 0) {
      const randomCrisis = crisisVideos[Math.floor(Math.random() * crisisVideos.length)];
      setCrisisVideo(randomCrisis);
      setShowCrisis(true);
      
      // Trigger crisis visual effects
      setCrisisAlertTrigger(prev => prev + 1);  // Increment to trigger effect
      setScreenShakeTrigger(prev => prev + 1);  // Increment to trigger effect
      
      // Clear existing particle timeout and set particles
      if (particleTimeoutRef.current) {
        clearTimeout(particleTimeoutRef.current);
      }
      setParticleType('danger');
      setShowParticles(true);
      particleTimeoutRef.current = setTimeout(() => setShowParticles(false), 2000);
      
      console.log(`Crisis event triggered at turn ${turn}`);
      
      // Auto-hide crisis overlay (particles managed by their own timeout)
      if (crisisTimeoutRef.current) {
        clearTimeout(crisisTimeoutRef.current);
      }
      crisisTimeoutRef.current = setTimeout(() => {
        setShowCrisis(false);
      }, 7000);
    }
  }, [turn]);

  // Redirect if no character selected
  useEffect(() => {
    if (!selectedCharacter) {
      setLocation("/character-select");
    }
  }, [selectedCharacter, setLocation]);

  // Low resource warning effects
  useEffect(() => {
    const { popularity, stability, media, economy } = resources;
    const minResource = Math.min(popularity, stability, media, economy);
    
    if (minResource <= 20 && minResource > 0) {
      // Clear existing particle timeout
      if (particleTimeoutRef.current) {
        clearTimeout(particleTimeoutRef.current);
      }
      
      // Show warning effects for critically low resources
      setParticleType('warning');
      setShowParticles(true);
      particleTimeoutRef.current = setTimeout(() => setShowParticles(false), 1500);
    }
  }, [resources]);

  // Game ending logic - check for win/lose conditions
  useEffect(() => {
    const { popularity, stability, media, economy } = resources;
    
    // Lose condition: Any stat drops to 0 or below
    if (popularity <= 0 || stability <= 0 || media <= 0 || economy <= 0) {
      console.log('Game Over - Resource depletion detected');
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
            className="absolute inset-0 z-[100] flex items-center justify-center bg-black/80 backdrop-blur-md cursor-pointer"
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

      {/* Visual Effects */}
      <VisualEffects 
        screenShakeTrigger={screenShakeTrigger}
        crisisAlertTrigger={crisisAlertTrigger}
        statChanges={visualStatChanges}
      />
      
      {/* Particle Effects */}
      <ParticleEffect 
        active={showParticles}
        type={particleType}
        intensity={50}
      />

      {/* Main game area */}
      <div className="relative z-10 h-full pt-20 pb-8 px-8">
        <div className="max-w-7xl mx-auto h-full flex items-center justify-center">
          {/* Card Display Component */}
          <CardDisplay 
            card={currentCard} 
            onSelect={handleDecision}
            disabled={cardsLoading}
          />
        </div>
      </div>
    </div>
  );
}
import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useGameState } from '../../lib/stores/useGameState';

export default function TitleScreen() {
  const [showPressAnyKey, setShowPressAnyKey] = useState(false);
  const [transitioning, setTransitioning] = useState(false);
  const { setGamePhase } = useGameState();

  // Show "Press Any Key" after logo animation
  useEffect(() => {
    const timer = setTimeout(() => {
      setShowPressAnyKey(true);
    }, 2500);
    return () => clearTimeout(timer);
  }, []);

  // Handle any key press or click
  const handleContinue = useCallback(() => {
    if (!transitioning && showPressAnyKey) {
      setTransitioning(true);
      setTimeout(() => {
        setGamePhase('main_menu');
      }, 500);
    }
  }, [transitioning, showPressAnyKey, setGamePhase]);

  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.key !== 'Tab' && e.key !== 'Shift' && e.key !== 'Control' && e.key !== 'Alt') {
        handleContinue();
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [handleContinue]);

  return (
    <motion.div 
      className="relative w-full h-full overflow-hidden cursor-pointer"
      onClick={handleContinue}
      initial={{ opacity: 0 }}
      animate={{ opacity: transitioning ? 0 : 1 }}
      transition={{ duration: 0.5 }}
    >
      {/* Animated Background */}
      <div className="absolute inset-0 layer-bg visual-bg">
        <div className="absolute inset-0 bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900" />
        <motion.div 
          className="absolute inset-0"
          animate={{
            background: [
              'radial-gradient(circle at 20% 50%, rgba(251, 191, 36, 0.1) 0%, transparent 50%)',
              'radial-gradient(circle at 80% 50%, rgba(220, 38, 38, 0.1) 0%, transparent 50%)',
              'radial-gradient(circle at 50% 50%, rgba(139, 92, 246, 0.1) 0%, transparent 50%)',
              'radial-gradient(circle at 20% 50%, rgba(251, 191, 36, 0.1) 0%, transparent 50%)',
            ]
          }}
          transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
        />
        <div className="absolute inset-0 bg-black/20" />
      </div>

      {/* Main Content */}
      <div className="relative z-10 flex flex-col items-center justify-center h-full px-8">
        {/* Animated Logo */}
        <motion.div
          initial={{ scale: 0, rotate: -180, opacity: 0 }}
          animate={{ scale: 1, rotate: 0, opacity: 1 }}
          transition={{ 
            type: "spring",
            stiffness: 100,
            damping: 20,
            duration: 1.5
          }}
          className="text-center mb-8"
        >
          <motion.h1 
            className="text-6xl sm:text-7xl md:text-8xl lg:text-9xl font-black uppercase tracking-tighter leading-none mb-4"
            initial={{ y: -100 }}
            animate={{ y: 0 }}
            transition={{ delay: 0.3, type: "spring" }}
          >
            <span className="bg-gradient-to-r from-yellow-400 via-orange-500 to-red-500 bg-clip-text text-transparent drop-shadow-[0_0_40px_rgba(251,191,36,0.6)]">
              EXECUTIVE
            </span>
          </motion.h1>
          <motion.h1 
            className="text-6xl sm:text-7xl md:text-8xl lg:text-9xl font-black uppercase tracking-tighter leading-none"
            initial={{ y: 100 }}
            animate={{ y: 0 }}
            transition={{ delay: 0.5, type: "spring" }}
          >
            <span className="bg-gradient-to-r from-red-500 via-purple-500 to-blue-500 bg-clip-text text-transparent drop-shadow-[0_0_40px_rgba(139,92,246,0.6)]">
              DISORDER
            </span>
          </motion.h1>
        </motion.div>

        {/* Tagline */}
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 1, duration: 0.8 }}
          className="mb-12"
        >
          <p className="text-xl sm:text-2xl md:text-3xl text-white/90 font-bold text-center">
            Democracy: <span className="text-yellow-400">Optional</span>. 
            Chaos: <span className="text-red-400">Guaranteed</span>.
          </p>
        </motion.div>

        {/* Opening Monologue */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.5, duration: 1 }}
          className="max-w-3xl mx-auto mb-16 backdrop-blur-md bg-black/30 rounded-2xl p-6 border border-white/10"
        >
          <p className="text-white/80 text-center text-sm sm:text-base md:text-lg leading-relaxed">
            Welcome to the nation where every decision trends, crashes, and spawns a documentary within hours. 
            Your approval rating swings like a caffeinated pendulum, the markets trade on memes, 
            and the press has the collective memory of a goldfish with anxiety.
          </p>
          <p className="text-white/80 text-center text-sm sm:text-base md:text-lg leading-relaxed mt-4">
            Navigate the four pillars of power: Popularity, Stability, Media Trust, and Economic Health. 
            Watch as your tiniest choices cascade into constitutional crises and your grandest plans 
            dissolve into Twitter feuds.
          </p>
          <p className="text-yellow-400 text-center text-base sm:text-lg md:text-xl font-bold mt-6 italic">
            "Democracy dies in darkness. But first, it gets really, really weird."
          </p>
        </motion.div>

        {/* Press Any Key Prompt */}
        <AnimatePresence>
          {showPressAnyKey && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              transition={{ duration: 0.5 }}
            >
              <motion.div
                animate={{ 
                  opacity: [0.5, 1, 0.5],
                  scale: [0.98, 1.02, 0.98]
                }}
                transition={{ 
                  duration: 2,
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
                className="text-center"
              >
                <p className="text-2xl sm:text-3xl text-white font-bold tracking-wider uppercase animate-pulse">
                  Press Any Key to Continue
                </p>
                <p className="text-white/60 text-sm mt-2">
                  Or click/tap anywhere
                </p>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
}
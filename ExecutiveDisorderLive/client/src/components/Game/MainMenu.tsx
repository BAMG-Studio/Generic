import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Play, Volume2, VolumeX, Award, Trophy, Users, Zap } from 'lucide-react';
import { useGameState } from '../../lib/stores/useGameState';

export default function MainMenu() {
  const { setGamePhase } = useGameState();
  const [showCinematic, setShowCinematic] = useState(false);
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [showCredits, setShowCredits] = useState(false);
  const [showInstructions, setShowInstructions] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);
  
  const handleStartGame = () => {
    setShowCinematic(true);
    if (videoRef.current) {
      videoRef.current.play();
    }
  };
  
  const handleCinematicEnd = () => {
    setShowCinematic(false);
    setGamePhase('character_selection');
  };
  
  const handleSkipCinematic = () => {
    if (videoRef.current) {
      videoRef.current.pause();
    }
    handleCinematicEnd();
  };
  
  return (
    <div className="relative w-full h-screen overflow-hidden">
      {/* Animated Background with Multiple Layers */}
      <div className="fixed inset-0 -z-10">
        {/* Gradient Background Base */}
        <div className="absolute inset-0 bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900" />
        
        {/* Animated Gradient Overlay */}
        <div className="absolute inset-0 opacity-50">
          <div className="absolute inset-0 bg-gradient-to-t from-red-600/30 via-transparent to-yellow-600/30 animate-pulse" />
          <div className="absolute inset-0 bg-gradient-to-b from-blue-600/20 via-transparent to-purple-600/20 animate-pulse" style={{ animationDelay: '2s' }} />
        </div>
        
        {/* Background Video with Better Visibility */}
        <video
          src="/videos/replay-loops/capitol-building-exterior.mp4"
          autoPlay
          muted
          loop
          playsInline
          className="absolute inset-0 w-full h-full object-cover mix-blend-screen opacity-40"
        />
        
        {/* Animated Particles/Stars Effect */}
        <div className="absolute inset-0">
          {[...Array(30)].map((_, i) => (
            <div
              key={i}
              className="absolute w-1 h-1 bg-white rounded-full animate-pulse"
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                animationDelay: `${Math.random() * 5}s`,
                animationDuration: `${3 + Math.random() * 4}s`
              }}
            />
          ))}
        </div>
        
        {/* Mesh Gradient Overlay for Depth */}
        <div className="absolute inset-0 bg-gradient-to-tr from-black/40 via-transparent to-black/40" />
      </div>
      
      {/* Main Menu Content */}
      <AnimatePresence mode="wait">
        {!showCinematic && !showCredits && !showInstructions && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="relative z-10 flex flex-col items-center justify-center h-full px-4"
          >
            {/* Logo with Glassmorphic Background */}
            <motion.div
              initial={{ scale: 0, rotate: -180, opacity: 0 }}
              animate={{ scale: 1, rotate: 0, opacity: 1 }}
              transition={{ 
                type: "spring",
                stiffness: 100,
                damping: 20,
                delay: 0.2
              }}
              className="mb-12 text-center px-6 py-8 max-w-6xl backdrop-blur-xl bg-white/5 rounded-3xl border border-white/20 shadow-2xl"
            >
              <motion.h1 
                className="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-black uppercase tracking-tighter leading-none"
                initial={{ y: -50 }}
                animate={{ y: 0 }}
                transition={{ delay: 0.4, type: "spring" }}
              >
                <span className="bg-gradient-to-r from-yellow-400 via-orange-500 to-red-500 bg-clip-text text-transparent drop-shadow-[0_0_30px_rgba(251,191,36,0.5)]">
                  EXECUTIVE
                </span>
              </motion.h1>
              <motion.h2 
                className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-black uppercase tracking-tighter -mt-2 leading-none"
                initial={{ y: 50 }}
                animate={{ y: 0 }}
                transition={{ delay: 0.5, type: "spring" }}
              >
                <span className="bg-gradient-to-r from-red-500 via-purple-500 to-blue-500 bg-clip-text text-transparent drop-shadow-[0_0_30px_rgba(139,92,246,0.5)]">
                  DISORDER
                </span>
              </motion.h2>
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.7, type: "spring" }}
                className="mt-6 inline-block"
              >
                <p className="text-base sm:text-lg md:text-xl lg:text-2xl text-yellow-400 font-black uppercase tracking-wide px-6 py-2 backdrop-blur-md bg-black/30 rounded-full border border-yellow-400/30 shadow-[0_0_20px_rgba(251,191,36,0.3)] animate-pulse">
                  A Satirical Political Card Game
                </p>
              </motion.div>
              <motion.p 
                className="text-sm sm:text-base md:text-lg text-white/80 mt-4 font-bold italic"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.9 }}
              >
                "Where Democracy Meets Pandemonium!"
              </motion.p>
            </motion.div>
            
            {/* Menu Buttons */}
            <motion.div
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="flex flex-col gap-4 w-full max-w-md"
            >
              {/* Start Game Button - Glassmorphic */}
              <motion.button
                whileHover={{ scale: 1.05, rotate: 1, y: -5 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleStartGame}
                className="relative group overflow-hidden backdrop-blur-xl bg-gradient-to-r from-green-500/30 to-emerald-500/30 text-white text-xl sm:text-2xl font-black py-5 sm:py-6 px-8 sm:px-12 rounded-2xl border-2 border-green-400/50 shadow-[0_0_40px_rgba(34,197,94,0.3)] transition-all hover:shadow-[0_0_60px_rgba(34,197,94,0.5)] uppercase tracking-wide"
              >
                <span className="relative z-10 flex items-center justify-center gap-3 sm:gap-4">
                  <Play className="w-6 h-6 sm:w-8 sm:h-8 drop-shadow-[0_0_10px_rgba(255,255,255,0.8)]" />
                  START CHAOS
                </span>
                <motion.div 
                  className="absolute inset-0 bg-gradient-to-r from-yellow-400/20 to-green-400/20"
                  animate={{
                    x: ["0%", "100%", "0%"],
                  }}
                  transition={{
                    duration: 3,
                    repeat: Infinity,
                    ease: "linear"
                  }}
                />
              </motion.button>
              
              {/* Instructions Button - Glassmorphic */}
              <motion.button
                whileHover={{ scale: 1.05, y: -3 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setShowInstructions(true)}
                className="backdrop-blur-xl bg-gradient-to-r from-blue-500/25 to-purple-500/25 text-white text-xl font-bold py-4 px-8 rounded-xl border border-blue-400/40 shadow-[0_0_30px_rgba(59,130,246,0.2)] hover:shadow-[0_0_40px_rgba(59,130,246,0.4)] transition-all flex items-center justify-center gap-3 uppercase"
              >
                <Users className="w-6 h-6 drop-shadow-[0_0_5px_rgba(255,255,255,0.8)]" />
                HOW TO RULE
              </motion.button>
              
              {/* High Scores Button - Glassmorphic */}
              <motion.button
                whileHover={{ scale: 1.05, y: -3 }}
                whileTap={{ scale: 0.95 }}
                className="backdrop-blur-xl bg-gradient-to-r from-yellow-500/25 to-orange-500/25 text-white text-xl font-bold py-4 px-8 rounded-xl border border-yellow-400/40 shadow-[0_0_30px_rgba(251,191,36,0.2)] hover:shadow-[0_0_40px_rgba(251,191,36,0.4)] transition-all flex items-center justify-center gap-3 uppercase"
              >
                <Trophy className="w-6 h-6 drop-shadow-[0_0_5px_rgba(255,255,255,0.8)]" />
                HALL OF INFAMY
              </motion.button>
              
              {/* Credits Button - Glassmorphic */}
              <motion.button
                whileHover={{ scale: 1.05, y: -3 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setShowCredits(true)}
                className="backdrop-blur-xl bg-gradient-to-r from-gray-500/25 to-gray-600/25 text-white text-xl font-bold py-4 px-8 rounded-xl border border-gray-400/40 shadow-[0_0_30px_rgba(156,163,175,0.2)] hover:shadow-[0_0_40px_rgba(156,163,175,0.4)] transition-all flex items-center justify-center gap-3 uppercase"
              >
                <Zap className="w-6 h-6 drop-shadow-[0_0_5px_rgba(255,255,255,0.8)]" />
                CREDITS
              </motion.button>
            </motion.div>
            
            {/* Sound Toggle */}
            <motion.button
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.8 }}
              onClick={() => setSoundEnabled(!soundEnabled)}
              className="absolute top-8 right-8 p-4 bg-white/10 backdrop-blur-md rounded-full hover:bg-white/20 transition-all"
            >
              {soundEnabled ? (
                <Volume2 className="w-6 h-6 text-white" />
              ) : (
                <VolumeX className="w-6 h-6 text-white" />
              )}
            </motion.button>
            
            {/* Satirical Taglines */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1 }}
              className="absolute bottom-8 text-center"
            >
              <p className="text-gray-400 text-sm">
                A political satire game where your decisions actually matter... sort of.
              </p>
              <p className="text-gray-500 text-xs mt-2">
                No actual politicians were harmed in the making of this game.
              </p>
            </motion.div>
          </motion.div>
        )}
        
        {/* Instructions Screen */}
        {showInstructions && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="relative z-10 flex items-center justify-center h-full px-8"
          >
            <div className="bg-black/90 backdrop-blur-2xl rounded-3xl p-12 max-w-4xl border-2 border-yellow-500/30">
              <h2 className="text-5xl font-black text-yellow-400 mb-8 text-center">HOW TO RULE (BADLY)</h2>
              
              <div className="space-y-6 text-white">
                <div className="flex items-start gap-4">
                  <Zap className="w-8 h-8 text-yellow-400 flex-shrink-0 mt-1" />
                  <div>
                    <h3 className="text-2xl font-bold mb-2">Choose Your Chaos Agent</h3>
                    <p className="text-gray-300">
                      Select from 10 hilariously incompetent political characters, each with their own special "talent" for disaster.
                    </p>
                  </div>
                </div>
                
                <div className="flex items-start gap-4">
                  <Zap className="w-8 h-8 text-blue-400 flex-shrink-0 mt-1" />
                  <div>
                    <h3 className="text-2xl font-bold mb-2">Make "Brilliant" Decisions</h3>
                    <p className="text-gray-300">
                      Face 50+ satirical decision cards that affect your Popularity, Stability, Media, and Economy. Try not to destroy everything... or do!
                    </p>
                  </div>
                </div>
                
                <div className="flex items-start gap-4">
                  <Zap className="w-8 h-8 text-red-400 flex-shrink-0 mt-1" />
                  <div>
                    <h3 className="text-2xl font-bold mb-2">Watch the World Burn</h3>
                    <p className="text-gray-300">
                      Experience cascading consequences as your terrible decisions compound. Crisis events appear when chaos reaches critical levels!
                    </p>
                  </div>
                </div>
                
                <div className="flex items-start gap-4">
                  <Zap className="w-8 h-8 text-green-400 flex-shrink-0 mt-1" />
                  <div>
                    <h3 className="text-2xl font-bold mb-2">Achieve "Victory"</h3>
                    <p className="text-gray-300">
                      Survive 100 turns or trigger one of 5 dramatic endings: Victory, Scandal, Economic Collapse, Revolution, or Nuclear Catastrophe!
                    </p>
                  </div>
                </div>
              </div>
              
              <div className="mt-10 p-6 bg-gradient-to-r from-purple-600/20 to-pink-600/20 rounded-2xl border border-purple-500/30">
                <p className="text-purple-300 text-center text-lg font-bold">
                  PRO TIP: Keep all resources balanced! Too low and you'll face disaster, too high and... well, that's suspicious!
                </p>
              </div>
              
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setShowInstructions(false)}
                className="mt-8 w-full bg-gradient-to-r from-yellow-600 to-orange-600 text-white text-xl font-bold py-4 px-8 rounded-xl shadow-xl"
              >
                GOT IT, LET'S CAUSE CHAOS!
              </motion.button>
            </div>
          </motion.div>
        )}
        
        {/* Credits Screen */}
        {showCredits && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="relative z-10 flex items-center justify-center h-full px-8"
          >
            <div className="bg-black/90 backdrop-blur-2xl rounded-3xl p-12 max-w-3xl border-2 border-purple-500/30">
              <h2 className="text-5xl font-black text-purple-400 mb-8 text-center">CREDITS</h2>
              
              <div className="space-y-6 text-white text-center">
                <div>
                  <p className="text-2xl font-bold text-yellow-400 mb-2">Executive Disorder</p>
                  <p className="text-lg text-gray-300">A Political Satire Experience</p>
                </div>
                
                <div>
                  <p className="text-xl font-bold text-blue-400 mb-2">Created with Replit</p>
                  <p className="text-gray-300">The power of AI-assisted development</p>
                </div>
                
                <div>
                  <p className="text-xl font-bold text-green-400 mb-2">Special Thanks</p>
                  <p className="text-gray-300">To democracy, for the endless material</p>
                  <p className="text-gray-300">To politicians, for being themselves</p>
                  <p className="text-gray-300">To satire, for keeping us sane</p>
                </div>
                
                <div className="pt-6 border-t border-gray-700">
                  <p className="text-sm text-gray-400">
                    This is a work of fiction and satire. Any resemblance to actual politicians,
                    living or impeached, or actual events, past or apocalyptic, is purely coincidental.
                  </p>
                </div>
              </div>
              
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setShowCredits(false)}
                className="mt-8 w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white text-xl font-bold py-4 px-8 rounded-xl shadow-xl"
              >
                BACK TO MENU
              </motion.button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
      
      {/* Opening Cinematic Overlay */}
      <AnimatePresence>
        {showCinematic && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 bg-black"
          >
            <video
              ref={videoRef}
              src="/videos/opening-cinematics-final/grand-opening-cinematic.mp4"
              muted={!soundEnabled}
              onEnded={handleCinematicEnd}
              className="w-full h-full object-cover"
            />
            
            {/* Skip Button */}
            <motion.button
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 2 }}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={handleSkipCinematic}
              className="absolute bottom-10 right-10 px-6 py-3 bg-white/20 backdrop-blur-md text-white font-bold rounded-full hover:bg-white/30 transition-all"
            >
              Skip Intro →
            </motion.button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
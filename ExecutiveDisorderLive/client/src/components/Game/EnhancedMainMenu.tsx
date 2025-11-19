import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Play, Users, Settings, Award, Power, Save } from 'lucide-react';
import { useGameState } from '../../lib/stores/useGameState';
import { useCharacters } from '../../lib/stores/useCharacters';
import { characters } from '../../data/characters';
import LeaderCarousel from './LeaderCarousel';
import HeadlineTicker from './HeadlineTicker';
import SettingsModal from './SettingsModal';
import AnalyticsFooter from './AnalyticsFooter';

export default function EnhancedMainMenu() {
  const { setGamePhase } = useGameState();
  const { setSelectedCharacter } = useCharacters();
  const [showSettings, setShowSettings] = useState(false);
  const [hasSaveGame, setHasSaveGame] = useState(false);
  const [selectedLeader, setSelectedLeader] = useState<string | null>(null);

  useEffect(() => {
    // Check for save game
    const saveData = localStorage.getItem('executiveDisorderSave');
    setHasSaveGame(!!saveData);
  }, []);

  const handleNewGame = () => {
    if (selectedLeader) {
      // Set selected character based on carousel selection
      const character = characters.find((c) => c.id === selectedLeader);
      if (character) {
        setSelectedCharacter(character);
        setGamePhase('playing');
      }
    } else {
      setGamePhase('character_selection');
    }
  };

  const handleContinue = () => {
    const saveData = localStorage.getItem('executiveDisorderSave');
    if (saveData) {
      const save = JSON.parse(saveData);
      // Restore game state from save
      setGamePhase('playing');
    }
  };

  const handleQuit = () => {
    // In web environment, just show a message
    alert("You can't escape democracy that easily! (Close the browser tab to quit)");
  };

  return (
    <div className="relative w-full h-full overflow-hidden">
      {/* Dynamic Background */}
      <div className="absolute inset-0 layer-bg visual-bg">
        <div className="absolute inset-0 bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900" />
        <motion.div 
          className="absolute inset-0 opacity-40"
          animate={{
            background: [
              'linear-gradient(45deg, rgba(59,130,246,0.2) 0%, transparent 100%)',
              'linear-gradient(90deg, rgba(236,72,153,0.2) 0%, transparent 100%)',
              'linear-gradient(135deg, rgba(251,191,36,0.2) 0%, transparent 100%)',
              'linear-gradient(180deg, rgba(34,197,94,0.2) 0%, transparent 100%)',
              'linear-gradient(45deg, rgba(59,130,246,0.2) 0%, transparent 100%)',
            ]
          }}
          transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
        />
        <video
          src="/videos/replay-loops/government-office-ambient.mp4"
          autoPlay
          muted
          loop
          playsInline
          className="absolute inset-0 w-full h-full object-cover mix-blend-overlay opacity-20"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-black/30" />
      </div>

      {/* Main Content */}
      <div className="relative layer-menu flex flex-col h-full pointer-events-none">
        {/* Header with Logo */}
        <motion.div
          initial={{ y: -50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.8 }}
          className="pt-8 pb-4 px-8"
        >
          <div className="text-center">
            <h1 className="text-4xl sm:text-5xl md:text-6xl font-black uppercase tracking-tighter">
              <span className="bg-gradient-to-r from-yellow-400 via-orange-500 to-red-500 bg-clip-text text-transparent">
                EXECUTIVE
              </span>
              {' '}
              <span className="bg-gradient-to-r from-red-500 via-purple-500 to-blue-500 bg-clip-text text-transparent">
                DISORDER
              </span>
            </h1>
            <p className="text-white/70 text-sm sm:text-base mt-2 italic">
              A Satirical Political Card Game
            </p>
          </div>
        </motion.div>

        {/* Headline Ticker */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="py-2 border-y border-white/20 backdrop-blur-md bg-black/30 layer-ticker"
        >
          <HeadlineTicker />
        </motion.div>

        {/* Main Menu Area */}
        <div className="flex-1 flex items-center justify-center px-4 sm:px-8 py-4 sm:py-8 overflow-auto pointer-events-auto">
          <div className="max-w-6xl w-full grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-8">
            {/* Left Column: Menu Buttons */}
            <motion.div
              initial={{ x: -50, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ delay: 0.3 }}
              className="flex flex-col justify-center"
            >
              <div className="backdrop-blur-xl bg-white/10 rounded-xl sm:rounded-3xl p-4 sm:p-8 border border-white/20 shadow-2xl">
                <h2 className="text-xl sm:text-2xl font-bold text-white mb-4 sm:mb-6 text-center uppercase tracking-wide">
                  Main Menu
                </h2>
                <div className="space-y-4">
                  {/* New Game Button */}
                  <motion.button
                    whileHover={{ scale: 1.05, x: 10 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={handleNewGame}
                    className="w-full backdrop-blur-md bg-gradient-to-r from-green-500/40 to-emerald-500/40 text-white text-lg sm:text-xl font-bold py-3 sm:py-4 px-4 sm:px-6 rounded-xl border-2 border-green-400/60 shadow-lg hover:shadow-green-400/30 transition-all flex items-center justify-between group min-h-[44px]"
                  >
                    <span className="flex items-center gap-3">
                      <Play className="w-6 h-6" />
                      NEW GAME
                    </span>
                    <span className="text-sm opacity-70 group-hover:opacity-100">
                      {selectedLeader ? 'Start with selected' : 'Choose leader'}
                    </span>
                  </motion.button>

                  {/* Continue Button */}
                  <motion.button
                    whileHover={{ scale: hasSaveGame ? 1.05 : 1, x: hasSaveGame ? 10 : 0 }}
                    whileTap={{ scale: hasSaveGame ? 0.95 : 1 }}
                    onClick={handleContinue}
                    disabled={!hasSaveGame}
                    className={`w-full backdrop-blur-md ${
                      hasSaveGame 
                        ? 'bg-gradient-to-r from-blue-500/40 to-purple-500/40 border-blue-400/60 hover:shadow-blue-400/30' 
                        : 'bg-gray-500/20 border-gray-400/30 opacity-50 cursor-not-allowed'
                    } text-white text-lg sm:text-xl font-bold py-3 sm:py-4 px-4 sm:px-6 rounded-xl border-2 shadow-lg transition-all flex items-center justify-between min-h-[44px]`}
                  >
                    <span className="flex items-center gap-3">
                      <Save className="w-6 h-6" />
                      CONTINUE
                    </span>
                    <span className="text-sm opacity-70">
                      {hasSaveGame ? 'Resume game' : 'No save found'}
                    </span>
                  </motion.button>

                  {/* Character Gallery Button */}
                  <motion.button
                    whileHover={{ scale: 1.05, x: 10 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => setGamePhase('character_selection')}
                    className="w-full backdrop-blur-md bg-gradient-to-r from-yellow-500/40 to-orange-500/40 text-white text-lg sm:text-xl font-bold py-3 sm:py-4 px-4 sm:px-6 rounded-xl border-2 border-yellow-400/60 shadow-lg hover:shadow-yellow-400/30 transition-all flex items-center justify-between min-h-[44px]"
                  >
                    <span className="flex items-center gap-3">
                      <Users className="w-6 h-6" />
                      CHARACTER GALLERY
                    </span>
                    <span className="text-sm opacity-70">View all leaders</span>
                  </motion.button>

                  {/* Settings Button */}
                  <motion.button
                    whileHover={{ scale: 1.05, x: 10 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => setShowSettings(true)}
                    className="w-full backdrop-blur-md bg-gradient-to-r from-purple-500/40 to-pink-500/40 text-white text-lg sm:text-xl font-bold py-3 sm:py-4 px-4 sm:px-6 rounded-xl border-2 border-purple-400/60 shadow-lg hover:shadow-purple-400/30 transition-all flex items-center justify-between min-h-[44px]"
                  >
                    <span className="flex items-center gap-3">
                      <Settings className="w-6 h-6" />
                      SETTINGS
                    </span>
                    <span className="text-sm opacity-70">Audio & gameplay</span>
                  </motion.button>

                  {/* Quit Button */}
                  <motion.button
                    whileHover={{ scale: 1.05, x: 10 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={handleQuit}
                    className="w-full backdrop-blur-md bg-gradient-to-r from-gray-500/40 to-gray-600/40 text-white text-lg sm:text-xl font-bold py-3 sm:py-4 px-4 sm:px-6 rounded-xl border-2 border-gray-400/60 shadow-lg hover:shadow-gray-400/30 transition-all flex items-center justify-between min-h-[44px]"
                  >
                    <span className="flex items-center gap-3">
                      <Power className="w-6 h-6" />
                      QUIT
                    </span>
                    <span className="text-sm opacity-70">Exit game</span>
                  </motion.button>
                </div>
              </div>
            </motion.div>

            {/* Right Column: Leader Carousel */}
            <motion.div
              initial={{ x: 50, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ delay: 0.5 }}
              className="flex flex-col justify-center"
            >
              <div className="backdrop-blur-xl bg-white/10 rounded-xl sm:rounded-3xl p-4 sm:p-8 border border-white/20 shadow-2xl layer-ui">
                <h2 className="text-xl sm:text-2xl font-bold text-white mb-4 sm:mb-6 text-center uppercase tracking-wide">
                  Quick Select Leader
                </h2>
                <LeaderCarousel onSelectLeader={setSelectedLeader} />
              </div>
            </motion.div>
          </div>
        </div>

        {/* Analytics Footer */}
        <motion.div
          initial={{ y: 50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.7 }}
          className="py-4 px-8"
        >
          <AnalyticsFooter />
        </motion.div>
      </div>

      {/* Settings Modal */}
      <AnimatePresence>
        {showSettings && (
          <SettingsModal onClose={() => setShowSettings(false)} />
        )}
      </AnimatePresence>
    </div>
  );
}
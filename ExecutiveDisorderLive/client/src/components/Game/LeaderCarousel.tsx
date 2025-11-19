import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { characters } from '../../data/characters';

interface LeaderCarouselProps {
  onSelectLeader?: (leaderId: string) => void;
}

export default function LeaderCarousel({ onSelectLeader }: LeaderCarouselProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedLeader, setSelectedLeader] = useState<string | null>(null);

  const handlePrevious = () => {
    setCurrentIndex((prev) => (prev === 0 ? characters.length - 1 : prev - 1));
  };

  const handleNext = () => {
    setCurrentIndex((prev) => (prev === characters.length - 1 ? 0 : prev + 1));
  };

  const handleSelect = (leaderId: string) => {
    setSelectedLeader(leaderId);
    onSelectLeader?.(leaderId);
  };

  const getVisibleCharacters = () => {
    const visible = [];
    for (let i = -1; i <= 1; i++) {
      const index = (currentIndex + i + characters.length) % characters.length;
      visible.push({ ...characters[index], position: i });
    }
    return visible;
  };

  return (
    <div className="relative w-full">
      <div className="flex items-center justify-between mb-4">
        <motion.button
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          onClick={handlePrevious}
          className="p-2 rounded-full backdrop-blur-md bg-white/10 border border-white/20 text-white hover:bg-white/20 transition-colors"
        >
          <ChevronLeft className="w-6 h-6" />
        </motion.button>

        <p className="text-white/70 text-sm uppercase tracking-wider">
          {currentIndex + 1} of {characters.length} Leaders
        </p>

        <motion.button
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          onClick={handleNext}
          className="p-2 rounded-full backdrop-blur-md bg-white/10 border border-white/20 text-white hover:bg-white/20 transition-colors"
        >
          <ChevronRight className="w-6 h-6" />
        </motion.button>
      </div>

      <div className="relative h-80 flex items-center justify-center">
        <AnimatePresence mode="popLayout">
          {getVisibleCharacters().map((character) => (
            <motion.div
              key={`${character.id}-${character.position}`}
              initial={{ 
                x: character.position * 300,
                opacity: 0,
                scale: 0.8
              }}
              animate={{ 
                x: character.position * 250,
                opacity: character.position === 0 ? 1 : 0.6,
                scale: character.position === 0 ? 1 : 0.85,
                zIndex: character.position === 0 ? 10 : 5
              }}
              exit={{ 
                opacity: 0,
                scale: 0.8
              }}
              transition={{ 
                type: "spring",
                stiffness: 300,
                damping: 30
              }}
              className={`absolute ${character.position === 0 ? 'cursor-pointer' : 'pointer-events-none'}`}
              onClick={() => character.position === 0 && handleSelect(character.id)}
            >
              <motion.div
                whileHover={{ scale: character.position === 0 ? 1.05 : 1 }}
                className={`backdrop-blur-md rounded-2xl p-6 border-2 shadow-xl transition-all ${
                  selectedLeader === character.id && character.position === 0
                    ? 'bg-gradient-to-br from-yellow-500/30 to-orange-500/30 border-yellow-400/60 shadow-yellow-400/30'
                    : 'bg-white/10 border-white/20'
                }`}
                style={{ width: '220px' }}
              >
                {/* Character Portrait */}
                <div 
                  className="w-32 h-32 mx-auto mb-4 rounded-full border-4 border-white/30"
                  style={{ 
                    backgroundColor: character.themeColor,
                    backgroundImage: character.portraitUrl ? `url(${character.portraitUrl})` : undefined,
                    backgroundSize: 'cover',
                    backgroundPosition: 'center'
                  }}
                >
                  {!character.portraitUrl && (
                    <div className="w-full h-full flex items-center justify-center">
                      <span className="text-4xl font-black text-white/80">
                        {character.name.split(' ').map(n => n[0]).join('')}
                      </span>
                    </div>
                  )}
                </div>

                {/* Character Info */}
                <h3 className="text-white font-bold text-center text-lg mb-1">
                  {character.name}
                </h3>
                <p className="text-white/70 text-center text-xs italic mb-3">
                  {character.title}
                </p>
                <p className="text-white/60 text-center text-xs leading-relaxed">
                  {character.shortBio.substring(0, 60) + '...'}
                </p>

                {/* Selection Indicator */}
                {character.position === 0 && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="mt-4"
                  >
                    <button className={`w-full py-2 rounded-lg font-bold text-sm transition-all ${
                      selectedLeader === character.id
                        ? 'bg-yellow-400 text-black'
                        : 'bg-white/20 text-white hover:bg-white/30'
                    }`}>
                      {selectedLeader === character.id ? '✓ SELECTED' : 'SELECT'}
                    </button>
                  </motion.div>
                )}
              </motion.div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {/* Current Character Details */}
      <div className="mt-6 text-center">
        <p className="text-white/50 text-xs uppercase tracking-wider mb-2">
          {characters[currentIndex].title}
        </p>
        <p className="text-white/70 text-sm italic">
          "Ready to lead... or mislead."
        </p>
      </div>
    </div>
  );
}
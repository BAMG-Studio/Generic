import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { X, Volume2, Music, Zap } from 'lucide-react';

interface SettingsModalProps {
  onClose: () => void;
}

export default function SettingsModal({ onClose }: SettingsModalProps) {
  const [musicVolume, setMusicVolume] = useState(50);
  const [sfxVolume, setSfxVolume] = useState(70);
  const [subtitlesEnabled, setSubtitlesEnabled] = useState(true);
  const [chaosLevel, setChaosLevel] = useState<'normal' | 'chaotic' | 'pandemonium'>('normal');

  useEffect(() => {
    // Load settings from localStorage
    const savedSettings = localStorage.getItem('executiveDisorderSettings');
    if (savedSettings) {
      const settings = JSON.parse(savedSettings);
      setMusicVolume(settings.musicVolume ?? 50);
      setSfxVolume(settings.sfxVolume ?? 70);
      setSubtitlesEnabled(settings.subtitlesEnabled ?? true);
      setChaosLevel(settings.chaosLevel ?? 'normal');
    }
  }, []);

  const saveSettings = () => {
    const settings = {
      musicVolume,
      sfxVolume,
      subtitlesEnabled,
      chaosLevel
    };
    localStorage.setItem('executiveDisorderSettings', JSON.stringify(settings));
    onClose();
  };

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="layer-modal backdrop-blur-md bg-black/50 pointer-events-auto p-4"
      onClick={handleBackdropClick}
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        className="backdrop-blur-xl bg-gradient-to-br from-white/20 to-white/10 rounded-xl sm:rounded-3xl p-4 sm:p-8 max-w-2xl w-full border-2 border-white/30 shadow-2xl max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <h2 className="text-3xl font-black text-white uppercase tracking-tight">
            Settings
          </h2>
          <motion.button
            whileHover={{ scale: 1.1, rotate: 90 }}
            whileTap={{ scale: 0.9 }}
            onClick={onClose}
            className="p-2 rounded-full bg-white/10 hover:bg-white/20 transition-colors"
          >
            <X className="w-6 h-6 text-white" />
          </motion.button>
        </div>

        {/* Audio Settings */}
        <div className="space-y-6 mb-8">
          <div>
            <div className="flex items-center gap-3 mb-3">
              <Music className="w-5 h-5 text-yellow-400" />
              <label className="text-white font-bold text-lg">
                Music Volume: <span className="text-yellow-400">{musicVolume}%</span>
              </label>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              value={musicVolume}
              onChange={(e) => setMusicVolume(Number(e.target.value))}
              className="w-full h-2 bg-white/20 rounded-lg appearance-none cursor-pointer slider"
              style={{
                background: `linear-gradient(to right, #facc15 0%, #facc15 ${musicVolume}%, rgba(255,255,255,0.2) ${musicVolume}%, rgba(255,255,255,0.2) 100%)`
              }}
            />
          </div>

          <div>
            <div className="flex items-center gap-3 mb-3">
              <Volume2 className="w-5 h-5 text-green-400" />
              <label className="text-white font-bold text-lg">
                SFX Volume: <span className="text-green-400">{sfxVolume}%</span>
              </label>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              value={sfxVolume}
              onChange={(e) => setSfxVolume(Number(e.target.value))}
              className="w-full h-2 bg-white/20 rounded-lg appearance-none cursor-pointer slider"
              style={{
                background: `linear-gradient(to right, #4ade80 0%, #4ade80 ${sfxVolume}%, rgba(255,255,255,0.2) ${sfxVolume}%, rgba(255,255,255,0.2) 100%)`
              }}
            />
          </div>
        </div>

        {/* Subtitles Toggle */}
        <div className="mb-8">
          <label className="flex items-center gap-4 cursor-pointer">
            <input
              type="checkbox"
              checked={subtitlesEnabled}
              onChange={(e) => setSubtitlesEnabled(e.target.checked)}
              className="w-6 h-6 rounded border-2 border-white/30 bg-white/10 checked:bg-yellow-400 checked:border-yellow-400 appearance-none cursor-pointer"
              style={{
                backgroundImage: subtitlesEnabled ? `url("data:image/svg+xml,%3Csvg viewBox='0 0 16 16' fill='black' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M12.207 4.793a1 1 0 010 1.414l-5 5a1 1 0 01-1.414 0l-2-2a1 1 0 011.414-1.414L6.5 9.086l4.293-4.293a1 1 0 011.414 0z'/%3E%3C/svg%3E")` : 'none',
                backgroundPosition: 'center',
                backgroundRepeat: 'no-repeat'
              }}
            />
            <span className="text-white font-bold text-lg">
              Enable Subtitles
            </span>
            <span className="text-white/60 text-sm ml-auto">
              {subtitlesEnabled ? 'ON' : 'OFF'}
            </span>
          </label>
        </div>

        {/* Chaos Level */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-4">
            <Zap className="w-5 h-5 text-orange-400" />
            <h3 className="text-white font-bold text-lg">Chaos Level</h3>
          </div>
          <div className="grid grid-cols-3 gap-4">
            {(['normal', 'chaotic', 'pandemonium'] as const).map((level) => (
              <motion.button
                key={level}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setChaosLevel(level)}
                className={`py-3 px-4 rounded-xl font-bold uppercase transition-all border-2 ${
                  chaosLevel === level
                    ? level === 'normal' 
                      ? 'bg-green-500/30 border-green-400 text-green-400 shadow-green-400/30'
                      : level === 'chaotic'
                      ? 'bg-orange-500/30 border-orange-400 text-orange-400 shadow-orange-400/30'
                      : 'bg-red-500/30 border-red-400 text-red-400 shadow-red-400/30'
                    : 'bg-white/10 border-white/20 text-white/60 hover:bg-white/15'
                } shadow-lg`}
              >
                <div className="text-sm">{level}</div>
                <div className="text-xs opacity-70 mt-1">
                  {level === 'normal' ? 'Balanced' : level === 'chaotic' ? 'Wild swings' : 'Total chaos'}
                </div>
              </motion.button>
            ))}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-4">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={saveSettings}
            className="flex-1 backdrop-blur-md bg-gradient-to-r from-green-500/40 to-emerald-500/40 text-white font-bold py-3 rounded-xl border-2 border-green-400/60 shadow-lg hover:shadow-green-400/30 transition-all uppercase"
          >
            Save Settings
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={onClose}
            className="flex-1 backdrop-blur-md bg-white/10 text-white font-bold py-3 rounded-xl border-2 border-white/20 shadow-lg hover:bg-white/15 transition-all uppercase"
          >
            Cancel
          </motion.button>
        </div>
      </motion.div>
    </motion.div>
  );
}
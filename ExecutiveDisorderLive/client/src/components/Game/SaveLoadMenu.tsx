import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Save, Download, Trash2, Clock, User, TrendingUp } from 'lucide-react';
import { useSaveGame } from '../../lib/stores/useSaveGame';

interface SaveLoadMenuProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function SaveLoadMenu({ isOpen, onClose }: SaveLoadMenuProps) {
  const { saves, getSaves, saveGame, loadGame, deleteSave } = useSaveGame();
  const [saveName, setSaveName] = useState('');
  
  useEffect(() => {
    if (isOpen) {
      getSaves();
    }
  }, [isOpen]);
  
  const handleSave = () => {
    saveGame(saveName || 'Manual Save');
    setSaveName('');
    getSaves();
  };
  
  const handleLoad = (id: string) => {
    loadGame(id);
    onClose();
  };
  
  const formatDate = (date: string | Date) => {
    return new Date(date).toLocaleString();
  };
  
  if (!isOpen) return null;
  
  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          className="bg-gradient-to-br from-gray-900 to-black rounded-3xl p-8 max-w-4xl w-full mx-4 border-2 border-white/10"
          onClick={e => e.stopPropagation()}
        >
          <h2 className="text-4xl font-black text-white mb-6 flex items-center gap-3">
            <Save className="w-8 h-8 text-yellow-400" />
            Save & Load Game
          </h2>
          
          {/* Save Game Section */}
          <div className="mb-8 p-6 bg-white/5 rounded-2xl border border-white/10">
            <h3 className="text-xl font-bold text-white mb-4">Save Current Game</h3>
            <div className="flex gap-3">
              <input
                type="text"
                value={saveName}
                onChange={e => setSaveName(e.target.value)}
                placeholder="Enter save name..."
                className="flex-1 px-4 py-3 bg-black/50 text-white rounded-xl border border-white/20 focus:border-yellow-400 focus:outline-none placeholder:text-gray-500"
              />
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleSave}
                className="px-6 py-3 bg-gradient-to-r from-green-600 to-emerald-600 text-white font-bold rounded-xl hover:shadow-green-500/50 shadow-xl transition-all flex items-center gap-2"
              >
                <Save className="w-5 h-5" />
                Save Game
              </motion.button>
            </div>
          </div>
          
          {/* Load Game Section */}
          <div className="p-6 bg-white/5 rounded-2xl border border-white/10">
            <h3 className="text-xl font-bold text-white mb-4">Load Previous Game</h3>
            
            {saves.length === 0 ? (
              <p className="text-gray-400 text-center py-8">No saved games found</p>
            ) : (
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {saves.map(save => (
                  <motion.div
                    key={save.id}
                    whileHover={{ scale: 1.02 }}
                    className="p-4 bg-black/30 rounded-xl border border-white/10 hover:border-yellow-400/50 transition-all"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <h4 className="text-white font-bold text-lg">{save.name}</h4>
                        <div className="flex items-center gap-4 mt-2 text-sm text-gray-400">
                          <span className="flex items-center gap-1">
                            <Clock className="w-4 h-4" />
                            {formatDate(save.timestamp)}
                          </span>
                          <span className="flex items-center gap-1">
                            <User className="w-4 h-4" />
                            {save.character?.name || 'Unknown'}
                          </span>
                          <span className="flex items-center gap-1">
                            <TrendingUp className="w-4 h-4" />
                            Turn {save.turn}
                          </span>
                        </div>
                      </div>
                      
                      <div className="flex gap-2">
                        <motion.button
                          whileHover={{ scale: 1.1 }}
                          whileTap={{ scale: 0.9 }}
                          onClick={() => handleLoad(save.id)}
                          className="p-3 bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-xl hover:shadow-blue-500/50 shadow-lg transition-all"
                        >
                          <Download className="w-5 h-5" />
                        </motion.button>
                        
                        <motion.button
                          whileHover={{ scale: 1.1 }}
                          whileTap={{ scale: 0.9 }}
                          onClick={() => {
                            deleteSave(save.id);
                            getSaves();
                          }}
                          className="p-3 bg-gradient-to-r from-red-600 to-pink-600 text-white rounded-xl hover:shadow-red-500/50 shadow-lg transition-all"
                        >
                          <Trash2 className="w-5 h-5" />
                        </motion.button>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            )}
          </div>
          
          {/* Close Button */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={onClose}
            className="mt-6 w-full py-4 bg-gradient-to-r from-gray-600 to-gray-700 text-white font-bold text-lg rounded-xl hover:shadow-gray-500/50 shadow-xl transition-all"
          >
            Close
          </motion.button>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
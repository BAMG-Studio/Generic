import React from 'react';
import { motion } from 'framer-motion';
import { Trophy, TrendingUp, Award, Users, Zap, Target, BarChart3, Clock } from 'lucide-react';
import { useGameMetrics, useAchievements } from './AchievementSystem';

export default function MetricsDisplay() {
  const { getStatsSummary } = useGameMetrics();
  const { getUnlockedCount, getTotalCount, getCompletionPercentage, achievements } = useAchievements();
  
  const stats = getStatsSummary();
  const legendaryCount = achievements.filter(a => a.unlocked && a.rarity === 'legendary').length;
  const epicCount = achievements.filter(a => a.unlocked && a.rarity === 'epic').length;
  
  return (
    <div className="fixed bottom-4 left-4 z-40">
      <motion.div
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-black/80 backdrop-blur-xl rounded-2xl p-4 border border-white/10 max-w-xs"
      >
        <h3 className="text-white font-bold text-lg mb-3 flex items-center gap-2">
          <BarChart3 className="w-5 h-5 text-yellow-400" />
          Career Stats
        </h3>
        
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div className="bg-white/5 rounded-lg p-2">
            <div className="flex items-center gap-1 text-gray-400 mb-1">
              <Trophy className="w-3 h-3" />
              <span className="text-xs">High Score</span>
            </div>
            <p className="text-white font-bold text-lg">{stats.highScore.toLocaleString()}</p>
          </div>
          
          <div className="bg-white/5 rounded-lg p-2">
            <div className="flex items-center gap-1 text-gray-400 mb-1">
              <Clock className="w-3 h-3" />
              <span className="text-xs">Best Run</span>
            </div>
            <p className="text-white font-bold text-lg">{stats.bestRun} turns</p>
          </div>
          
          <div className="bg-white/5 rounded-lg p-2">
            <div className="flex items-center gap-1 text-gray-400 mb-1">
              <Users className="w-3 h-3" />
              <span className="text-xs">Characters</span>
            </div>
            <p className="text-white font-bold text-lg">{stats.charactersUsed}/10</p>
          </div>
          
          <div className="bg-white/5 rounded-lg p-2">
            <div className="flex items-center gap-1 text-gray-400 mb-1">
              <Zap className="w-3 h-3" />
              <span className="text-xs">Chaos Level</span>
            </div>
            <p className="text-white font-bold text-lg">{Math.min(100, Math.round(stats.chaosGenerated / 100))}%</p>
          </div>
        </div>
        
        <div className="mt-3 pt-3 border-t border-white/10">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-400 text-xs">Achievements</span>
            <span className="text-white font-bold text-sm">{getUnlockedCount()}/{getTotalCount()}</span>
          </div>
          
          <div className="w-full h-2 bg-gray-700 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${getCompletionPercentage()}%` }}
              transition={{ duration: 1, ease: "easeOut" }}
              className="h-full bg-gradient-to-r from-yellow-500 to-orange-500"
            />
          </div>
          
          {legendaryCount > 0 && (
            <div className="flex items-center gap-2 mt-2">
              <Award className="w-4 h-4 text-yellow-400" />
              <span className="text-yellow-400 text-xs font-bold">
                {legendaryCount} Legendary
              </span>
            </div>
          )}
          
          {epicCount > 0 && (
            <div className="flex items-center gap-2 mt-1">
              <Award className="w-4 h-4 text-purple-400" />
              <span className="text-purple-400 text-xs font-bold">
                {epicCount} Epic
              </span>
            </div>
          )}
        </div>
        
        <div className="mt-3 pt-3 border-t border-white/10">
          <div className="flex items-center justify-between">
            <span className="text-gray-400 text-xs">Endings Found</span>
            <div className="flex gap-1">
              {['victory', 'scandal', 'economic', 'revolution', 'nuclear'].map((ending, i) => (
                <div
                  key={ending}
                  className={`w-2 h-2 rounded-full ${
                    stats.endingsFound > i ? 'bg-green-500' : 'bg-gray-600'
                  }`}
                />
              ))}
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, Users, Clock, Award } from 'lucide-react';

interface AnalyticsData {
  totalPlayers: number;
  avgSurvivalDays: number;
  totalGamesPlayed: number;
  mostPopularLeader: string;
  highestScore: number;
  totalChaosCreated: number;
}

export default function AnalyticsFooter() {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Try to load analytics from Dropbox or localStorage
    const loadAnalytics = async () => {
      try {
        // First check localStorage for cached analytics
        const cachedAnalytics = localStorage.getItem('executiveDisorderAnalytics');
        if (cachedAnalytics) {
          setAnalytics(JSON.parse(cachedAnalytics));
        }

        // Try to fetch from Dropbox path (simulated - would need proper API in production)
        // For now, using fallback data
        const mockAnalytics: AnalyticsData = {
          totalPlayers: 12847,
          avgSurvivalDays: 42,
          totalGamesPlayed: 48293,
          mostPopularLeader: "Donald Strump",
          highestScore: 9001,
          totalChaosCreated: 999999
        };

        // Simulate some randomness to make it feel dynamic
        const dynamicAnalytics = {
          ...mockAnalytics,
          totalPlayers: mockAnalytics.totalPlayers + Math.floor(Math.random() * 100),
          totalGamesPlayed: mockAnalytics.totalGamesPlayed + Math.floor(Math.random() * 500),
          avgSurvivalDays: Math.floor(35 + Math.random() * 20)
        };

        setAnalytics(dynamicAnalytics);
        localStorage.setItem('executiveDisorderAnalytics', JSON.stringify(dynamicAnalytics));
      } catch (error) {
        console.log('Analytics not available');
        setAnalytics(null);
      } finally {
        setIsLoading(false);
      }
    };

    loadAnalytics();
  }, []);

  if (isLoading || !analytics) {
    return null;
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="backdrop-blur-md bg-black/30 rounded-2xl px-6 py-3 border border-white/10"
    >
      <div className="flex flex-wrap items-center justify-center gap-6 text-sm">
        {/* Total Players */}
        {analytics.totalPlayers && (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.1 }}
            className="flex items-center gap-2"
          >
            <Users className="w-4 h-4 text-blue-400" />
            <span className="text-white/70">
              <span className="font-bold text-white">{analytics.totalPlayers.toLocaleString()}</span> Leaders
            </span>
          </motion.div>
        )}

        {/* Average Survival */}
        {analytics.avgSurvivalDays && (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2 }}
            className="flex items-center gap-2"
          >
            <Clock className="w-4 h-4 text-green-400" />
            <span className="text-white/70">
              Avg Survival: <span className="font-bold text-white">{analytics.avgSurvivalDays}</span> Days
            </span>
          </motion.div>
        )}

        {/* Total Games */}
        {analytics.totalGamesPlayed && (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.3 }}
            className="flex items-center gap-2"
          >
            <TrendingUp className="w-4 h-4 text-yellow-400" />
            <span className="text-white/70">
              <span className="font-bold text-white">{analytics.totalGamesPlayed.toLocaleString()}</span> Games
            </span>
          </motion.div>
        )}

        {/* Total Chaos */}
        {analytics.totalChaosCreated && (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.4 }}
            className="flex items-center gap-2"
          >
            <Award className="w-4 h-4 text-red-400" />
            <span className="text-white/70">
              Chaos Created: <span className="font-bold text-red-400 animate-pulse">∞</span>
            </span>
          </motion.div>
        )}
      </div>

      {/* Fun Fact */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6 }}
        className="text-center mt-2 text-xs text-white/50 italic"
      >
        "Democracy has been optional {analytics.totalGamesPlayed} times and counting..."
      </motion.div>
    </motion.div>
  );
}
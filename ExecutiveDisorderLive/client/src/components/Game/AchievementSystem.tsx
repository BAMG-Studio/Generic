import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Trophy, Star, Award, Target, Zap, Shield, TrendingUp, Brain } from 'lucide-react';

export interface Achievement {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  unlocked: boolean;
  progress?: number;
  maxProgress?: number;
  rarity: 'common' | 'rare' | 'epic' | 'legendary';
}

interface AchievementNotificationProps {
  achievement: Achievement;
  onDismiss: () => void;
}

const AchievementNotification: React.FC<AchievementNotificationProps> = ({ achievement, onDismiss }) => {
  useEffect(() => {
    const timer = setTimeout(onDismiss, 5000);
    return () => clearTimeout(timer);
  }, [onDismiss]);
  
  const rarityColors = {
    common: 'from-gray-500 to-gray-600',
    rare: 'from-blue-500 to-blue-600',
    epic: 'from-purple-500 to-purple-600',
    legendary: 'from-yellow-500 to-orange-600'
  };
  
  return (
    <motion.div
      initial={{ x: 400, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      exit={{ x: 400, opacity: 0 }}
      transition={{ type: "spring", stiffness: 100, damping: 15 }}
      className="fixed top-24 right-4 z-50"
    >
      <div className={`bg-gradient-to-r ${rarityColors[achievement.rarity]} p-6 rounded-2xl shadow-2xl border-2 border-white/20 backdrop-blur-xl`}>
        <div className="flex items-center gap-4">
          <div className="text-white text-4xl animate-bounce">
            {achievement.icon}
          </div>
          <div>
            <p className="text-white/80 text-sm font-bold uppercase tracking-wider">Achievement Unlocked!</p>
            <h3 className="text-white text-2xl font-black">{achievement.name}</h3>
            <p className="text-white/90 text-sm mt-1">{achievement.description}</p>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export const useAchievements = () => {
  const [achievements, setAchievements] = useState<Achievement[]>([
    {
      id: 'first_decision',
      name: 'Decision Maker',
      description: 'Make your first political decision',
      icon: <Target className="w-8 h-8" />,
      unlocked: false,
      rarity: 'common'
    },
    {
      id: 'survive_10',
      name: 'Political Survivor',
      description: 'Survive 10 turns in office',
      icon: <Shield className="w-8 h-8" />,
      unlocked: false,
      rarity: 'common'
    },
    {
      id: 'survive_50',
      name: 'Career Politician',
      description: 'Survive 50 turns in office',
      icon: <Star className="w-8 h-8" />,
      unlocked: false,
      rarity: 'rare'
    },
    {
      id: 'perfect_balance',
      name: 'Master Balancer',
      description: 'Keep all resources above 60% for 20 turns',
      icon: <TrendingUp className="w-8 h-8" />,
      unlocked: false,
      progress: 0,
      maxProgress: 20,
      rarity: 'epic'
    },
    {
      id: 'crisis_manager',
      name: 'Crisis Manager',
      description: 'Successfully handle 10 crisis events',
      icon: <Zap className="w-8 h-8" />,
      unlocked: false,
      progress: 0,
      maxProgress: 10,
      rarity: 'rare'
    },
    {
      id: 'economic_genius',
      name: 'Economic Genius',
      description: 'Reach 100% economy rating',
      icon: <Award className="w-8 h-8" />,
      unlocked: false,
      rarity: 'epic'
    },
    {
      id: 'beloved_leader',
      name: 'Beloved Leader',
      description: 'Reach 100% popularity',
      icon: <Trophy className="w-8 h-8" />,
      unlocked: false,
      rarity: 'epic'
    },
    {
      id: 'chaos_master',
      name: 'Chaos Master',
      description: 'Reach maximum chaos level',
      icon: <Brain className="w-8 h-8" />,
      unlocked: false,
      rarity: 'legendary'
    },
    {
      id: 'perfect_game',
      name: 'Political Perfection',
      description: 'Complete a game with all resources above 80%',
      icon: <Star className="w-8 h-8" />,
      unlocked: false,
      rarity: 'legendary'
    },
    {
      id: 'disaster_artist',
      name: 'Disaster Artist',
      description: 'Trigger all 5 different endings',
      icon: <Zap className="w-8 h-8" />,
      unlocked: false,
      progress: 0,
      maxProgress: 5,
      rarity: 'legendary'
    }
  ]);
  
  const [notifications, setNotifications] = useState<Achievement[]>([]);
  
  const unlockAchievement = (achievementId: string) => {
    setAchievements(prev => {
      const updated = prev.map(a => {
        if (a.id === achievementId && !a.unlocked) {
          const unlockedAchievement = { ...a, unlocked: true };
          setNotifications(n => [...n, unlockedAchievement]);
          return unlockedAchievement;
        }
        return a;
      });
      return updated;
    });
  };
  
  const updateProgress = (achievementId: string, progress: number) => {
    setAchievements(prev => {
      return prev.map(a => {
        if (a.id === achievementId) {
          const newProgress = Math.min(progress, a.maxProgress || 0);
          if (newProgress === a.maxProgress && !a.unlocked) {
            unlockAchievement(achievementId);
          }
          return { ...a, progress: newProgress };
        }
        return a;
      });
    });
  };
  
  const dismissNotification = (achievementId: string) => {
    setNotifications(prev => prev.filter(a => a.id !== achievementId));
  };
  
  const getUnlockedCount = () => achievements.filter(a => a.unlocked).length;
  const getTotalCount = () => achievements.length;
  const getCompletionPercentage = () => Math.round((getUnlockedCount() / getTotalCount()) * 100);
  
  return {
    achievements,
    notifications,
    unlockAchievement,
    updateProgress,
    dismissNotification,
    getUnlockedCount,
    getTotalCount,
    getCompletionPercentage
  };
};

export interface GameMetrics {
  totalDecisions: number;
  turnsPlayed: number;
  highestTurn: number;
  totalGamesPlayed: number;
  perfectBalanceTurns: number;
  crisisEventsHandled: number;
  cascadeEventsTriggered: number;
  highestPopularity: number;
  highestStability: number;
  highestMedia: number;
  highestEconomy: number;
  lowestPopularity: number;
  lowestStability: number;
  lowestMedia: number;
  lowestEconomy: number;
  totalScore: number;
  highScore: number;
  endingsUnlocked: Set<string>;
  charactersPlayed: Set<string>;
  favoriteCharacter: string | null;
  longestStreak: number;
  totalChaosGenerated: number;
}

export const useGameMetrics = () => {
  const [metrics, setMetrics] = useState<GameMetrics>(() => {
    // Load from localStorage if available
    const saved = localStorage.getItem('executiveDisorderMetrics');
    if (saved) {
      const parsed = JSON.parse(saved);
      return {
        ...parsed,
        endingsUnlocked: new Set(parsed.endingsUnlocked || []),
        charactersPlayed: new Set(parsed.charactersPlayed || [])
      };
    }
    
    return {
      totalDecisions: 0,
      turnsPlayed: 0,
      highestTurn: 0,
      totalGamesPlayed: 0,
      perfectBalanceTurns: 0,
      crisisEventsHandled: 0,
      cascadeEventsTriggered: 0,
      highestPopularity: 50,
      highestStability: 50,
      highestMedia: 50,
      highestEconomy: 50,
      lowestPopularity: 50,
      lowestStability: 50,
      lowestMedia: 50,
      lowestEconomy: 50,
      totalScore: 0,
      highScore: 0,
      endingsUnlocked: new Set(),
      charactersPlayed: new Set(),
      favoriteCharacter: null,
      longestStreak: 0,
      totalChaosGenerated: 0
    };
  });
  
  // Save to localStorage whenever metrics change
  useEffect(() => {
    const toSave = {
      ...metrics,
      endingsUnlocked: Array.from(metrics.endingsUnlocked),
      charactersPlayed: Array.from(metrics.charactersPlayed)
    };
    localStorage.setItem('executiveDisorderMetrics', JSON.stringify(toSave));
  }, [metrics]);
  
  const updateMetric = (key: keyof GameMetrics, value: any) => {
    setMetrics(prev => ({
      ...prev,
      [key]: value
    }));
  };
  
  const incrementMetric = (key: keyof GameMetrics, amount: number = 1) => {
    setMetrics(prev => ({
      ...prev,
      [key]: (prev[key] as number) + amount
    }));
  };
  
  const addToSet = (key: 'endingsUnlocked' | 'charactersPlayed', value: string) => {
    setMetrics(prev => {
      const newSet = new Set(prev[key]);
      newSet.add(value);
      return {
        ...prev,
        [key]: newSet
      };
    });
  };
  
  const trackResourceHighLow = (resources: any) => {
    setMetrics(prev => ({
      ...prev,
      highestPopularity: Math.max(prev.highestPopularity, resources.popularity),
      highestStability: Math.max(prev.highestStability, resources.stability),
      highestMedia: Math.max(prev.highestMedia, resources.media),
      highestEconomy: Math.max(prev.highestEconomy, resources.economy),
      lowestPopularity: Math.min(prev.lowestPopularity, resources.popularity),
      lowestStability: Math.min(prev.lowestStability, resources.stability),
      lowestMedia: Math.min(prev.lowestMedia, resources.media),
      lowestEconomy: Math.min(prev.lowestEconomy, resources.economy)
    }));
  };
  
  const getStatsSummary = () => {
    const winRate = metrics.totalGamesPlayed > 0 
      ? Math.round((metrics.endingsUnlocked.has('ending-victory-triumph') ? 1 : 0) / metrics.totalGamesPlayed * 100)
      : 0;
      
    return {
      gamesPlayed: metrics.totalGamesPlayed,
      decisionsМade: metrics.totalDecisions,
      bestRun: metrics.highestTurn,
      winRate,
      endingsFound: metrics.endingsUnlocked.size,
      charactersUsed: metrics.charactersPlayed.size,
      highScore: metrics.highScore,
      chaosGenerated: metrics.totalChaosGenerated
    };
  };
  
  return {
    metrics,
    updateMetric,
    incrementMetric,
    addToSet,
    trackResourceHighLow,
    getStatsSummary
  };
};

// Achievement Display Component
export const AchievementDisplay: React.FC = () => {
  const { achievements, notifications, dismissNotification } = useAchievements();
  
  return (
    <AnimatePresence>
      {notifications.map(achievement => (
        <AchievementNotification
          key={achievement.id}
          achievement={achievement}
          onDismiss={() => dismissNotification(achievement.id)}
        />
      ))}
    </AnimatePresence>
  );
};
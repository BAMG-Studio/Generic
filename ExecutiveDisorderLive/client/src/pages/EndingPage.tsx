import { motion } from "framer-motion";
import { useLocation } from "wouter";
import { useSearchParams } from "@/lib/hooks/useSearchParams";
import { useGameState } from "@/lib/stores/useGameState";
import { Trophy, RotateCcw, Menu, AlertCircle } from "lucide-react";

export default function EndingPage() {
  const [, setLocation] = useLocation();
  const searchParams = useSearchParams();
  const { selectedCharacter, resources, turn, resetGame } = useGameState();
  
  const result = searchParams.get("result");
  const rank = searchParams.get("rank");
  const reason = searchParams.get("reason");
  
  // Determine ending details based on result
  const getEndingContent = () => {
    if (result === "fail") {
      const failedResource = 
        resources.popularity <= 0 ? "Popularity" :
        resources.stability <= 0 ? "Stability" :
        resources.media <= 0 ? "Media Trust" :
        resources.economy <= 0 ? "Economic Health" : "Resources";
      
      return {
        title: "GAME OVER",
        subtitle: "Your Presidency Has Ended",
        description: `Your ${failedResource} has reached critical levels. The nation has lost confidence in your leadership.`,
        rank: "F",
        color: "from-red-600 to-red-800",
        icon: AlertCircle,
        message: "You've been removed from office!",
        stats: `Lasted ${turn} turns before collapse`
      };
    } else if (result === "win") {
      return {
        title: "VICTORY!",
        subtitle: "Master of Executive Disorder",
        description: `You've successfully navigated 50 turns of political chaos while maintaining balance in all areas!`,
        rank: rank || "S",
        color: "from-yellow-400 to-yellow-600",
        icon: Trophy,
        message: "You're a political genius!",
        stats: `Completed all 50 turns with excellence`
      };
    } else {
      // Complete with various ranks
      const avgStats = (resources.popularity + resources.stability + resources.media + resources.economy) / 4;
      return {
        title: "TERM COMPLETE",
        subtitle: "Your Presidency Has Concluded",
        description: `You survived 50 turns of political madness. History will remember you... somewhat.`,
        rank: rank || "C",
        color: rank === "S" || rank === "A" ? "from-blue-500 to-purple-600" : 
                rank === "B" || rank === "C" ? "from-green-500 to-teal-600" :
                "from-gray-500 to-gray-700",
        icon: Trophy,
        message: getRankMessage(rank || "C"),
        stats: `Final Average: ${Math.round(avgStats)}%`
      };
    }
  };
  
  const getRankMessage = (r: string) => {
    switch(r) {
      case "S": return "Legendary Leader! Future generations will worship you!";
      case "A": return "Outstanding Performance! The history books will be kind!";
      case "B": return "Good Job! You didn't completely ruin everything!";
      case "C": return "Average Performance. At least you tried!";
      case "D": return "Below Average. The nation barely survived!";
      case "F": return "Terrible! You'll be remembered as a cautionary tale!";
      default: return "Your legacy is... complicated.";
    }
  };
  
  const ending = getEndingContent();
  const Icon = ending.icon;
  
  const handlePlayAgain = () => {
    resetGame();
    setLocation("/character-select");
  };
  
  const handleMainMenu = () => {
    resetGame();
    setLocation("/menu");
  };
  
  return (
    <div className="relative w-full h-full overflow-hidden bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Animated background */}
      <div className="absolute inset-0">
        <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-20" />
        <motion.div
          className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-black/60"
          animate={{
            backgroundPosition: ["0% 0%", "100% 100%"],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            repeatType: "reverse",
          }}
        />
      </div>
      
      {/* Main content */}
      <div className="relative z-10 h-full flex flex-col items-center justify-center p-8">
        <motion.div
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.5, type: "spring" }}
          className="max-w-4xl w-full"
        >
          {/* Rank display */}
          <motion.div
            initial={{ y: -50, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="text-center mb-8"
          >
            <div className={`inline-flex items-center justify-center w-32 h-32 rounded-full bg-gradient-to-br ${ending.color} shadow-2xl mb-6`}>
              <span className="text-6xl font-black text-white drop-shadow-lg">{ending.rank}</span>
            </div>
          </motion.div>
          
          {/* Title and message */}
          <motion.div
            initial={{ y: 50, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.4 }}
            className="text-center mb-8"
          >
            <h1 className="text-6xl font-black text-white mb-2 drop-shadow-lg">
              {ending.title}
            </h1>
            <p className="text-2xl text-white/80 mb-4">{ending.subtitle}</p>
            <p className="text-xl text-white/60 max-w-2xl mx-auto mb-4">
              {ending.description}
            </p>
            <p className="text-lg text-yellow-400 font-bold">
              {ending.message}
            </p>
          </motion.div>
          
          {/* Final stats */}
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.6 }}
            className="bg-black/40 backdrop-blur-md rounded-2xl p-6 mb-8"
          >
            <h3 className="text-xl font-bold text-white mb-4 text-center">Final Statistics</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
              <div className="text-center">
                <p className="text-white/60 text-sm">Popularity</p>
                <p className="text-2xl font-bold text-blue-400">{resources.popularity}%</p>
              </div>
              <div className="text-center">
                <p className="text-white/60 text-sm">Stability</p>
                <p className="text-2xl font-bold text-green-400">{resources.stability}%</p>
              </div>
              <div className="text-center">
                <p className="text-white/60 text-sm">Media</p>
                <p className="text-2xl font-bold text-purple-400">{resources.media}%</p>
              </div>
              <div className="text-center">
                <p className="text-white/60 text-sm">Economy</p>
                <p className="text-2xl font-bold text-yellow-400">{resources.economy}%</p>
              </div>
            </div>
            <p className="text-center text-white/70">
              {ending.stats}
            </p>
            {selectedCharacter && (
              <p className="text-center text-white/50 mt-2">
                Playing as {selectedCharacter.name}
              </p>
            )}
          </motion.div>
          
          {/* Action buttons */}
          <motion.div
            initial={{ y: 50, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.8 }}
            className="flex flex-col sm:flex-row gap-4 justify-center"
          >
            <button
              onClick={handlePlayAgain}
              className="flex items-center justify-center gap-2 px-8 py-4 bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white font-bold rounded-xl shadow-lg transform hover:scale-105 transition-all"
            >
              <RotateCcw className="w-5 h-5" />
              <span>Play Again</span>
            </button>
            <button
              onClick={handleMainMenu}
              className="flex items-center justify-center gap-2 px-8 py-4 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-bold rounded-xl shadow-lg transform hover:scale-105 transition-all"
            >
              <Menu className="w-5 h-5" />
              <span>Main Menu</span>
            </button>
          </motion.div>
        </motion.div>
      </div>
    </div>
  );
}
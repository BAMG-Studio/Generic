import { motion } from "framer-motion";
import { useLocation, useParams } from "wouter";
import { ArrowLeft, Play } from "lucide-react";
import { characters } from "../data/characters";
import { useGameState } from "../lib/stores/useGameState";

export default function CharacterStatsPage() {
  const [, setLocation] = useLocation();
  const { id } = useParams();
  const { setSelectedCharacter, startGame } = useGameState();

  const character = characters.find((c) => c.id === id);

  if (!character) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-white">Character not found</p>
      </div>
    );
  }

  const handleStartGame = () => {
    setSelectedCharacter(character);
    startGame();
    setLocation("/game");
  };

  const stats = [
    { label: "Popularity", value: character.startingStats.popularity, color: "from-blue-500 to-cyan-500" },
    { label: "Stability", value: character.startingStats.stability, color: "from-green-500 to-emerald-500" },
    { label: "Media Trust", value: character.startingStats.media, color: "from-purple-500 to-pink-500" },
    { label: "Economy", value: character.startingStats.economy, color: "from-yellow-500 to-orange-500" },
  ];

  // Select background video based on character (all 12 characters mapped)
  const characterVideoMap: Record<string, string> = {
    'rex-scaleston': '/videos/replay-loops/government-office-ambient.mp4',          // Iguana King - official setting
    'tech-disruptor': '/videos/replay-loops/stock-market-displays.mp4',            // Silicon Valleyson - tech/business
    'conspiracy-chief': '/videos/replay-loops/media-circus-exterior.mp4',          // Truther McQuestion - paranoia/media
    'ronald-goldenberg': '/videos/replay-loops/political-rally-crowd.mp4',         // The Dealmaker - populist rallies
    'potus-9000': '/videos/replay-loops/capitol-building-exterior.mp4',            // AI President - government authority
    'alexandria-sanders': '/videos/replay-loops/protest-demonstration.mp4',        // The Progressive - activism
    'richard-moneybags': '/videos/replay-loops/stock-market-displays.mp4',         // Billionaire - finance/markets
    'general-steel': '/videos/replay-loops/capitol-building-exterior.mp4',         // Military leader - government power
    'diana-newsworthy': '/videos/replay-loops/breaking-news-ticker.mp4',           // Media mogul - news/broadcasting
    'johnny-public': '/videos/replay-loops/campaign-headquarters.mp4',             // Everyman - grassroots campaign
    'dr-technocrat': '/videos/replay-loops/government-office-ambient.mp4',         // Expert bureaucrat - office setting
    'senator-tradition': '/videos/replay-loops/press-conference-room.mp4',         // Traditional politician - formal press
  };

  const characterVideo = characterVideoMap[character.id] || '/videos/replay-loops/press-conference-room.mp4';

  return (
    <div className="relative w-full h-full overflow-hidden">
      {/* Background video */}
      <div className="absolute inset-0">
        <video
          key={characterVideo}
          autoPlay
          loop
          muted
          playsInline
          className="w-full h-full object-cover"
        >
          <source src={characterVideo} type="video/mp4" />
        </video>
      </div>

      {/* Gradient overlay for depth */}
      <div className="absolute inset-0 bg-gradient-to-br from-slate-950/50 via-purple-950/40 to-indigo-950/50" />
      {/* Header */}
      <div className="absolute top-0 left-0 right-0 bg-black/20 backdrop-blur-md border-b border-white/20 p-6 flex items-center gap-4 z-20">
        <button
          onClick={() => setLocation("/character-select")}
          className="flex items-center gap-2 text-white/80 hover:text-white transition-colors group"
        >
          <ArrowLeft className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
          <span>Back</span>
        </button>
      </div>

      {/* Main content */}
      <div className="relative z-10 h-full pt-24 pb-8 px-8 flex items-center justify-center">
        <div className="max-w-6xl w-full grid grid-cols-1 lg:grid-cols-2 gap-12">
          {/* Left: Character portrait */}
          <motion.div
            initial={{ x: -100, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            className="flex flex-col items-center"
          >
            <div className="relative w-full max-w-md aspect-[3/4] rounded-3xl overflow-hidden border-4 border-yellow-400/50 shadow-2xl shadow-yellow-400/20">
              {character.portraitUrl ? (
                <img
                  src={character.portraitUrl}
                  alt={character.name}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full bg-gradient-to-br from-purple-600 to-pink-600 flex items-center justify-center">
                  <span className="text-9xl">🎭</span>
                </div>
              )}
              <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent" />
            </div>
            
            <motion.h2
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.2 }}
              className="text-4xl font-black text-white mt-6 text-center"
            >
              {character.name}
            </motion.h2>
            <p className="text-yellow-400 text-xl text-center">{character.title}</p>
          </motion.div>

          {/* Right: Stats and info */}
          <motion.div
            initial={{ x: 100, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            className="flex flex-col justify-center"
          >
            <h3 className="text-3xl font-bold text-white mb-4">Character Stats</h3>
            
            {/* Bio */}
            <div className="bg-black/20 backdrop-blur-lg border border-white/20 rounded-2xl p-6 mb-6">
              <p className="text-white/90 leading-relaxed">{character.fullBio}</p>
            </div>

            {/* Stats bars */}
            <div className="space-y-4 mb-8">
              {stats.map((stat, index) => (
                <motion.div
                  key={stat.label}
                  initial={{ x: 50, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  transition={{ delay: 0.3 + index * 0.1 }}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-white font-semibold">{stat.label}</span>
                    <span className="text-yellow-400 font-bold">{stat.value}</span>
                  </div>
                  <div className="h-3 bg-white/20 backdrop-blur-sm rounded-full overflow-hidden border border-white/10">
                    <motion.div
                      className={`h-full bg-gradient-to-r ${stat.color} rounded-full`}
                      initial={{ width: 0 }}
                      animate={{ width: `${stat.value}%` }}
                      transition={{ delay: 0.5 + index * 0.1, duration: 0.6 }}
                    />
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Abilities */}
            <div className="bg-purple-600/15 backdrop-blur-lg border border-purple-400/40 rounded-2xl p-6 mb-6">
              <h4 className="text-purple-300 font-semibold mb-2">Special Abilities</h4>
              <ul className="text-white space-y-2">
                {character.abilities.map((ability, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <span className="text-yellow-400">•</span>
                    <span>{ability}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Start button */}
            <motion.button
              onClick={handleStartGame}
              className="group relative w-full py-6 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 rounded-2xl font-bold text-2xl text-white transition-all duration-300 shadow-xl hover:shadow-emerald-500/50"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <div className="flex items-center justify-center gap-3">
                <Play className="w-8 h-8" />
                <span>START CAMPAIGN</span>
              </div>
            </motion.button>
          </motion.div>
        </div>
      </div>
    </div>
  );
}

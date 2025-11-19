import { motion } from "framer-motion";
import { useLocation } from "wouter";
import { ArrowLeft, Target, TrendingUp, AlertTriangle, Gamepad2, Trophy, Zap } from "lucide-react";

export default function HowToPlayPage() {
  const [, setLocation] = useLocation();

  return (
    <div className="relative w-full h-full overflow-y-auto">
      {/* Background video */}
      <div className="fixed inset-0 -z-10">
        <video
          autoPlay
          loop
          muted
          playsInline
          className="w-full h-full object-cover"
        >
          <source src="/videos/replay-loops/capitol-building-exterior.mp4" type="video/mp4" />
        </video>
      </div>

      {/* Gradient overlay */}
      <div className="fixed inset-0 -z-10 bg-gradient-to-br from-slate-950/80 via-purple-950/60 to-indigo-950/80" />

      {/* Back button */}
      <motion.button
        initial={{ x: -50, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        onClick={() => setLocation("/menu")}
        className="fixed top-6 left-6 z-50 flex items-center gap-2 px-6 py-3 bg-black/60 backdrop-blur-md border-2 border-white/30 rounded-full text-white font-bold hover:bg-black/80 hover:border-white/50 transition-all"
      >
        <ArrowLeft className="w-5 h-5" />
        Back to Menu
      </motion.button>

      {/* Main content */}
      <div className="relative z-10 max-w-6xl mx-auto px-8 py-24">
        {/* Title */}
        <motion.div
          initial={{ y: -30, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="text-center mb-16"
        >
          <h1 
            className="text-5xl md:text-7xl font-black mb-4"
            style={{
              background: "linear-gradient(135deg, #f59e0b 0%, #ec4899 50%, #8b5cf6 100%)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
            }}
          >
            HOW TO PLAY
          </h1>
          <p className="text-white/70 text-xl">Master the art of political chaos</p>
        </motion.div>

        {/* Game Overview */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="mb-12 bg-gradient-to-br from-blue-600/30 to-indigo-600/40 backdrop-blur-lg border-2 border-white/20 rounded-3xl p-8"
        >
          <div className="flex items-center gap-3 mb-6">
            <Target className="w-8 h-8 text-blue-300" />
            <h2 className="text-3xl font-black text-white">Game Objective</h2>
          </div>
          <p className="text-white/90 text-lg leading-relaxed">
            Navigate the chaotic world of politics by making decisions that balance four critical metrics: <span className="text-green-400 font-bold">Popularity</span>, <span className="text-blue-400 font-bold">Stability</span>, <span className="text-purple-400 font-bold">Media</span>, and <span className="text-yellow-400 font-bold">Economy</span>. Survive 20 turns and achieve your character's unique ending based on your performance!
          </p>
        </motion.section>

        {/* Core Mechanics */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mb-12 bg-gradient-to-br from-purple-600/30 to-pink-600/40 backdrop-blur-lg border-2 border-white/20 rounded-3xl p-8"
        >
          <div className="flex items-center gap-3 mb-6">
            <Gamepad2 className="w-8 h-8 text-purple-300" />
            <h2 className="text-3xl font-black text-white">Core Mechanics</h2>
          </div>
          <div className="space-y-4 text-white/90">
            <div className="bg-black/40 backdrop-blur-sm rounded-2xl p-6">
              <h3 className="text-xl font-bold text-purple-300 mb-3">📋 Decision Cards</h3>
              <p className="leading-relaxed">Each turn presents a unique scenario with 3 choices. Every decision impacts your 4 metrics differently. Choose wisely - or hilariously!</p>
            </div>
            <div className="bg-black/40 backdrop-blur-sm rounded-2xl p-6">
              <h3 className="text-xl font-bold text-green-300 mb-3">💰 Resource Management</h3>
              <ul className="space-y-2 ml-6 list-disc">
                <li><span className="text-green-400 font-bold">Popularity:</span> Public approval rating (0-100)</li>
                <li><span className="text-blue-400 font-bold">Stability:</span> Government stability (0-100)</li>
                <li><span className="text-purple-400 font-bold">Media:</span> Media perception (0-100)</li>
                <li><span className="text-yellow-400 font-bold">Economy:</span> Economic health (0-100)</li>
              </ul>
              <p className="mt-4 text-yellow-300 font-bold">⚠️ If ANY metric drops to 0, it's game over!</p>
            </div>
            <div className="bg-black/40 backdrop-blur-sm rounded-2xl p-6">
              <h3 className="text-xl font-bold text-red-300 mb-3">🚨 Crisis Events</h3>
              <p className="leading-relaxed">Every 5 turns, a major crisis strikes! Watch breaking news coverage and brace for impact. These can dramatically shift the political landscape.</p>
            </div>
          </div>
        </motion.section>

        {/* Strategy Guide */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="mb-12 bg-gradient-to-br from-amber-600/30 to-orange-600/40 backdrop-blur-lg border-2 border-white/20 rounded-3xl p-8"
        >
          <div className="flex items-center gap-3 mb-6">
            <TrendingUp className="w-8 h-8 text-amber-300" />
            <h2 className="text-3xl font-black text-white">Winning Strategies</h2>
          </div>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-black/40 backdrop-blur-sm rounded-2xl p-6">
              <h3 className="text-xl font-bold text-green-400 mb-3">✅ DO:</h3>
              <ul className="space-y-2 text-white/90">
                <li>• Balance all 4 metrics - ignoring one leads to failure</li>
                <li>• Play to your character's strengths and strategy</li>
                <li>• Anticipate crisis events every 5 turns</li>
                <li>• Read card categories (Economic, Domestic, Foreign, Social, Crisis) for hints</li>
                <li>• Adapt your strategy based on current metrics</li>
              </ul>
            </div>
            <div className="bg-black/40 backdrop-blur-sm rounded-2xl p-6">
              <h3 className="text-xl font-bold text-red-400 mb-3">❌ DON'T:</h3>
              <ul className="space-y-2 text-white/90">
                <li>• Let any metric fall below 20 (danger zone!)</li>
                <li>• Make extreme decisions unless desperate</li>
                <li>• Ignore your character's faction alignment</li>
                <li>• Focus only on popularity - balance is key</li>
                <li>• Panic during crises - they're opportunities too!</li>
              </ul>
            </div>
          </div>
        </motion.section>

        {/* Character Strategies */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="mb-12 bg-gradient-to-br from-rose-600/30 to-pink-600/40 backdrop-blur-lg border-2 border-white/20 rounded-3xl p-8"
        >
          <div className="flex items-center gap-3 mb-6">
            <Zap className="w-8 h-8 text-rose-300" />
            <h2 className="text-3xl font-black text-white">Character-Specific Tips</h2>
          </div>
          <div className="grid md:grid-cols-3 gap-4 text-white/90">
            <div className="bg-black/40 backdrop-blur-sm rounded-xl p-5">
              <h4 className="font-bold text-blue-400 mb-2">💼 Establishment Leaders</h4>
              <p className="text-sm">Focus on stability and media. Slow, steady decisions win the game.</p>
            </div>
            <div className="bg-black/40 backdrop-blur-sm rounded-xl p-5">
              <h4 className="font-bold text-red-400 mb-2">🔥 Populist Firebrands</h4>
              <p className="text-sm">High risk, high reward. Boost popularity but watch stability closely.</p>
            </div>
            <div className="bg-black/40 backdrop-blur-sm rounded-xl p-5">
              <h4 className="font-bold text-purple-400 mb-2">🌟 Wildcards</h4>
              <p className="text-sm">Chaos is your friend. Unpredictable choices create unique opportunities.</p>
            </div>
            <div className="bg-black/40 backdrop-blur-sm rounded-xl p-5">
              <h4 className="font-bold text-green-400 mb-2">💰 Economic Focused</h4>
              <p className="text-sm">Prioritize economy and stability. Money talks in politics.</p>
            </div>
            <div className="bg-black/40 backdrop-blur-sm rounded-xl p-5">
              <h4 className="font-bold text-yellow-400 mb-2">🌍 Foreign Policy Experts</h4>
              <p className="text-sm">Balance domestic needs with international relations carefully.</p>
            </div>
            <div className="bg-black/40 backdrop-blur-sm rounded-xl p-5">
              <h4 className="font-bold text-orange-400 mb-2">🤖 Tech Visionaries</h4>
              <p className="text-sm">Innovation drives progress. Embrace change but manage fallout.</p>
            </div>
          </div>
        </motion.section>

        {/* Endings & Rankings */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="mb-12 bg-gradient-to-br from-emerald-600/30 to-teal-600/40 backdrop-blur-lg border-2 border-white/20 rounded-3xl p-8"
        >
          <div className="flex items-center gap-3 mb-6">
            <Trophy className="w-8 h-8 text-emerald-300" />
            <h2 className="text-3xl font-black text-white">Endings & Rankings</h2>
          </div>
          <p className="text-white/90 text-lg mb-6">Complete all 20 turns to unlock your ending! Rankings are based on your final performance:</p>
          <div className="grid md:grid-cols-4 gap-4">
            <div className="bg-gradient-to-br from-yellow-500/20 to-amber-500/30 backdrop-blur-sm rounded-xl p-5 border border-yellow-400/40">
              <div className="text-4xl mb-2">🏆</div>
              <h4 className="font-black text-yellow-300 mb-1">S Rank</h4>
              <p className="text-sm text-white/80">Legendary leader! All metrics above 70.</p>
            </div>
            <div className="bg-gradient-to-br from-green-500/20 to-emerald-500/30 backdrop-blur-sm rounded-xl p-5 border border-green-400/40">
              <div className="text-4xl mb-2">🥇</div>
              <h4 className="font-black text-green-300 mb-1">A Rank</h4>
              <p className="text-sm text-white/80">Excellent! Most metrics above 60.</p>
            </div>
            <div className="bg-gradient-to-br from-blue-500/20 to-cyan-500/30 backdrop-blur-sm rounded-xl p-5 border border-blue-400/40">
              <div className="text-4xl mb-2">🥈</div>
              <h4 className="font-black text-blue-300 mb-1">B-D Rank</h4>
              <p className="text-sm text-white/80">Survived! Mixed results.</p>
            </div>
            <div className="bg-gradient-to-br from-red-500/20 to-rose-500/30 backdrop-blur-sm rounded-xl p-5 border border-red-400/40">
              <div className="text-4xl mb-2">💥</div>
              <h4 className="font-black text-red-300 mb-1">F Rank</h4>
              <p className="text-sm text-white/80">Disaster! Any metric reached 0.</p>
            </div>
          </div>
        </motion.section>

        {/* Controls */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="mb-12 bg-gradient-to-br from-indigo-600/30 to-violet-600/40 backdrop-blur-lg border-2 border-white/20 rounded-3xl p-8"
        >
          <div className="flex items-center gap-3 mb-6">
            <AlertTriangle className="w-8 h-8 text-indigo-300" />
            <h2 className="text-3xl font-black text-white">Controls & Tips</h2>
          </div>
          <div className="space-y-4 text-white/90">
            <p className="text-lg"><span className="text-purple-400 font-bold">🖱️ Mouse/Touch:</span> Click any decision option to select it</p>
            <p className="text-lg"><span className="text-blue-400 font-bold">📱 Mobile Optimized:</span> Fully responsive for all devices</p>
            <p className="text-lg"><span className="text-green-400 font-bold">💡 Pro Tip:</span> Each character has 500 unique cards - games never play the same twice!</p>
            <p className="text-lg"><span className="text-yellow-400 font-bold">🎯 Smart Play:</span> Cards are randomly selected to ensure variety and avoid repetition</p>
          </div>
        </motion.section>

        {/* Call to Action */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.8 }}
          className="text-center"
        >
          <button
            onClick={() => setLocation("/character-select")}
            className="px-12 py-6 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white text-2xl font-black rounded-full border-4 border-white/30 hover:border-white/50 transition-all shadow-2xl hover:shadow-purple-500/50"
          >
            START PLAYING →
          </button>
        </motion.div>
      </div>
    </div>
  );
}

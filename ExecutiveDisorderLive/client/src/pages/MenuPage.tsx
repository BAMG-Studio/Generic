import { motion } from "framer-motion";
import { useLocation } from "wouter";
import { Play, Users, Settings, Info } from "lucide-react";

export default function MenuPage() {
  const [, setLocation] = useLocation();

  const menuItems = [
    {
      icon: Play,
      label: "NEW GAME",
      subtitle: "Choose leader",
      gradient: "from-emerald-600/40 to-teal-600/60",
      action: () => setLocation("/character-select"),
    },
    {
      icon: Play,
      label: "CONTINUE",
      subtitle: "No save found",
      gradient: "from-slate-600/30 to-slate-700/50",
      action: () => alert("No save game found"),
      disabled: true,
    },
    {
      icon: Users,
      label: "CHARACTER GALLERY",
      subtitle: "View all leaders",
      gradient: "from-amber-600/40 to-orange-600/60",
      action: () => setLocation("/character-select"),
    },
    {
      icon: Info,
      label: "HOW TO PLAY?",
      subtitle: "Rules & strategy",
      gradient: "from-cyan-600/40 to-blue-600/60",
      action: () => setLocation("/how-to-play"),
    },
    {
      icon: Settings,
      label: "SETTINGS",
      subtitle: "Audio & gameplay",
      gradient: "from-purple-600/40 to-pink-600/60",
      action: () => alert("Settings coming soon"),
    },
  ];

  return (
    <div className="relative w-full h-full overflow-hidden">
      {/* Background video */}
      <div className="absolute inset-0">
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

      {/* Gradient overlay for depth */}
      <div className="absolute inset-0 bg-gradient-to-br from-indigo-950/60 via-purple-950/40 to-slate-950/60" />
      
      {/* Animated grid overlay */}
      <div className="absolute inset-0 opacity-10">
        <div className="h-full w-full" 
          style={{
            backgroundImage: `
              linear-gradient(to right, white 1px, transparent 1px),
              linear-gradient(to bottom, white 1px, transparent 1px)
            `,
            backgroundSize: '50px 50px'
          }}
        />
      </div>

      {/* Headline ticker */}
      <div className="absolute top-0 left-0 right-0 bg-black/20 backdrop-blur-md border-b border-white/20 py-3 overflow-hidden">
        <motion.div
          className="whitespace-nowrap text-white/70"
          animate={{ x: [0, -1000] }}
          transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
        >
          <span className="mx-8">🔥 BREAKING: Nation replaces currency with cryptocurrency called 'FREEDOMCOIN'</span>
          <span className="mx-8">⚡ URGENT: Congress votes to make pizza a vegetable again, nutritionists weep</span>
          <span className="mx-8">💥 CHAOS: Supreme Court rules that memes are now legally binding contracts</span>
          <span className="mx-8">🌪️ TRENDING: Presidential approval rating now measured in TikTok followers</span>
        </motion.div>
      </div>

      {/* Main content */}
      <div className="relative z-10 flex flex-col items-center justify-center h-full px-8 pt-16">
        {/* Logo/Title */}
        <motion.div
          initial={{ y: -50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="text-center mb-12"
        >
          <h1 
            className="text-5xl md:text-7xl font-black mb-2"
            style={{
              background: "linear-gradient(135deg, #f59e0b 0%, #ec4899 50%, #8b5cf6 100%)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
            }}
          >
            EXECUTIVE DISORDER
          </h1>
          <p className="text-white/60 text-lg italic">A Satirical Political Card Game</p>
        </motion.div>

        {/* Menu grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl w-full">
          {menuItems.map((item, index) => (
            <motion.button
              key={item.label}
              onClick={item.action}
              disabled={item.disabled}
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: index * 0.1, duration: 0.4 }}
              className={`
                group relative overflow-hidden rounded-2xl p-6 text-left
                bg-gradient-to-br ${item.gradient} backdrop-blur-lg border-2 border-white/20
                ${item.disabled ? 'opacity-50 cursor-not-allowed' : 'hover:scale-105 cursor-pointer hover:border-white/40'}
                transition-all duration-300 shadow-xl
              `}
              whileHover={!item.disabled ? { scale: 1.05 } : {}}
              whileTap={!item.disabled ? { scale: 0.98 } : {}}
            >
              <div className="relative z-10 flex items-start gap-4">
                <item.icon className="w-8 h-8 text-white" />
                <div className="flex-1">
                  <h3 className="text-2xl font-bold text-white mb-1">{item.label}</h3>
                  <p className="text-white/80">{item.subtitle}</p>
                </div>
              </div>
              
              {!item.disabled && (
                <motion.div
                  className="absolute inset-0 bg-white/10"
                  initial={{ x: '-100%' }}
                  whileHover={{ x: '100%' }}
                  transition={{ duration: 0.5 }}
                />
              )}
            </motion.button>
          ))}
        </div>

        {/* Stats footer */}
        <motion.div
          initial={{ y: 50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="absolute bottom-8 flex items-center gap-8 text-white/60 text-sm"
        >
          <div className="flex items-center gap-2">
            <Users className="w-4 h-4" />
            <span>12,850 Leaders</span>
          </div>
          <div className="flex items-center gap-2">
            <Info className="w-4 h-4" />
            <span>Avg Survival: 36 Days</span>
          </div>
          <div className="flex items-center gap-2">
            <span>🎮</span>
            <span>48,497 Games</span>
          </div>
          <div className="flex items-center gap-2">
            <span>🔥</span>
            <span>Chaos Created: ∞</span>
          </div>
        </motion.div>
      </div>
    </div>
  );
}

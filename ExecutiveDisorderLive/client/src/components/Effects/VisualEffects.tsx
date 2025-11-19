import { useEffect, useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface StatChange {
  id: string;
  stat: string;
  value: number;
  x: number;
  y: number;
}

interface VisualEffectsProps {
  screenShakeTrigger?: number;  // Changed to trigger ID
  crisisAlertTrigger?: number;   // Changed to trigger ID
  statChanges?: StatChange[];
}

export default function VisualEffects({ 
  screenShakeTrigger = 0, 
  crisisAlertTrigger = 0,
  statChanges = []
}: VisualEffectsProps) {
  const [shake, setShake] = useState(false);
  const [showAlert, setShowAlert] = useState(false);
  const [particles, setParticles] = useState<Array<{ id: string; x: number; y: number; color: string }>>([]);
  
  const prevShakeTrigger = useRef(0);
  const prevCrisisTrigger = useRef(0);
  const shakeTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const crisisTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Screen shake effect - triggers when ID changes
  useEffect(() => {
    if (screenShakeTrigger > prevShakeTrigger.current && screenShakeTrigger > 0) {
      prevShakeTrigger.current = screenShakeTrigger;
      
      // Clear any existing timeout
      if (shakeTimeoutRef.current) {
        clearTimeout(shakeTimeoutRef.current);
      }
      
      setShake(true);
      shakeTimeoutRef.current = setTimeout(() => setShake(false), 500);
    }
  }, [screenShakeTrigger]);

  // Crisis alert effect - triggers when ID changes
  useEffect(() => {
    if (crisisAlertTrigger > prevCrisisTrigger.current && crisisAlertTrigger > 0) {
      prevCrisisTrigger.current = crisisAlertTrigger;
      
      // Clear any existing timeout
      if (crisisTimeoutRef.current) {
        clearTimeout(crisisTimeoutRef.current);
      }
      
      setShowAlert(true);
      
      // Generate crisis particles
      const newParticles = Array.from({ length: 20 }, (_, i) => ({
        id: `crisis-${Date.now()}-${i}`,
        x: Math.random() * window.innerWidth,
        y: Math.random() * window.innerHeight,
        color: 'rgb(239, 68, 68)' // red
      }));
      setParticles(newParticles);
      
      crisisTimeoutRef.current = setTimeout(() => {
        setShowAlert(false);
        setParticles([]);
      }, 2000);
    }
  }, [crisisAlertTrigger]);

  return (
    <>
      {/* Screen shake effect */}
      {shake && (
        <div className="fixed inset-0 pointer-events-none z-50 animate-shake" />
      )}

      {/* Crisis particles */}
      <AnimatePresence>
        {particles.map((particle) => (
          <motion.div
            key={particle.id}
            initial={{ 
              x: particle.x, 
              y: particle.y, 
              scale: 0, 
              opacity: 1 
            }}
            animate={{ 
              y: particle.y - 200, 
              scale: 1, 
              opacity: 0 
            }}
            exit={{ opacity: 0 }}
            transition={{ duration: 2, ease: "easeOut" }}
            className="fixed w-2 h-2 rounded-full pointer-events-none z-40"
            style={{ backgroundColor: particle.color }}
          />
        ))}
      </AnimatePresence>

      {/* Stat change indicators */}
      <AnimatePresence>
        {statChanges.map((change) => (
          <motion.div
            key={change.id}
            initial={{ 
              x: change.x, 
              y: change.y, 
              opacity: 0, 
              scale: 0.5 
            }}
            animate={{ 
              y: change.y - 80, 
              opacity: 1, 
              scale: 1 
            }}
            exit={{ 
              opacity: 0, 
              scale: 0.5 
            }}
            transition={{ duration: 1.5, ease: "easeOut" }}
            className={`fixed pointer-events-none z-50 text-2xl font-bold ${
              change.value > 0 ? 'text-green-400' : 'text-red-400'
            }`}
            style={{
              textShadow: '0 0 10px rgba(0,0,0,0.8), 0 0 20px rgba(0,0,0,0.6)',
            }}
          >
            {change.value > 0 ? '+' : ''}{change.value}
          </motion.div>
        ))}
      </AnimatePresence>

      {/* Crisis alert overlay */}
      <AnimatePresence>
        {showAlert && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: [0, 0.3, 0] }}
            exit={{ opacity: 0 }}
            transition={{ duration: 1, times: [0, 0.5, 1] }}
            className="fixed inset-0 bg-red-600 pointer-events-none z-30"
          />
        )}
      </AnimatePresence>
    </>
  );
}

// Hook for managing stat change effects
export function useStatChangeEffects() {
  const [statChanges, setStatChanges] = useState<StatChange[]>([]);

  const showStatChange = (stat: string, value: number, x: number, y: number) => {
    const id = `stat-${Date.now()}-${Math.random()}`;
    setStatChanges(prev => [...prev, { id, stat, value, x, y }]);
    setTimeout(() => {
      setStatChanges(prev => prev.filter(s => s.id !== id));
    }, 1500);
  };

  return { statChanges, showStatChange };
}

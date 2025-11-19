export const gameConfig = {
  // Game mechanics
  maxTurns: 50,
  criticalResourceThreshold: 10,
  gameEndResourceTotal: 80,
  
  // UI settings
  cardDisplayTime: 3000,
  transitionDuration: 1000,
  particleEffectDuration: 2000,
  
  // Audio settings
  backgroundMusicVolume: 0.3,
  sfxVolume: 0.8,
  
  // Visual settings
  cameraSettings: {
    position: [0, 2, 8],
    fov: 45,
    near: 0.1,
    far: 1000
  },
  
  // Time of day progression
  timeOfDayTurns: {
    morning: 0,
    afternoon: 15,
    night: 35
  },
  
  // Resource colors
  resourceColors: {
    popularity: '#ef4444',
    stability: '#3b82f6',
    media: '#8b5cf6',
    economy: '#059669'
  },
  
  // Game endings based on resource totals
  endings: {
    triumphant: { threshold: 280, title: "Accidental Genius", description: "Against all odds and basic logic, you somehow didn't destroy everything. Historians are confused. Your approval rating is 'yes.' Someone is making a statue of you, but nobody remembers ordering it." },
    successful: { threshold: 240, title: "Surprisingly Not Terrible", description: "You managed to not start any wars, crash the economy, or become a meme (mostly). Political scientists are calling it 'The Miracle of Low Expectations.' Your memoir is titled 'I Showed Up.'"},
    moderate: { threshold: 200, title: "The Medium Place", description: "Not great, not terrible. Perfectly mediocre. Your legacy is that people vaguely remember you existed. Your presidential library is a storage unit. The Wikipedia entry about you has a [citation needed]." },
    controversial: { threshold: 160, title: "The Chaos Presidency", description: "Half the country thinks you're a hero, the other half thinks you're a villain, and historians think you're a cautionary tale. Your name becomes a verb meaning 'to accidentally start drama.' Textbooks use your photo with the caption 'yikes.'" },
    struggling: { threshold: 120, title: "The Struggle Bus Driver", description: "Your presidency was like watching someone try to parallel park for 4 years straight. Painful. Awkward. Everyone learned something (mostly what not to do). Late night comedians send you fruit baskets as thank-you gifts." },
    disaster: { threshold: 0, title: "Catastrophic Failure Speedrun (World Record)", description: "You didn't just fail - you failed so spectacularly that failure itself is impressed. Countries are using your term as a case study in what NOT to do. Your legacy is a Wikipedia page titled 'List of Ways This Could Have Gone Wrong (It Did).' Congratulations?" }
  }
};

export const cardCategories = [
  'domestic',
  'foreign', 
  'economic',
  'social',
  'crisis'
] as const;

export type CardCategory = typeof cardCategories[number];

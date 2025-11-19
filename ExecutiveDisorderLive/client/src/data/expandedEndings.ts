/**
 * Expanded Endings System - 20 Different Endings
 * Based on comprehensive game configuration
 */

export interface GameEnding {
  id: string;
  name: string;
  description: string;
  video: string;
  trigger: {
    type: 'resources' | 'special' | 'turn' | 'combo';
    conditions: any;
  };
  score: number;
  rank: 'S' | 'A' | 'B' | 'C' | 'D' | 'F';
  category: 'victory' | 'disaster' | 'chaos' | 'special';
}

export const expandedEndings: GameEnding[] = [
  // VICTORY ENDINGS (S-A Rank)
  {
    id: 'perfect-victory',
    name: 'Utopian Triumph',
    description: 'Against all odds and logic, you created a perfect administration. Historians are confused.',
    video: '/videos/ending-cinematics/ending-victory-triumph.mp4',
    trigger: {
      type: 'resources',
      conditions: { all: 90 }
    },
    score: 10000,
    rank: 'S',
    category: 'victory'
  },
  {
    id: 'balanced-victory',
    name: 'Political Equilibrium',
    description: 'You mastered the art of keeping everyone equally satisfied... and suspicious.',
    video: '/videos/ending-cinematics/ending-victory-triumph.mp4',
    trigger: {
      type: 'resources',
      conditions: { all: 70, balanced: true }
    },
    score: 7500,
    rank: 'A',
    category: 'victory'
  },
  {
    id: 'popular-victory',
    name: 'Beloved Dictator',
    description: 'The people love you! Everything else is falling apart, but who cares?',
    video: '/videos/ending-cinematics/ending-victory-triumph.mp4',
    trigger: {
      type: 'resources',
      conditions: { popularity: 95 }
    },
    score: 6000,
    rank: 'A',
    category: 'victory'
  },
  {
    id: 'economic-miracle',
    name: 'Wall Street Darling',
    description: 'The economy is booming! Shame about literally everything else.',
    video: '/videos/ending-cinematics/ending-victory-triumph.mp4',
    trigger: {
      type: 'resources',
      conditions: { economy: 95 }
    },
    score: 6000,
    rank: 'A',
    category: 'victory'
  },
  
  // DISASTER ENDINGS (C-F Rank)
  {
    id: 'total-collapse',
    name: 'Apocalyptic Failure',
    description: 'You somehow failed at everything simultaneously. Impressive in the worst way.',
    video: '/videos/ending-cinematics/ending-nuclear-catastrophe.mp4',
    trigger: {
      type: 'resources',
      conditions: { all: 15 }
    },
    score: 100,
    rank: 'F',
    category: 'disaster'
  },
  {
    id: 'economic-depression',
    name: 'The Great Recession 2.0',
    description: 'Your economic policies make the Great Depression look like a minor inconvenience.',
    video: '/videos/ending-cinematics/ending-economic-collapse.mp4',
    trigger: {
      type: 'resources',
      conditions: { economy: 10 }
    },
    score: 500,
    rank: 'D',
    category: 'disaster'
  },
  {
    id: 'revolution',
    name: 'Viva La Revolution!',
    description: 'The people have spoken... with molotov cocktails and guillotines.',
    video: '/videos/ending-cinematics/ending-revolution-uprising.mp4',
    trigger: {
      type: 'resources',
      conditions: { stability: 10 }
    },
    score: 500,
    rank: 'D',
    category: 'disaster'
  },
  {
    id: 'media-scandal',
    name: 'Watergate 2.0',
    description: 'The media destroyed you. Your name is now a verb meaning "to fail spectacularly."',
    video: '/videos/ending-cinematics/ending-scandal-impeachment.mp4',
    trigger: {
      type: 'resources',
      conditions: { media: 10 }
    },
    score: 750,
    rank: 'D',
    category: 'disaster'
  },
  {
    id: 'impeachment',
    name: 'Impeached & Removed',
    description: 'Constitutional crisis achieved! You\'re the textbook example of what NOT to do.',
    video: '/videos/ending-cinematics/ending-scandal-impeachment.mp4',
    trigger: {
      type: 'combo',
      conditions: { popularity: 20, media: 20 }
    },
    score: 1000,
    rank: 'C',
    category: 'disaster'
  },
  
  // CHAOS ENDINGS (B-D Rank)
  {
    id: 'pandemonium-peak',
    name: 'Maximum Chaos Achieved',
    description: 'You broke reality itself. The simulation is questioning its existence.',
    video: '/videos/ending-cinematics/ending-nuclear-catastrophe.mp4',
    trigger: {
      type: 'special',
      conditions: { chaos: 100 }
    },
    score: 4000,
    rank: 'B',
    category: 'chaos'
  },
  {
    id: 'absurdist-finale',
    name: 'The Absurdist Ending',
    description: 'Nothing makes sense anymore. You weaponized absurdity and won... somehow.',
    video: '/videos/ending-cinematics/ending-nuclear-catastrophe.mp4',
    trigger: {
      type: 'special',
      conditions: { absurdCards: 30 }
    },
    score: 3500,
    rank: 'B',
    category: 'chaos'
  },
  {
    id: 'cascade-catastrophe',
    name: 'The Domino Effect',
    description: 'One bad decision led to another, which led to another... it never stopped.',
    video: '/videos/ending-cinematics/ending-revolution-uprising.mp4',
    trigger: {
      type: 'special',
      conditions: { cascades: 10 }
    },
    score: 1500,
    rank: 'D',
    category: 'chaos'
  },
  
  // SPECIAL ENDINGS (A-B Rank)
  {
    id: 'survivor',
    name: 'The Great Survivor',
    description: 'You survived 100 turns through sheer luck and questionable decisions.',
    video: '/videos/ending-cinematics/ending-victory-triumph.mp4',
    trigger: {
      type: 'turn',
      conditions: { turns: 100 }
    },
    score: 5000,
    rank: 'A',
    category: 'special'
  },
  {
    id: 'pyrrhic-victory',
    name: 'Pyrrhic Victory',
    description: 'Technically you won, but at what cost? Everything. The cost was everything.',
    video: '/videos/ending-cinematics/ending-scandal-impeachment.mp4',
    trigger: {
      type: 'combo',
      conditions: { popularity: 80, stability: 30, media: 30, economy: 30 }
    },
    score: 3000,
    rank: 'B',
    category: 'special'
  },
  {
    id: 'media-empire',
    name: 'The Fourth Estate Reigns',
    description: 'You became a media darling while the country crumbled. Style over substance achieved!',
    video: '/videos/ending-cinematics/ending-scandal-impeachment.mp4',
    trigger: {
      type: 'resources',
      conditions: { media: 90 }
    },
    score: 4000,
    rank: 'B',
    category: 'special'
  },
  {
    id: 'war-president',
    name: 'Wartime Leadership',
    description: 'Nothing unites a country like a good crisis. You manufactured several.',
    video: '/videos/ending-cinematics/ending-victory-triumph.mp4',
    trigger: {
      type: 'special',
      conditions: { crisisCards: 20 }
    },
    score: 3500,
    rank: 'B',
    category: 'special'
  },
  {
    id: 'puppet-master',
    name: 'The Puppet Master',
    description: 'Who needs popularity when you control everything behind the scenes?',
    video: '/videos/ending-cinematics/ending-scandal-impeachment.mp4',
    trigger: {
      type: 'combo',
      conditions: { popularity: 40, stability: 70, economy: 70 }
    },
    score: 4500,
    rank: 'A',
    category: 'special'
  },
  {
    id: 'accidental-genius',
    name: 'Accidental Genius',
    description: 'Every terrible decision somehow worked out. You\'re either lucky or in a simulation.',
    video: '/videos/ending-cinematics/ending-victory-triumph.mp4',
    trigger: {
      type: 'special',
      conditions: { badChoices: 40, finalScore: 5000 }
    },
    score: 6000,
    rank: 'A',
    category: 'special'
  },
  {
    id: 'legacy-destroyer',
    name: 'Legacy Destroyed',
    description: 'Future textbooks will use you as a cautionary tale. Congratulations!',
    video: '/videos/ending-cinematics/ending-scandal-impeachment.mp4',
    trigger: {
      type: 'combo',
      conditions: { allBelow: 40, turns: 50 }
    },
    score: 2000,
    rank: 'C',
    category: 'disaster'
  },
  {
    id: 'cult-leader',
    name: 'Cult of Personality',
    description: 'You built a cult following. Democracy is optional when you\'re this beloved/feared.',
    video: '/videos/ending-cinematics/ending-victory-triumph.mp4',
    trigger: {
      type: 'combo',
      conditions: { popularity: 90, stability: 50 }
    },
    score: 5500,
    rank: 'A',
    category: 'special'
  }
];

export const getEnding = (gameState: any): GameEnding => {
  const { resources, turn, chaos, cardHistory, decisions } = gameState;
  
  // Check for special endings first
  for (const ending of expandedEndings) {
    if (checkEndingCondition(ending, { resources, turn, chaos, cardHistory, decisions })) {
      return ending;
    }
  }
  
  // Default to basic ending based on resources
  return expandedEndings[0]; // perfect-victory as fallback
};

const checkEndingCondition = (ending: GameEnding, state: any): boolean => {
  const { resources, turn, chaos, cardHistory, decisions } = state;
  const { type, conditions } = ending.trigger;
  
  switch (type) {
    case 'resources':
      if (conditions.all) {
        return Object.values(resources).every((v: any) => v >= conditions.all);
      }
      if (conditions.allBelow) {
        return Object.values(resources).every((v: any) => v <= conditions.allBelow);
      }
      return Object.entries(conditions).every(([key, value]) => {
        const numValue = value as number;
        return resources[key] >= numValue || resources[key] <= numValue;
      });
      
    case 'turn':
      return turn >= conditions.turns;
      
    case 'special':
      if (conditions.chaos) return chaos >= conditions.chaos;
      if (conditions.absurdCards) {
        const absurdCount = cardHistory.filter((id: string) => id.includes('absurd')).length;
        return absurdCount >= conditions.absurdCards;
      }
      if (conditions.crisisCards) {
        const crisisCount = cardHistory.filter((id: string) => id.includes('crisis')).length;
        return crisisCount >= conditions.crisisCards;
      }
      return false;
      
    case 'combo':
      return Object.entries(conditions).every(([key, value]) => {
        const numValue = value as number;
        if (key === 'allBelow') {
          return Object.values(resources).every((v: any) => v <= numValue);
        }
        return resources[key] >= numValue || resources[key] <= numValue;
      });
      
    default:
      return false;
  }
};
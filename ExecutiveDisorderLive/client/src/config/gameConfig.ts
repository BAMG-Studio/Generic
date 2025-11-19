/**
 * Executive Disorder - Game Configuration
 * Based on comprehensive backend configuration
 */

export interface AIProviderConfig {
  openaiApiKey: string;
  elevenlabsApiKey: string;
  stabilityApiKey: string;
  anthropicApiKey: string;
  
  // Rate limiting
  maxRequestsPerMinute: number;
  maxTokensPerRequest: number;
  
  // Quality settings
  imageQuality: 'standard' | 'hd';
  imageSize: string;
  voiceQuality: 'standard' | 'premium';
}

export interface GameLogicConfig {
  // Pandemonium mechanics
  chaosThreshold: number;
  pandemoniumMultiplier: number;
  
  // Resource balance
  resourceMin: number;
  resourceMax: number;
  criticalThreshold: number;
  excessiveThreshold: number;
  
  // Reward/Punishment system
  rewardBonusMultiplier: number;
  punishmentPenaltyMultiplier: number;
  consequenceChainProbability: number;
  
  // Content counts
  totalCards: number;
  totalLeaders: number;
  totalCrises: number;
  totalFactions: number;
  totalEndings: number;
  
  // Card distribution
  cardCategories: {
    normal: number;
    crisis: number;
    scandal: number;
    absurd: number;
    character: number;
  };
}

export const gameConfig: GameLogicConfig = {
  // Pandemonium mechanics
  chaosThreshold: 85,
  pandemoniumMultiplier: 1.5,
  
  // Resource balance
  resourceMin: 0,
  resourceMax: 100,
  criticalThreshold: 20,
  excessiveThreshold: 80,
  
  // Reward/Punishment system
  rewardBonusMultiplier: 1.25,
  punishmentPenaltyMultiplier: 1.5,
  consequenceChainProbability: 0.7,
  
  // Content counts
  totalCards: 150,
  totalLeaders: 12,
  totalCrises: 50,
  totalFactions: 10,
  totalEndings: 20,
  
  // Card distribution
  cardCategories: {
    normal: 0.35,      // 35% standard policy decisions
    crisis: 0.20,      // 20% urgent situations
    scandal: 0.15,     // 15% political controversies
    absurd: 0.20,      // 20% satirical chaos
    character: 0.10,   // 10% character-specific events
  }
};

export const satiricalStyles = [
  'absurdist_bureaucracy',
  'dystopian_optimism',
  'corporate_doublespeak',
  'media_circus',
  'political_theater',
  'technological_nightmare',
  'economic_fantasy',
  'social_experiment_gone_wrong'
];

export const toneModifiers = [
  'darkly_comedic',
  'painfully_ironic',
  'exaggerated_realism',
  'satirical_documentary',
  'mockumentary_serious',
  'deadpan_absurd',
  'hyperrealistic_parody'
];

export const cardThemes = [
  // Political
  'executive_overreach', 'bureaucratic_nightmare', 'legislative_chaos',
  'diplomatic_disaster', 'constitutional_crisis', 'political_scandal',
  
  // Economic
  'market_manipulation', 'fiscal_insanity', 'corporate_takeover',
  'economic_bubbles', 'cryptocurrency_chaos', 'automation_apocalypse',
  
  // Social
  'viral_phenomena', 'social_media_meltdown', 'cultural_wars',
  'generational_divide', 'education_experiment', 'healthcare_havoc',
  
  // Environmental
  'climate_catastrophe', 'ecological_experiment', 'resource_depletion',
  'pollution_paradox', 'renewable_rebellion', 'extinction_event',
  
  // Technology
  'ai_uprising', 'cyber_warfare', 'digital_dystopia',
  'robot_rights', 'virtual_reality_escape', 'singularity_approach',
  
  // Military/Security
  'defense_dilemma', 'surveillance_state', 'nuclear_option',
  'space_force_shenanigans', 'military_industrial_complex', 'war_games',
  
  // Media/Culture
  'fake_news_frenzy', 'propaganda_push', 'celebrity_crisis',
  'entertainment_empire', 'cultural_appropriation', 'meme_warfare',
  
  // Absurd/Satirical
  'time_travel_taxes', 'alien_diplomacy', 'dimensional_rift',
  'sentient_buildings', 'weather_weaponization', 'gravity_modification'
];

export const artPalettes = {
  satirical_poster: {
    primary: ['#1a1a2e', '#16213e', '#0f3460'],
    accent: ['#e94560', '#f1f1f1'],
    style: '1950s propaganda poster meets modern graphic design'
  },
  corporate_dystopia: {
    primary: ['#0a0e27', '#1e3a8a', '#3b82f6'],
    accent: ['#10b981', '#fbbf24'],
    style: 'sleek corporate minimalism with ominous undertones'
  },
  media_frenzy: {
    primary: ['#7c2d12', '#dc2626', '#ef4444'],
    accent: ['#fbbf24', '#ffffff'],
    style: 'breaking news aesthetic with dramatic lighting'
  },
  tech_nightmare: {
    primary: ['#18181b', '#27272a', '#3f3f46'],
    accent: ['#06b6d4', '#8b5cf6'],
    style: 'cyberpunk meets silicon valley'
  }
};

export const voiceProfiles = {
  authoritative_leader: {
    description: 'Deep, commanding, presidential voice with gravitas',
    useCase: 'leader_dialogue, important_announcements'
  },
  cynical_narrator: {
    description: 'Dry, sardonic voice dripping with irony',
    useCase: 'card_narration, consequences'
  },
  enthusiastic_propagandist: {
    description: 'Overly cheerful, almost manic positivity',
    useCase: 'propaganda, positive_spin'
  },
  doom_prophet: {
    description: 'Ominous, foreboding, apocalyptic tone',
    useCase: 'crises, warnings, bad_endings'
  },
  bureaucratic_drone: {
    description: 'Monotone, lifeless, procedural delivery',
    useCase: 'policy_cards, regulations'
  },
  media_personality: {
    description: 'Energetic news anchor with dramatic flair',
    useCase: 'headlines, breaking_news'
  },
  conspiracy_theorist: {
    description: 'Paranoid, frantic, overexcited whisper-shouting',
    useCase: 'absurd_cards, rumors'
  },
  corporate_executive: {
    description: 'Smooth, professional, slightly menacing',
    useCase: 'business_cards, economic_events'
  }
};

export const pandemoniumTriggers = {
  absurdity_spike: { threshold: 85, duration: 3 },
  resource_chaos: { volatility: 40, timeframe: 5 },
  cascade_events: { min_chain: 3, escalation: 1.5 }
};

export const rewardPunishmentMatrix = {
  excellent_choice: { multiplier: 1.5, bonusEffects: true },
  good_choice: { multiplier: 1.2, bonusEffects: false },
  neutral_choice: { multiplier: 1.0, bonusEffects: false },
  poor_choice: { multiplier: 0.8, penaltyEffects: true },
  terrible_choice: { multiplier: 0.5, cascadeCrisis: true }
};

export const consequenceChains = {
  immediate: { delay: 0, probability: 1.0 },
  short_term: { delay: 1, probability: 0.8 },
  medium_term: { delay: 3, probability: 0.6 },
  long_term: { delay: 5, probability: 0.4 },
  endgame: { delay: 10, probability: 0.3 }
};
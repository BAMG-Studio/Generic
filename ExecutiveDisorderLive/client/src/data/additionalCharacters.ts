/**
 * Additional Characters to reach 12 total leaders
 * Expanding from 10 to 12 as per game configuration
 */

export const additionalCharacters = [
  {
    id: 'tech-disruptor',
    name: 'Silicon Valleyson',
    title: 'The Tech Disruptor',
    bio: 'A billionaire tech mogul who believes every problem can be solved with an app, blockchain, or AI. Has never held public office but claims to have "disrupted" democracy itself. Known for tweeting policy decisions at 3 AM and referring to citizens as "users."',
    startingStats: {
      popularity: 60,
      stability: 45,
      media: 75,
      economy: 65
    },
    specialAbility: 'Tech Solutions: Technology-related decisions have 50% stronger effects (positive or negative)',
    portrait: '/images/characters/tech-disruptor.png',
    color: '#3b82f6'
  },
  {
    id: 'conspiracy-chief',
    name: 'Truther McQuestion',
    title: 'The Conspiracy Chief',
    bio: 'A former podcast host who rode a wave of paranoia into the highest office. Believes the moon landing was faked but NASA is real... too real. Makes policy decisions based on "alternative facts" and claims the deep state is trying to hide the truth about everything.',
    startingStats: {
      popularity: 55,
      stability: 35,
      media: 40,
      economy: 50
    },
    specialAbility: 'Alternative Reality: Absurd decisions backfire 30% less, but normal decisions are 20% less effective',
    portrait: '/images/characters/conspiracy-chief.png',
    color: '#f97316'
  }
];

export const characterModifiersExtended = {
  'tech-disruptor': {
    modifier: {
      economy: 1.3,
      media: 1.2,
      stability: 0.9,
      popularity: 1.0
    },
    description: 'Tech Solutions active: +30% economy, +20% media, -10% stability'
  },
  'conspiracy-chief': {
    modifier: {
      popularity: 1.1,
      stability: 0.8,
      media: 0.7,
      economy: 1.0
    },
    description: 'Alternative Reality active: Absurd decisions less harmful, normal decisions less effective'
  }
};
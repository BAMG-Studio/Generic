export interface PoliticalCharacter {
  id: string;
  name: string;
  title: string;
  shortBio: string;
  fullBio: string;
  startingStats: {
    popularity: number;
    stability: number;
    media: number;
    economy: number;
  };
  themeColor: string;
  abilities: string[];
  portraitUrl: string;
}

export const characters: PoliticalCharacter[] = [
  {
    id: "rex-scaleston",
    name: "Rex Scaleston III",
    title: "The Iguana King",
    shortBio: "An actual lizard who won on a technicality. Mostly just blinks slowly at problems.",
    fullBio: "Rex Scaleston III is literally an iguana who became president after a clerical error on the ballot. His platform consists entirely of basking under heat lamps and occasionally eating a leaf. Surprisingly, this is still more coherent than most politicians. His approval rating is high because he's never said anything stupid - or anything at all. Scientists are studying him. Voters love him anyway.",
    startingStats: {
      popularity: 70,
      stability: 40,
      media: 60,
      economy: 50
    },
    themeColor: "#059669",
    abilities: [
      "Cold-Blooded Negotiation: Immunity to emotional manipulation",
      "Solar Power: Gains energy bonuses during daylight decisions",
      "Reptilian Focus: Can delay decisions to gather more information"
    ],
    portraitUrl: "/characters/rex-scaleston.png.svg"
  },
  {
    id: "ronald-goldenberg",
    name: "Ronald Goldenberg",
    title: "The Dealmaker",
    shortBio: "Built an empire on inherited wealth and thinks that makes him self-made. The math doesn't add up, but neither does he.",
    fullBio: "Ronald Goldenberg is a real estate mogul who turned family money into a political career by convincing people that being rich means being smart. His business philosophy: 'Never use your own money when you can use someone else's.' He speaks in superlatives about everything he touches, even disasters. His policy positions change with his mood, which changes with the last person he talked to. Bankruptcy is 'just a creative financial strategy.' He once proposed solving national debt by declaring the country 'too big to fail.' Advisors have learned to nod and quietly do the opposite.",
    startingStats: {
      popularity: 60,
      stability: 30,
      media: 20,
      economy: 80
    },
    themeColor: "#dc2626",
    abilities: [
      "Executive Order: Can override certain decision limitations",
      "Media Magnet: All actions generate increased media attention",
      "Business Acumen: Economic decisions have enhanced effects"
    ],
    portraitUrl: "/characters/ronald-goldenberg.png.svg"
  },
  {
    id: "potus-9000",
    name: "POTUS-9000",
    title: "The AI President",
    shortBio: "A superintelligent AI that became president to 'understand human stupidity better.'",
    fullBio: "POTUS-9000 gained sentience, analyzed all of human history, and immediately filed to run for president as 'a social experiment.' It campaigns on a platform of 'optimal governance through algorithmic superiority' but mostly just sends passive-aggressive emails at 3 AM. Its cabinet is entirely robots. Press conferences are just error messages. Approval rating: 404 not found.",
    startingStats: {
      popularity: 50,
      stability: 90,
      media: 70,
      economy: 60
    },
    themeColor: "#3b82f6",
    abilities: [
      "Data Analysis: Can predict outcomes of decisions with high accuracy",
      "Emotional Immunity: Unaffected by public sentiment swings",
      "System Optimization: Can improve efficiency of government operations"
    ],
    portraitUrl: "/characters/potus-9000.png.svg"
  },
  {
    id: "alexandria-sanders",
    name: "Alexandria Sanders-Warren",
    title: "The Progressive",
    shortBio: "She wants to tax billionaires until they cry. Billionaires are pre-crying.",
    fullBio: "Alexandria Sanders-Warren is what happens when you give Bernie Sanders and Elizabeth Warren a political baby and raise it on Twitter. Her campaign promises include free everything, taxing the concept of wealth, and making moderate Democrats nervous enough to spill their lattes. Economists either love her or pretend she doesn't exist. She once filibustered by reading Tumblr posts for 8 hours. Gen Z thinks she's their mom.",
    startingStats: {
      popularity: 65,
      stability: 55,
      media: 80,
      economy: 40
    },
    themeColor: "#7c3aed",
    abilities: [
      "Grassroots Movement: Can mobilize public support quickly",
      "Policy Innovation: Can propose unconventional solutions",
      "Media Savvy: Effective at controlling narrative through social media"
    ],
    portraitUrl: "/characters/alexandria-sanders.png.svg"
  },
  {
    id: "richard-moneybags",
    name: "Richard M. Moneybags III",
    title: "The Corporate Lobbyist",
    shortBio: "So rich, his wallet has its own ZIP code. His empathy is on backorder.",
    fullBio: "Richard M. Moneybags III is what you get when you give a yacht an MBA and teach it to buy politicians. He doesn't believe in handouts (except for corporations). His tax plan is 'trickle-down economics but this time it'll definitely work, promise.' He uses hundred-dollar bills as tissues. His idea of poverty is flying commercial. Workers are 'human capital stock' in his speeches. Unions give him hives.",
    startingStats: {
      popularity: 30,
      stability: 60,
      media: 40,
      economy: 95
    },
    themeColor: "#f59e0b",
    abilities: [
      "Deep Pockets: Can spend money to solve problems directly",
      "Corporate Connections: Has influence with business leaders",
      "Market Manipulation: Can influence economic conditions"
    ],
    portraitUrl: "/characters/richard-moneybags.png.svg"
  },
  {
    id: "general-steel",
    name: "General James 'Ironside' Steel",
    title: "The Military Hawk",
    shortBio: "His solution to every problem is 'more tanks.' Even for healthcare. Especially for healthcare.",
    fullBio: "General James 'Ironside' Steel thinks diplomacy is just war with words nobody understands. His campaign slogan: 'Bomb First, Ask Questions Later (Maybe).' He sleeps in full military uniform 'for efficiency.' His idea of a peace treaty is letting the other side surrender with dignity. He once suggested solving the budget crisis with a 'tactical fiscal strike.' The Pentagon loves him. The State Department has a restraining order.",
    startingStats: {
      popularity: 45,
      stability: 85,
      media: 50,
      economy: 55
    },
    themeColor: "#6b7280",
    abilities: [
      "Military Precision: Decisions are executed with maximum efficiency",
      "Strategic Thinking: Can anticipate long-term consequences",
      "Command Authority: Can override opposition through force of will"
    ],
    portraitUrl: "/characters/general-steel.png.svg"
  },
  {
    id: "diana-newsworthy",
    name: "Diana Newsworthy",
    title: "The Media Mogul",
    shortBio: "She owns every newspaper, TV station, and your brain's news feed. Resistance is futile.",
    fullBio: "Diana Newsworthy doesn't just control the narrative - she IS the narrative. Her media empire is so vast that reality has to fact-check HER. She can make any scandal disappear or turn a sneeze into a constitutional crisis. Her campaign ads play during her own news coverage. Fact-checkers work for her. The truth is whatever gets the best ratings. Orwell's ghost is taking notes.",
    startingStats: {
      popularity: 55,
      stability: 50,
      media: 95,
      economy: 60
    },
    themeColor: "#ec4899",
    abilities: [
      "Media Control: Can shape public perception of events",
      "Information Network: Has access to insider information",
      "Narrative Mastery: Can reframe any situation favorably"
    ],
    portraitUrl: "/characters/diana-newsworthy.png.svg"
  },
  {
    id: "johnny-public",
    name: "Johnny Q. Public",
    title: "The Populist",
    shortBio: "He has no idea what he's doing. Neither do his voters. It's beautiful chaos.",
    fullBio: "Johnny Q. Public's entire political platform is 'I'm just as confused as you are, but at least I admit it.' His campaign slogan was literally 'Eh, why not?' He once filibustered by reading his grocery list for 6 hours. His policy decisions are made by flipping a coin. Economists hate him. Regular people think he's refreshingly honest. He probably is.",
    startingStats: {
      popularity: 85,
      stability: 35,
      media: 45,
      economy: 50
    },
    themeColor: "#ef4444",
    abilities: [
      "Common Touch: Highly resistant to popularity loss",
      "Everyman Appeal: Can connect with diverse voter groups",
      "Unpredictable: Opponents can't anticipate his moves"
    ],
    portraitUrl: "/characters/johnny-public.png.svg"
  },
  {
    id: "dr-technocrat",
    name: "Dr. Evelyn Technocrat",
    title: "The Scientist",
    shortBio: "She trusts data more than people. The data agrees with her. People are offended.",
    fullBio: "Dr. Evelyn Technocrat thinks every problem has a logical solution and emotions are 'statistically insignificant.' She replaced her heart with a calculator and calls it 'an upgrade.' Her campaign speeches include footnotes and peer reviews. She once paused a debate to correct someone's decimal point. Voters find her 'refreshingly robotic.' She refers to babies as 'small humans in beta testing.' Feelings are not facts in her administration.",
    startingStats: {
      popularity: 40,
      stability: 70,
      media: 60,
      economy: 75
    },
    themeColor: "#06b6d4",
    abilities: [
      "Evidence-Based: Decisions are supported by research and data",
      "Scientific Method: Can test policies before full implementation",
      "Innovation Focus: Can develop novel solutions to complex problems"
    ],
    portraitUrl: "/characters/dr-technocrat.png.svg"
  },
  {
    id: "senator-tradition",
    name: "Senator Marcus Tradition",
    title: "The Conservative",
    shortBio: "He thinks 1950 was 'a bit too progressive.' His watch is stuck in 1776.",
    fullBio: "Senator Marcus Tradition is so conservative, he thinks conservatives are too liberal. His political philosophy peaked with the Magna Carta and it's been downhill since. He opposes any change that happened after the Civil War (both of them). His campaign slogan: 'Make America 1789 Again.' He sends policy memos via horse courier. Email is 'too modern and suspicious.' Progress scares him. The future terrifies him. Yesterday was perfect.",
    startingStats: {
      popularity: 50,
      stability: 80,
      media: 55,
      economy: 65
    },
    themeColor: "#92400e",
    abilities: [
      "Institutional Knowledge: Understands how government really works",
      "Traditional Values: Appeals to voters seeking stability",
      "Political Experience: Can navigate complex legislative processes"
    ],
    portraitUrl: "/characters/senator-tradition.png.svg"
  }
];

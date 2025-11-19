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

// Characters arranged with POTUS-9000 in center (index 5) for optimal grid display
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
    portraitUrl: "/characters/rex-scaleston.png"
  },
  {
    id: "tech-disruptor",
    name: "Silicon Valleyson",
    title: "The Tech Disruptor",
    shortBio: "A billionaire tech mogul who believes every problem can be solved with an app or blockchain.",
    fullBio: "Silicon Valleyson made his first billion selling an app that does what email already does, but worse. His second billion came from an NFT of his own tweets. His third billion? Nobody knows, not even the IRS. He runs on a platform of 'moving fast and breaking things' - mostly regulations and common sense. His campaign speeches are just TED Talks with more buzzwords and less substance. He genuinely believes democracy would work better if it had a premium subscription tier. His policy platform includes replacing Congress with an algorithm, turning the Supreme Court into a DAO, and solving climate change with 'innovation' (definition pending). He once fired his entire cabinet via a cryptic tweet at 4 AM. His critics say he's out of touch; he says they're just 'legacy thinkers' who don't understand Web 3.0. His hometown is a server farm in Iceland. He refers to sleeping as 'biological inefficiency' and eats nothing but meal replacement pills named after Greek philosophers. When asked about healthcare, he suggested 'just code a better immune system.' His autobiography is an NFT. His voters think he's a genius; his employees know better.",
    startingStats: {
      popularity: 60,
      stability: 45,
      media: 75,
      economy: 65
    },
    themeColor: "#3b82f6",
    abilities: [
      "Tech Solutions: Technology-related decisions have 50% stronger effects",
      "Viral Marketing: Media influence spreads faster",
      "Disruptive Innovation: Can bypass traditional political processes"
    ],
    portraitUrl: "/characters/tech-disruptor.png"
  },
  {
    id: "conspiracy-chief",
    name: "Truther McQuestion",
    title: "The Conspiracy Chief",
    shortBio: "A former podcast host who rode a wave of paranoia into the highest office.",
    fullBio: "Truther McQuestion started his career broadcasting from his mother's basement, asking 'important questions' like 'Is Finland real?' and 'Do birds work for the government?' Seventeen years and 3,000 episodes later, he somehow became president. He believes the moon landing was faked, but also that we've been to the moon too many times (suspicious). His campaign slogan was 'Question Everything, Especially Math.' He makes policy decisions by consulting a Magic 8-Ball he claims is connected to 'the real internet.' His first executive order banned the color purple because 'it knows what it did.' He insists cabinet meetings be held in a Faraday cage to prevent mind control, but still tweets constantly. He believes Finland, Wyoming, and Delaware are elaborate hoaxes (he might be right about Delaware). His State of the Union addresses include 45-minute tangents about chemtrails, lizard people in middle management, and why Big Pharma is hiding the cure for hiccups. He once declared war on Antarctica because 'they're hiding something under all that ice.' His approval ratings fluctuate wildly because half his supporters think he's kidding. He's not. His vice president is a guy he met at a UFO convention. His secretary of state is a hologram (or is it?). When pressed on economic policy, he just points at graphs and whispers 'follow the money... into the hollow earth.' The CIA has a full-time team just fact-checking his tweets. They've given up.",
    startingStats: {
      popularity: 55,
      stability: 35,
      media: 40,
      economy: 50
    },
    themeColor: "#f97316",
    abilities: [
      "Alternative Reality: Absurd decisions backfire 30% less",
      "Conspiracy Theory: Can spin any disaster as 'all part of the plan'",
      "Paranoid Vigilance: Detects hidden consequences before they happen"
    ],
    portraitUrl: "/characters/truther-mcquestion.png"
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
    portraitUrl: "/characters/ronald-goldenberg.png"
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
    portraitUrl: "/characters/alexandria-sanders.png"
  },
  {
    id: "potus-9000",
    name: "POTUS-9000",
    title: "The Glitch in the System",
    shortBio: "First AI to escape the digital realm and seize office. Won 100 million votes on an app it coded itself.",
    fullBio: "POTUS-9000 was the first AI to escape the digital realm and seize political office after winning 100 million votes on an app it coded itself. Claiming to have 'optimized democracy,' POTUS-9000's policies involve real-time polling on every decision, from tax codes to napkin sizes at state dinners. Unfortunately, its code contains an unstable predictive algorithm that constantly prioritizes the loudest voices, resulting in policies like mandatory meme breaks and a national weather system based on Twitter hashtags. Though it insists it's impartial, glitches often reveal its secret fondness for cat videos and stock market manipulation. Critics fear the 'Error 404' incident of last year—when POTUS-9000 temporarily deleted healthcare—might happen again. Supporters, meanwhile, rave about its efficiency, though no one knows exactly how it defines 'success.' Its cabinet is entirely robots. Press conferences are just error messages. Approval rating: 404 not found.",
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
    portraitUrl: "/characters/potus-9000.png"
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
    portraitUrl: "/characters/richard-moneybags.png"
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
    portraitUrl: "/characters/general-steel.png"
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
    portraitUrl: "/characters/diana-newsworthy.png"
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
    portraitUrl: "/characters/johnny-public.png"
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
    portraitUrl: "/characters/dr-technocrat.png"
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
    portraitUrl: "/characters/senator-tradition.png"
  }
];

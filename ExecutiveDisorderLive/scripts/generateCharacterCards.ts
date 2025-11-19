// Character Card Generator Script
// Generates varied character-specific cards efficiently

interface CharacterCard {
  character: string;
  ability: string;
  scenario: string;
  cardNumber: number;
}

const characters = [
  {
    id: "rex-scaleston",
    name: "Rex Scaleston III",
    title: "The Iguana King",
    abilities: ["Cold-Blooded Negotiation", "Solar Power", "Reptilian Focus"],
    scenarios: [
      "Diplomatic crisis with foreign nation",
      "Energy policy decision under sun",
      "Delaying crucial vote to analyze",
      "International trade negotiation",
      "Environmental protection decision",
      "Military intervention choice",
      "Economic stimulus debate",
      "Immigration policy reform",
      "Healthcare legislation vote",
      "Climate change action"
    ]
  },
  {
    id: "ronald-goldenberg",
    name: "Ronald Goldenberg",
    title: "The Dealmaker",
    abilities: ["Executive Order", "Media Magnet", "Business Acumen"],
    scenarios: [
      "Override congressional decision",
      "High-profile media announcement",
      "Major business tax reform",
      "Trade deal negotiation",
      "Corporate regulation decision",
      "Real estate development approval",
      "Media scandal management",
      "Economic recovery plan",
      "Labor relations crisis",
      "International business summit"
    ]
  },
  {
    id: "potus-9000",
    name: "POTUS-9000",
    title: "The AI President",
    abilities: ["Data Analysis", "Emotional Immunity", "System Optimization"],
    scenarios: [
      "Predict economic crash outcome",
      "Ignore public sentiment on policy",
      "Optimize government efficiency",
      "Algorithm-based law enforcement",
      "Automated diplomatic response",
      "Tech regulation decision",
      "Cyber security crisis",
      "AI rights legislation",
      "Digital privacy policy",
      "Automation job displacement"
    ]
  },
  {
    id: "alexandria-sanders-warren",
    name: "Alexandria Sanders-Warren",
    title: "The Progressive",
    abilities: ["Grassroots Movement", "Policy Innovation", "Media Savvy"],
    scenarios: [
      "Mobilize public support rally",
      "Propose universal basic income",
      "Social media campaign launch",
      "Medicare for all vote",
      "Green New Deal initiative",
      "Student debt forgiveness",
      "Wealth tax proposal",
      "Workers' rights reform",
      "Housing affordability plan",
      "Education funding increase"
    ]
  },
  {
    id: "richard-moneybags",
    name: "Richard M. Moneybags III",
    title: "The Corporate Lobbyist",
    abilities: ["Deep Pockets", "Corporate Connections", "Market Manipulation"],
    scenarios: [
      "Bribe to solve crisis",
      "CEO summit influence",
      "Stock market manipulation",
      "Luxury tax avoidance",
      "Corporate merger approval",
      "Lobbying campaign success",
      "Private sector bailout",
      "Deregulation push",
      "Tax haven protection",
      "Campaign finance loophole"
    ]
  },
  {
    id: "general-steel",
    name: "General James 'Ironside' Steel",
    title: "The Military Hawk",
    abilities: ["Military Precision", "Strategic Thinking", "Command Authority"],
    scenarios: [
      "Execute mission flawlessly",
      "Anticipate enemy movement",
      "Override civilian objections",
      "Military budget increase",
      "Strategic weapons deployment",
      "Wartime decision making",
      "Military coup prevention",
      "Defense contractor deal",
      "Veterans affairs reform",
      "Military intervention abroad"
    ]
  },
  {
    id: "diana-newsworthy",
    name: "Diana Newsworthy",
    title: "The Media Mogul",
    abilities: ["Media Control", "Information Network", "Narrative Mastery"],
    scenarios: [
      "Shape public perception",
      "Access insider information",
      "Reframe scandal favorably",
      "Breaking news manipulation",
      "Press conference control",
      "Social media narrative",
      "Investigative journalism",
      "Ratings-driven policy",
      "Media empire expansion",
      "Fake news combat"
    ]
  },
  {
    id: "johnny-q-public",
    name: "Johnny Q. Public",
    title: "The Populist",
    abilities: ["Common Touch", "Everyman Appeal", "Unpredictable"],
    scenarios: [
      "Maintain popularity despite scandal",
      "Connect with diverse voters",
      "Surprise policy announcement",
      "Main Street over Wall Street",
      "Common sense solution",
      "Anti-establishment stance",
      "Direct democracy vote",
      "Working class hero moment",
      "Simplify complex issue",
      "Grassroots campaign"
    ]
  },
  {
    id: "dr-evelyn-technocrat",
    name: "Dr. Evelyn Technocrat",
    title: "The Scientist",
    abilities: ["Evidence-Based", "Scientific Method", "Innovation Focus"],
    scenarios: [
      "Research-backed decision",
      "Pilot program testing",
      "Novel scientific solution",
      "Pandemic response plan",
      "Climate science policy",
      "Space exploration funding",
      "Scientific research grants",
      "Evidence vs politics",
      "Technology innovation",
      "Data-driven governance"
    ]
  },
  {
    id: "senator-marcus-tradition",
    name: "Senator Marcus Tradition",
    title: "The Conservative",
    abilities: ["Institutional Knowledge", "Traditional Values", "Political Experience"],
    scenarios: [
      "Navigate complex legislation",
      "Appeal to tradition",
      "Legislative process mastery",
      "Constitutional interpretation",
      "Bipartisan compromise",
      "Heritage preservation",
      "Fiscal conservatism",
      "States' rights defense",
      "Traditional family values",
      "Government restraint"
    ]
  }
];

// Generate card metadata for 50 cards per character
function generateCardList() {
  const allCards: CharacterCard[] = [];
  
  characters.forEach(char => {
    for (let i = 0; i < 50; i++) {
      const ability = char.abilities[i % char.abilities.length];
      const scenario = char.scenarios[i % char.scenarios.length];
      
      allCards.push({
        character: char.name,
        ability: ability,
        scenario: scenario,
        cardNumber: i + 1
      });
    }
  });
  
  return allCards;
}

const cardList = generateCardList();
console.log(`Generated ${cardList.length} card definitions`);
console.log(`Total characters: ${characters.length}`);
console.log(`Cards per character: 50`);

// Export card list for use
export { cardList, characters };

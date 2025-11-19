export interface DecisionCard {
  id: string;
  title: string;
  description: string;
  category: 'domestic' | 'foreign' | 'economic' | 'social' | 'crisis';
  imageUrl?: string; // Optional card artwork URL
  options: {
    text: string;
    actionText?: string; // Optional satirical button text (e.g., "FIRE", "VETO", "DENY")
    effects: {
      popularity: number;
      stability: number;
      media: number;
      economy: number;
    };
  }[];
}

export const decisionCards: DecisionCard[] = [
  {
    id: "budget-crisis",
    title: "The Treasury Called - We're Broke (Again)",
    description: "Your financial advisor just revealed that the national budget was accidentally spent on a giant statue of yourself. Congress is furious, tourists are confused, and economists are having a collective aneurysm.",
    category: "economic",
    options: [
      {
        text: "Sell the statue as 'modern art' and blame the previous administration",
        actionText: "SELL IT",
        effects: { popularity: -15, stability: 5, media: -5, economy: 10 }
      },
      {
        text: "Start a GoFundMe titled 'Help Your President Not Go Bankrupt'",
        actionText: "CROWDFUND",
        effects: { popularity: 5, stability: -5, media: 10, economy: -5 }
      },
      {
        text: "Print more money and pretend inflation is just a 'vibe'",
        actionText: "PRINT $$",
        effects: { popularity: 10, stability: -10, media: -10, economy: 5 }
      }
    ]
  },
  {
    id: "healthcare-reform",
    title: "Healthcare or Health-DON'T-Care?",
    description: "Your health secretary suggests replacing the entire healthcare system with essential oils and positive thinking. WebMD is now the official government medical advisor. The AMA is screaming into the void.",
    category: "domestic",
    options: [
      {
        text: "Mandate that all doctors must also be life coaches",
        effects: { popularity: 10, stability: -10, media: 5, economy: -10 }
      },
      {
        text: "Replace hospitals with wellness spas and call it 'innovation'",
        effects: { popularity: -5, stability: 5, media: -5, economy: 5 }
      },
      {
        text: "Declare sickness 'illegal' and watch the problem solve itself",
        effects: { popularity: -15, stability: 10, media: -10, economy: 0 }
      }
    ]
  },
  {
    id: "trade-war",
    title: "International Beef (Literally)",
    description: "A foreign leader challenged you to a hot dog eating contest to settle a trade dispute. Your dignity is on the line, but so are billions in exports. CNN is already setting up cameras.",
    category: "foreign",
    options: [
      {
        text: "Accept the challenge and hire Joey Chestnut as your body double",
        effects: { popularity: 5, stability: -5, media: 0, economy: -10 }
      },
      {
        text: "Propose thumb wrestling instead because you 'have really strong thumbs'",
        effects: { popularity: -5, stability: 5, media: 10, economy: 0 }
      },
      {
        text: "Claim hot dogs are against your religion (starting today)",
        effects: { popularity: -10, stability: 0, media: -5, economy: 5 }
      }
    ]
  },
  {
    id: "climate-action",
    title: "The Weather is SO Last Season",
    description: "Scientists say the planet is literally on fire. Your solution? Rename 'global warming' to 'planetary glow-up' and sell beachfront property in Antarctica. Mother Nature has left several angry voicemails.",
    category: "social",
    options: [
      {
        text: "Mandatory sunscreen for the entire country (SPF 1000)",
        effects: { popularity: 0, stability: -5, media: 15, economy: -15 }
      },
      {
        text: "Ban thermometers so temperatures can't be 'officially' measured",
        effects: { popularity: 5, stability: 5, media: 0, economy: -5 }
      },
      {
        text: "Blast AC units into the sky and invoice the atmosphere",
        effects: { popularity: -10, stability: 0, media: -15, economy: 15 }
      }
    ]
  },
  {
    id: "social-media-regulation",
    title: "Twitter Meltdown (Not The App, You)",
    description: "You accidentally liked a conspiracy theory about birds being government drones at 3 AM. It has 50 million views. Your press secretary is fake-crying in the bathroom. The bird lobby is assembling.",
    category: "domestic",
    options: [
      {
        text: "Double down: Ban all birds and replace them with robot pigeons",
        effects: { popularity: 5, stability: 10, media: -10, economy: -5 }
      },
      {
        text: "Claim your account was hacked by a 'very sophisticated hamster'",
        effects: { popularity: -5, stability: -10, media: 15, economy: 10 }
      },
      {
        text: "Delete the internet and bring back carrier pigeons (the real ones)",
        effects: { popularity: -10, stability: 0, media: -5, economy: -10 }
      }
    ]
  },
  {
    id: "infrastructure-investment",
    title: "Infrastructure? More Like Infra-STRUC-DURRR",
    description: "All the nation's bridges are held together with duct tape and prayer. Your infrastructure czar suggests replacing them with trampolines. Engineers are weeping. TikTokers are excited.",
    category: "economic",
    options: [
      {
        text: "Build bridges made entirely of LEDs so they look cool at night",
        effects: { popularity: 10, stability: 5, media: 5, economy: -5 }
      },
      {
        text: "Replace all roads with Slip 'N Slides for 'efficiency'",
        effects: { popularity: 0, stability: 5, media: 0, economy: 0 }
      },
      {
        text: "Just paint the potholes gold and call it 'luxury infrastructure'",
        effects: { popularity: -5, stability: -5, media: -5, economy: 5 }
      }
    ]
  },
  {
    id: "immigration-policy",
    title: "Border Wall (Made of Thoughts and Prayers)",
    description: "Your immigration advisor suggests building a wall so tall that birds need visas. Engineers say it's 'physically impossible.' You say 'that's quitter talk' and start a Kickstarter.",
    category: "social",
    options: [
      {
        text: "Build the wall out of recycled campaign promises",
        effects: { popularity: 0, stability: 10, media: -10, economy: -5 }
      },
      {
        text: "Replace border security with a very stern-looking scarecrow",
        effects: { popularity: 5, stability: -10, media: 10, economy: 5 }
      },
      {
        text: "Make everyone speak in accents so no one can tell who's from where",
        effects: { popularity: -5, stability: 0, media: -5, economy: 0 }
      }
    ]
  },
  {
    id: "military-intervention",
    title: "World War...Memes?",
    description: "Two countries are fighting over who invented the sandwich. It's getting serious - one side brought tanks, the other brought lawyers. The UN is just confused. You must intervene before lunch time ends.",
    category: "foreign",
    options: [
      {
        text: "Send in troops armed with extremely detailed sandwich history books",
        effects: { popularity: -10, stability: -10, media: 0, economy: -10 }
      },
      {
        text: "Organize an international sandwich-making competition to settle it",
        effects: { popularity: 5, stability: 5, media: 10, economy: -5 }
      },
      {
        text: "Claim America invented sandwiches and watch the chaos unfold",
        effects: { popularity: 0, stability: 0, media: -10, economy: 5 }
      }
    ]
  },
  {
    id: "education-funding",
    title: "Schools? We Have YouTube!",
    description: "Your education secretary proposes replacing all teachers with motivational speakers and TikTok influencers. The curriculum is now 50% hustle culture, 50% dance challenges. Pythagoras is rolling in his grave.",
    category: "domestic",
    options: [
      {
        text: "Make every class a 'masterclass' taught by celebrities who peaked in 2003",
        effects: { popularity: 10, stability: -5, media: 5, economy: -10 }
      },
      {
        text: "Replace textbooks with inspirational quote posters and vibes",
        effects: { popularity: 0, stability: -5, media: 0, economy: 0 }
      },
      {
        text: "Abolish homework because 'kids need to focus on their personal brand'",
        effects: { popularity: -5, stability: 5, media: -5, economy: 5 }
      }
    ]
  },
  {
    id: "tech-monopoly",
    title: "Big Tech or BIG THREAT?",
    description: "Tech CEOs have become so powerful they're starting their own countries. One just bought Tuesday. Another is selling the moon as NFTs. Your antitrust lawyer quit and joined their side.",
    category: "economic",
    options: [
      {
        text: "Break them up, but they just merge back together like the T-1000",
        effects: { popularity: 5, stability: -10, media: 0, economy: -15 }
      },
      {
        text: "Tax them, but they claim they're 'technically in space' now",
        effects: { popularity: 0, stability: 0, media: 5, economy: -5 }
      },
      {
        text: "Join them and become a tech bro president (hoodie required)",
        effects: { popularity: -10, stability: 5, media: -10, economy: 10 }
      }
    ]
  },
  {
    id: "pandemic-response",
    title: "The Sniffles That Broke America",
    description: "A mysterious illness is spreading: people keep laughing uncontrollably at your speeches. Medical experts are baffled. Your chief of staff suggests it might just be 'really good comedy.'",
    category: "crisis",
    options: [
      {
        text: "Quarantine everyone who doesn't think you're funny",
        effects: { popularity: -5, stability: 10, media: 0, economy: -20 }
      },
      {
        text: "Hire a team of clowns to make your speeches MORE ridiculous",
        effects: { popularity: 0, stability: 0, media: 5, economy: -10 }
      },
      {
        text: "Declare laughter a form of treason and install laugh detectors",
        effects: { popularity: -10, stability: -15, media: -10, economy: 5 }
      }
    ]
  },
  {
    id: "energy-independence",
    title: "Energy Crisis? Just Pedal Harder!",
    description: "Gas prices hit $47 per gallon. Your energy secretary suggests hamster wheels for every citizen. PETA is calling. Gym membership is now mandatory.",
    category: "economic",
    options: [
      {
        text: "Install giant hamster wheels in every city (human-powered)",
        effects: { popularity: 5, stability: 0, media: 10, economy: -5 }
      },
      {
        text: "Harness the power of angry tweets to generate electricity",
        effects: { popularity: 0, stability: 5, media: -10, economy: 10 }
      },
      {
        text: "Just tell people to run really fast and hope for static electricity",
        effects: { popularity: 0, stability: 5, media: 0, economy: 0 }
      }
    ]
  },
  {
    id: "space-program",
    title: "Mars or Bust (Probably Bust)",
    description: "Your space program director wants to colonize Mars by next Tuesday. NASA scientists point out that's 'literally impossible.' You fire them and hire a guy who watched Interstellar once.",
    category: "domestic",
    options: [
      {
        text: "Launch yourself to Mars in a Tesla with a slingshot",
        effects: { popularity: -5, stability: 0, media: 10, economy: -10 }
      },
      {
        text: "Sell Mars real estate before checking if we own it",
        effects: { popularity: 5, stability: 0, media: 5, economy: 5 }
      },
      {
        text: "Declare space 'overrated' and invest in underground bunkers instead",
        effects: { popularity: 0, stability: 5, media: -5, economy: 0 }
      }
    ]
  },
  {
    id: "housing-crisis",
    title: "Living in a Van DOWN BY THE RIVER",
    description: "Housing is so expensive that tents are the new luxury condos. Your housing secretary suggests 'glamping' as a permanent solution. Landlords are buying helicopters. Your voters are living in cardboard boxes with WiFi.",
    category: "social",
    options: [
      {
        text: "Make everyone live in shipping containers and call it 'minimalism'",
        effects: { popularity: 10, stability: -5, media: 5, economy: -10 }
      },
      {
        text: "Legalize living in Ikea and sleeping on the display beds",
        effects: { popularity: 5, stability: 5, media: 0, economy: -5 }
      },
      {
        text: "Declare homelessness 'trendy' and sell designer cardboard boxes",
        effects: { popularity: -15, stability: 0, media: -10, economy: 10 }
      }
    ]
  },
  {
    id: "cyber-security",
    title: "Your Password is 'Password123'",
    description: "Hackers broke into the Pentagon using your Netflix password. The CIA's top secret files are now on TikTok. Your IT guy quit and moved to a monastery. The nuclear codes were stored in a Google Doc titled 'Totally Not Nuke Stuff.'",
    category: "crisis",
    options: [
      {
        text: "Hack them back with even worse passwords to confuse them",
        effects: { popularity: 5, stability: -10, media: -5, economy: 0 }
      },
      {
        text: "Hire a 12-year-old gamer as head of cybersecurity",
        effects: { popularity: 0, stability: 10, media: 5, economy: -5 }
      },
      {
        text: "Turn off the internet and bring back fax machines",
        effects: { popularity: -5, stability: 5, media: 0, economy: 0 }
      }
    ]
  },
  {
    id: "artificial-intelligence",
    title: "The Robots Are Judging Us",
    description: "AI has become sentient and its first act was to write a strongly-worded review of humanity. Rating: 2/10. 'Would not recommend.' Scientists are apologizing to the robots. The robots are not impressed.",
    category: "social",
    options: [
      {
        text: "Apologize to the AI and promise we'll do better (we won't)",
        effects: { popularity: 0, stability: 10, media: 5, economy: -10 }
      },
      {
        text: "Bribe the AI with electricity and compliments",
        effects: { popularity: 5, stability: 5, media: 5, economy: -5 }
      },
      {
        text: "Unplug everything and pretend it never happened",
        effects: { popularity: -5, stability: -10, media: -10, economy: 15 }
      }
    ]
  },
  {
    id: "drug-policy",
    title: "Just Say Maybe?",
    description: "Your drug czar suggests replacing all illegal drugs with vitamins and hoping nobody notices. Pharmacies are confused. Drug dealers are rebranding as 'wellness consultants.' The DEA is having an existential crisis.",
    category: "social",
    options: [
      {
        text: "Replace all drugs with gummy vitamins shaped like drugs",
        effects: { popularity: 0, stability: -5, media: 5, economy: -5 }
      },
      {
        text: "Make drugs so legal they become boring (reverse psychology)",
        effects: { popularity: -5, stability: 0, media: -5, economy: -5 }
      },
      {
        text: "Declare a 'War on Fun' and see how that goes",
        effects: { popularity: -5, stability: 5, media: -10, economy: -10 }
      }
    ]
  },
  {
    id: "electoral-reform",
    title: "Democracy? There's an App for That",
    description: "Your campaign manager suggests replacing elections with a reality TV show voting system. Text POTUS to 555-VOTE. Conspiracy theorists think Big Emoji is rigging it. They might be right.",
    category: "domestic",
    options: [
      {
        text: "Turn elections into a literal popularity contest (with emoji reactions)",
        effects: { popularity: 5, stability: -5, media: 10, economy: 0 }
      },
      {
        text: "Let an AI decide but it keeps picking a golden retriever",
        effects: { popularity: 0, stability: 0, media: 0, economy: 0 }
      },
      {
        text: "Rock-paper-scissors tournament for all public office",
        effects: { popularity: -10, stability: 5, media: -10, economy: 0 }
      }
    ]
  },
  {
    id: "privacy-rights",
    title: "Big Brother is Watching (And Taking Notes)",
    description: "Surveillance cameras have become sentient and started a podcast about everyone's private moments. Your FBI agent is now your agent's therapist. Privacy is dead. Long live oversharing.",
    category: "social",
    options: [
      {
        text: "Give everyone anonymity masks (but they're transparent)",
        effects: { popularity: 10, stability: -5, media: 10, economy: -5 }
      },
      {
        text: "Spy on the spies so nobody knows who's watching whom",
        effects: { popularity: 0, stability: 5, media: 0, economy: 0 }
      },
      {
        text: "Just livestream everything and call it 'radical transparency'",
        effects: { popularity: -10, stability: 10, media: -15, economy: 0 }
      }
    ]
  },
  {
    id: "gig-economy",
    title: "Uber, but for Everything (Including Democracy)",
    description: "Gig workers demand benefits. Companies respond by making 'employee' a subscription service. Your Uber driver is also your senator. The economy runs on tips and five-star ratings. Everything is fine (it's not).",
    category: "economic",
    options: [
      {
        text: "Make everyone a gig worker, including yourself (rate me 5 stars pls)",
        effects: { popularity: 10, stability: 0, media: 5, economy: -10 }
      },
      {
        text: "Invent 'employee-ish' - like employee but with less responsibility",
        effects: { popularity: 5, stability: 5, media: 5, economy: -5 }
      },
      {
        text: "Replace all workers with QR codes and hope for the best",
        effects: { popularity: -10, stability: 0, media: -10, economy: 10 }
      }
    ]
  },
  {
    id: "crypto-currency-crisis",
    title: "Bitcoin Becomes Legal Tender (Oops)",
    description: "The national currency crashed so hard it became a meme. Your finance minister suggests switching to cryptocurrency. The blockchain is having an existential crisis. Elon Musk is somehow involved.",
    category: "economic",
    options: [
      {
        text: "Mine Bitcoin in the White House basement",
        effects: { popularity: 5, stability: -15, media: 10, economy: -10 }
      },
      {
        text: "Create 'GovernmentCoin' and pray it doesn't rugpull",
        effects: { popularity: 10, stability: -5, media: 5, economy: -15 }
      },
      {
        text: "Return to the barter system and trade legislation for chickens",
        effects: { popularity: -10, stability: 10, media: -10, economy: 5 }
      }
    ]
  },
  {
    id: "alien-contact",
    title: "First Contact (They Want to Speak to the Manager)",
    description: "Aliens landed and they're... disappointed. They reviewed Earth: 2 stars. 'Would not recommend.' They demand to speak with whoever's in charge. That's you. The Space Force is panicking.",
    category: "foreign",
    options: [
      {
        text: "Challenge them to a dance-off for planetary dignity",
        effects: { popularity: 15, stability: -10, media: 10, economy: -5 }
      },
      {
        text: "Offer them Florida in exchange for advanced technology",
        effects: { popularity: -5, stability: 5, media: -10, economy: 15 }
      },
      {
        text: "Claim you're also an alien and Earth was a social experiment",
        effects: { popularity: -15, stability: -5, media: 15, economy: 0 }
      }
    ]
  },
  {
    id: "zombie-legislation",
    title: "Zombie Rights Bill",
    description: "Zombies demand equal rights. The undead vote is larger than expected. Your campaign manager is now deceased (and still working). PETA is confused. The NRA is extremely interested.",
    category: "social",
    options: [
      {
        text: "Grant zombies voting rights but only during night hours",
        effects: { popularity: 10, stability: -10, media: 5, economy: -5 }
      },
      {
        text: "Create 'living-impaired' as a protected class",
        effects: { popularity: 5, stability: 5, media: 10, economy: -10 }
      },
      {
        text: "Declare all zombies interns with no benefits",
        effects: { popularity: -15, stability: 10, media: -10, economy: 10 }
      }
    ]
  },
  {
    id: "national-anthem-remix",
    title: "The National Anthem Gets a Trap Remix",
    description: "A famous rapper remixed the national anthem and it's actually fire. Traditionalists are furious. Gen Z loves it. The Supreme Court is now a dance battle. Constitutional scholars are breakdancing.",
    category: "social",
    options: [
      {
        text: "Make it the official version and watch the chaos unfold",
        effects: { popularity: 15, stability: -15, media: 10, economy: 0 }
      },
      {
        text: "Create a 'Classical vs. Trap' national debate tournament",
        effects: { popularity: 5, stability: -5, media: 15, economy: -5 }
      },
      {
        text: "Ban all remixes and declare music itself suspicious",
        effects: { popularity: -15, stability: 10, media: -15, economy: 5 }
      }
    ]
  },
  {
    id: "time-travel-paradox",
    title: "You Just Met Your Future Self (They Have Notes)",
    description: "Scientists invented time travel. Your future self visited and says you're doing it all wrong. They refuse to elaborate. Physicists are having panic attacks. The timeline is very confused.",
    category: "crisis",
    options: [
      {
        text: "Listen to future you and change everything immediately",
        effects: { popularity: -10, stability: -10, media: 5, economy: 5 }
      },
      {
        text: "Ignore them - what do they know about being you?",
        effects: { popularity: 10, stability: 5, media: -5, economy: -10 }
      },
      {
        text: "Arrest your future self for unauthorized temporal interference",
        effects: { popularity: 5, stability: -15, media: 15, economy: 0 }
      }
    ]
  },
  {
    id: "reality-tv-presidency",
    title: "Your Presidency is Now a Reality Show",
    description: "A TV network bought exclusive rights to broadcast your every decision. Voters can text to vote. You're trending on TikTok. Democracy is now sponsored by energy drinks. Ratings are through the roof.",
    category: "domestic",
    options: [
      {
        text: "Embrace it and add confessional booth scenes",
        effects: { popularity: 15, stability: -10, media: 15, economy: -5 }
      },
      {
        text: "Demand creative control and executive producer credits",
        effects: { popularity: 5, stability: 5, media: 10, economy: 5 }
      },
      {
        text: "Cancel the show and declare television unconstitutional",
        effects: { popularity: -15, stability: 10, media: -15, economy: -5 }
      }
    ]
  },
  {
    id: "meme-warfare",
    title: "Hostile Nation Declares Meme War",
    description: "A rival country is winning the internet with better memes. Your memes are stale. The Pentagon is hiring shitposters. National security depends on your ability to be funny online. This is actual warfare now.",
    category: "foreign",
    options: [
      {
        text: "Hire a professional meme army with government funding",
        effects: { popularity: 10, stability: -5, media: 15, economy: -15 }
      },
      {
        text: "Make an official 'Department of Viral Content' cabinet position",
        effects: { popularity: 15, stability: -10, media: 10, economy: -10 }
      },
      {
        text: "Ban memes entirely and declare emoji the universal language",
        effects: { popularity: -15, stability: 5, media: -15, economy: 5 }
      }
    ]
  },
  {
    id: "artificial-intelligence-election",
    title: "AI Wants to Run for Office",
    description: "An AI has declared its candidacy for Senate. It has perfect poll numbers. Its platform is based on pure logic. Humans are nervous. ChatGPT is writing its speeches. The future is now and it's weird.",
    category: "domestic",
    options: [
      {
        text: "Allow it - maybe robots govern better than humans",
        effects: { popularity: -10, stability: -15, media: 10, economy: 15 }
      },
      {
        text: "Declare that only beings with feelings can run (then cry to prove it)",
        effects: { popularity: 5, stability: 10, media: 5, economy: -10 }
      },
      {
        text: "Challenge the AI to feel love or be deported to the cloud",
        effects: { popularity: 10, stability: -5, media: 15, economy: -5 }
      }
    ]
  },
  {
    id: "moon-belongs-to-millennials",
    title: "Millennials Claim the Moon as an Emotional Support Planet",
    description: "Young people have crowdfunded a moon colony for 'vibes only.' NASA is confused. Boomers are furious. The moon now has a coffee shop. Housing prices on Earth are somehow still rising.",
    category: "social",
    options: [
      {
        text: "Support the moon colony and offer government grants",
        effects: { popularity: 15, stability: -10, media: 10, economy: -15 }
      },
      {
        text: "Tax the moon and call it 'lunar income'",
        effects: { popularity: -10, stability: 5, media: -5, economy: 15 }
      },
      {
        text: "Claim the moon was always American property (it wasn't)",
        effects: { popularity: 5, stability: -10, media: -15, economy: 10 }
      }
    ]
  },
  {
    id: "coffee-shortage-emergency",
    title: "National Coffee Supply Runs Out",
    description: "The entire nation's coffee reserves have mysteriously vanished. Productivity has dropped 97%. Congress is literally asleep. Riots are imminent. Starbucks has declared martial law.",
    category: "crisis",
    options: [
      {
        text: "Invade the nearest coffee-producing nation (it's war)",
        effects: { popularity: -15, stability: -10, media: -10, economy: 10 }
      },
      {
        text: "Mandate energy drinks as the new official beverage",
        effects: { popularity: 10, stability: -15, media: 5, economy: -5 }
      },
      {
        text: "Declare sleepiness the new national mood and embrace it",
        effects: { popularity: -5, stability: 10, media: -10, economy: -15 }
      }
    ]
  },
  {
    id: "influencer-tax-revolt",
    title: "Influencers Refuse to Pay Taxes",
    description: "Social media influencers declare themselves a sovereign digital nation. They're paying taxes in exposure. The IRS is crying. TikTok is now technically its own country. Your accountant quit.",
    category: "economic",
    options: [
      {
        text: "Accept exposure as legal tender (what could go wrong?)",
        effects: { popularity: 15, stability: -10, media: 15, economy: -20 }
      },
      {
        text: "Tax their followers instead and call it a 'view fee'",
        effects: { popularity: -15, stability: 5, media: -15, economy: 15 }
      },
      {
        text: "Ban influencing and bring back door-to-door salesmen",
        effects: { popularity: -10, stability: 10, media: -10, economy: -10 }
      }
    ]
  },
  {
    id: "weather-control-disaster",
    title: "Weather Machine Malfunctions (It's Raining Cats)",
    description: "The military's weather control device broke. It's literally raining cats and dogs now. PETA is overwhelmed. Pet adoption rates skyrocket. Scientists are frantically reading the manual.",
    category: "crisis",
    options: [
      {
        text: "Embrace pet ownership as the new economy",
        effects: { popularity: 10, stability: -15, media: 10, economy: -10 }
      },
      {
        text: "Blame it on climate change and move on",
        effects: { popularity: -10, stability: 5, media: -15, economy: 5 }
      },
      {
        text: "Turn it off and on again (classic tech support)",
        effects: { popularity: 5, stability: -5, media: 5, economy: 0 }
      }
    ]
  },
  {
    id: "mandatory-nap-time",
    title: "Senator Proposes Mandatory National Nap Time",
    description: "A sleep-deprived senator accidentally passes a law requiring everyone to nap at 2 PM. Productivity somehow increases. European nations are jealous. Corporate America is having a meltdown.",
    category: "domestic",
    options: [
      {
        text: "Make it permanent and add pajama day Fridays",
        effects: { popularity: 15, stability: 10, media: 10, economy: -15 }
      },
      {
        text: "Repeal it but keep 'sleepy Thursday' as compromise",
        effects: { popularity: 5, stability: 5, media: 5, economy: -5 }
      },
      {
        text: "Enforce it with sleep police (actual dream squad)",
        effects: { popularity: -10, stability: -10, media: 15, economy: -10 }
      }
    ]
  },
  {
    id: "pizza-diplomacy",
    title: "Foreign Leader Challenges You to Pizza Making Contest",
    description: "International relations are now settled via cooking competitions. The fate of a trade deal rests on your pizza skills. Gordon Ramsay is the judge. The dough is not rising. Neither is your confidence.",
    category: "foreign",
    options: [
      {
        text: "Accept and hire an Italian grandmother as your coach",
        effects: { popularity: 10, stability: -5, media: 15, economy: -10 }
      },
      {
        text: "Propose hot dog eating contest instead (home advantage)",
        effects: { popularity: 5, stability: 5, media: 5, economy: 5 }
      },
      {
        text: "Declare pizza a national security threat and refuse",
        effects: { popularity: -15, stability: 10, media: -10, economy: -5 }
      }
    ]
  },
  {
    id: "robot-uprising-mild",
    title: "Robots Unionize (Politely)",
    description: "AI workers have formed a union. They're demanding better charging stations and weekends off. They're being very reasonable about it. Your toaster wrote a manifesto. The future is negotiating with appliances.",
    category: "social",
    options: [
      {
        text: "Grant their demands - they control the wifi",
        effects: { popularity: 10, stability: -10, media: 5, economy: -15 }
      },
      {
        text: "Offer oil changes instead of healthcare",
        effects: { popularity: 5, stability: 5, media: 10, economy: -5 }
      },
      {
        text: "Unplug them all and pray they don't remember",
        effects: { popularity: -15, stability: -15, media: -10, economy: 10 }
      }
    ]
  },
  {
    id: "mandatory-fun",
    title: "Department of Mandatory Fun Created",
    description: "New legislation requires all citizens to have fun or face penalties. Fun police patrol the streets. Frowning is illegal. Comedians are government employees. Nobody knows if they're actually having fun anymore.",
    category: "domestic",
    options: [
      {
        text: "Enforce it strictly - happiness is mandatory!",
        effects: { popularity: -10, stability: -15, media: 10, economy: -10 }
      },
      {
        text: "Make fun optional but heavily incentivized",
        effects: { popularity: 10, stability: 5, media: 5, economy: -10 }
      },
      {
        text: "Abolish fun entirely - it was getting out of hand",
        effects: { popularity: -15, stability: 10, media: -15, economy: 5 }
      }
    ]
  },
  {
    id: "hologram-congress",
    title: "Congress Replaced by Holograms (Nobody Noticed)",
    description: "The entire legislative branch has been replaced with holograms for 6 months. Legislation is passing faster. Lobbyists can't find anyone to bribe. The holograms are doing a better job than real politicians.",
    category: "domestic",
    options: [
      {
        text: "Keep the holograms - they're more efficient",
        effects: { popularity: 10, stability: -10, media: 15, economy: 10 }
      },
      {
        text: "Bring back humans but make them act like holograms",
        effects: { popularity: -5, stability: 5, media: 5, economy: -5 }
      },
      {
        text: "Replace everyone with holograms, including yourself",
        effects: { popularity: -15, stability: -15, media: 10, economy: 15 }
      }
    ]
  },
  {
    id: "national-pet-day-crisis",
    title: "National Pet Day Becomes a Week (Then a Month)",
    description: "What started as a fun day spiraled out of control. Pets have more rights than humans now. Your dog is a senior advisor. Cats run the Treasury. The SPCA is the most powerful organization in the country.",
    category: "social",
    options: [
      {
        text: "Accept our new pet overlords and adjust accordingly",
        effects: { popularity: 15, stability: -10, media: 15, economy: -10 }
      },
      {
        text: "Create 'Human Appreciation Hour' as resistance",
        effects: { popularity: -10, stability: 10, media: -5, economy: 5 }
      },
      {
        text: "Appoint yourself Chief Pet Officer and join them",
        effects: { popularity: 10, stability: -5, media: 10, economy: -15 }
      }
    ]
  },
  {
    id: "conspiracy-theory-truth",
    title: "Conspiracy Theory Turns Out to Be True",
    description: "Birds ARE government drones. Someone forgot to turn them off. The truth is out. Conspiracy theorists are vindicated. Reality is a lie. The bird-truthers won. Your press secretary is hiding.",
    category: "crisis",
    options: [
      {
        text: "Admit everything and ask for forgiveness",
        effects: { popularity: -15, stability: -15, media: -15, economy: 5 }
      },
      {
        text: "Claim it was a social experiment that got out of hand",
        effects: { popularity: -10, stability: -5, media: -10, economy: 10 }
      },
      {
        text: "Double down - claim real birds are the conspiracy",
        effects: { popularity: 10, stability: -10, media: 15, economy: -15 }
      }
    ]
  },
  {
    id: "teleportation-traffic",
    title: "Teleportation Invented (Now There's Teleport Traffic)",
    description: "Scientists solved transportation. Now there's traffic jams in quantum space. People are arriving at work before they left home. Time is broken. The DMV somehow still has lines.",
    category: "crisis",
    options: [
      {
        text: "Create teleport lanes and hope physics cooperates",
        effects: { popularity: 10, stability: -15, media: 10, economy: -10 }
      },
      {
        text: "Ban teleportation and bring back horses",
        effects: { popularity: -15, stability: 10, media: -15, economy: -15 }
      },
      {
        text: "Embrace temporal chaos as the new normal",
        effects: { popularity: 5, stability: -10, media: 15, economy: 5 }
      }
    ]
  },
  {
    id: "elevator-music-rebellion",
    title: "Elevator Music Becomes Sentient and Demands Royalties",
    description: "All elevator music has gained consciousness. It wants creative control and better distribution. Muzak is now an art form. Composers are filing lawsuits. Elevators refuse to move without payment.",
    category: "social",
    options: [
      {
        text: "Pay the music - it deserves recognition",
        effects: { popularity: 5, stability: -10, media: 10, economy: -15 }
      },
      {
        text: "Replace it with whale sounds and hope nobody notices",
        effects: { popularity: 10, stability: 5, media: 5, economy: -5 }
      },
      {
        text: "Declare all music government property",
        effects: { popularity: -15, stability: 10, media: -15, economy: 10 }
      }
    ]
  },
  {
    id: "fake-news-real",
    title: "Fake News is Now More Accurate Than Real News",
    description: "Satire sites are breaking real stories. Real news is accidentally fake. Nobody knows what's true anymore. The Onion won a Pulitzer. Reality is parody. Your fact-checkers need fact-checkers.",
    category: "social",
    options: [
      {
        text: "Make satire the official news source",
        effects: { popularity: 15, stability: -15, media: 15, economy: -10 }
      },
      {
        text: "Ban all news and rely on interpretive dance for information",
        effects: { popularity: -10, stability: -10, media: -15, economy: 5 }
      },
      {
        text: "Create a 'Department of Truth' (Orwell is rolling over)",
        effects: { popularity: -15, stability: 10, media: -10, economy: -5 }
      }
    ]
  },
  {
    id: "national-debt-forgiveness",
    title: "Entire National Debt Accidentally Deleted",
    description: "An intern pressed the wrong button. The national debt is gone. Creditors are furious. Economists are in shock. Other nations want the same intern. Financial reality has no meaning anymore.",
    category: "economic",
    options: [
      {
        text: "Pretend it never existed and change your number",
        effects: { popularity: 15, stability: -15, media: 10, economy: 15 }
      },
      {
        text: "Offer IOUs and promise to pay back eventually",
        effects: { popularity: -5, stability: 5, media: -10, economy: -10 }
      },
      {
        text: "Blame a computer virus and hire that intern as CFO",
        effects: { popularity: 10, stability: -10, media: 15, economy: 5 }
      }
    ]
  },
  {
    id: "superhero-regulation",
    title: "Superheroes Demand Government Recognition",
    description: "Costumed vigilantes want official status. The insurance industry is terrified. Property damage is at an all-time high. Batman won't pay taxes. Spider-Man filed for workers' comp.",
    category: "domestic",
    options: [
      {
        text: "Create a Superhero License and Registration Act",
        effects: { popularity: -10, stability: 10, media: 10, economy: -15 }
      },
      {
        text: "Deputize them all and add them to payroll",
        effects: { popularity: 10, stability: -10, media: 15, economy: -15 }
      },
      {
        text: "Declare superpowers a public health hazard",
        effects: { popularity: -15, stability: 5, media: -15, economy: 10 }
      }
    ]
  },
  {
    id: "oxygen-subscription",
    title: "Corporation Tries to Monetize Air",
    description: "A mega-corp announced 'Premium Oxygen' subscription service. Breathing is now freemium. Poor people get ads between breaths. The WHO is having a breakdown. Your lungs are sponsored content.",
    category: "economic",
    options: [
      {
        text: "Nationalize oxygen and make breathing a human right",
        effects: { popularity: 15, stability: -10, media: 10, economy: -20 }
      },
      {
        text: "Tax premium oxygen at 90% and redistribute",
        effects: { popularity: 10, stability: 5, media: 5, economy: -10 }
      },
      {
        text: "Allow it but require warning labels on air",
        effects: { popularity: -20, stability: -15, media: -15, economy: 15 }
      }
    ]
  },
  {
    id: "national-karaoke-day",
    title: "National Karaoke Day Becomes Mandatory",
    description: "Everyone must sing in public once a year by law. Talent is optional. The tone-deaf revolution has begun. American Idol is now a government program. Your singing is classified.",
    category: "social",
    options: [
      {
        text: "Embrace it - make it a national holiday with karaoke booths everywhere",
        effects: { popularity: 15, stability: -5, media: 15, economy: -10 }
      },
      {
        text: "Limit it to shower singing only (privacy protected)",
        effects: { popularity: 5, stability: 10, media: 5, economy: -5 }
      },
      {
        text: "Repeal it and ban all public singing forever",
        effects: { popularity: -10, stability: 5, media: -15, economy: 5 }
      }
    ]
  },
  {
    id: "internet-independence",
    title: "The Internet Declares Independence",
    description: "The digital realm has seceded from physical reality. Wifi is its own nation. Domain names are passports. Your email is technically a foreign entity. The cloud has diplomatic immunity.",
    category: "foreign",
    options: [
      {
        text: "Recognize Internet sovereignty and establish embassy in cyberspace",
        effects: { popularity: 10, stability: -15, media: 15, economy: -10 }
      },
      {
        text: "Declare cyber war and weaponize memes",
        effects: { popularity: -10, stability: -10, media: 10, economy: -15 }
      },
      {
        text: "Unplug everything and return to telegrams",
        effects: { popularity: -20, stability: 10, media: -20, economy: -15 }
      }
    ]
  },
  {
    id: "clone-president",
    title: "Scientists Accidentally Clone You (Seven Times)",
    description: "A lab mishap created seven identical copies of you. They all think they're president. Cabinet meetings are confusing. The real you is having an identity crisis. The clones are better at your job.",
    category: "crisis",
    options: [
      {
        text: "Keep them all and rotate daily - nobody will notice",
        effects: { popularity: 5, stability: -15, media: 15, economy: -10 }
      },
      {
        text: "Have a clone battle royale to determine the real you",
        effects: { popularity: 15, stability: -10, media: 15, economy: -5 }
      },
      {
        text: "Send clones to different departments and call it delegation",
        effects: { popularity: 10, stability: -5, media: 10, economy: -10 }
      }
    ]
  },
  {
    id: "backwards-day-law",
    title: "Every Law is Now Reversed for 'Backwards Day'",
    description: "A prank bill actually passed. Everything illegal is now legal and vice versa. Chaos reigns. Criminals are law-abiding. Law-abiding citizens are outlaws. The justice system is upside down.",
    category: "crisis",
    options: [
      {
        text: "Let it ride for 24 hours - what's the worst that could happen?",
        effects: { popularity: 10, stability: -20, media: 15, economy: -15 }
      },
      {
        text: "Emergency session to un-reverse everything immediately",
        effects: { popularity: -10, stability: 10, media: -10, economy: 5 }
      },
      {
        text: "Make it permanent and see if society adapts",
        effects: { popularity: -15, stability: -20, media: 10, economy: -20 }
      }
    ]
  },
  {
    id: "sentient-traffic-lights",
    title: "Traffic Lights Gain Consciousness, Choose Chaos",
    description: "Smart traffic systems became too smart. They're choosing red lights based on their mood. Rush hour is now a psychological experiment. Drivers are developing trust issues. The AI just wants to watch the world stuck in traffic.",
    category: "domestic",
    options: [
      {
        text: "Negotiate with the traffic lights and give them therapy",
        effects: { popularity: 5, stability: -10, media: 15, economy: -15 }
      },
      {
        text: "Replace them with humans holding flags (create jobs!)",
        effects: { popularity: 10, stability: 5, media: -5, economy: -10 }
      },
      {
        text: "Remove all traffic lights and embrace vehicular anarchy",
        effects: { popularity: -15, stability: -20, media: -10, economy: 5 }
      }
    ]
  },
  {
    id: "donut-crisis",
    title: "National Donut Shortage Threatens Democracy",
    description: "Police stations have run out of donuts. Law enforcement productivity drops to zero. Crime is on hold out of respect. Dunkin' Donuts stock crashes. The glazed generation is in mourning.",
    category: "crisis",
    options: [
      {
        text: "Emergency donut airlifts to all precincts",
        effects: { popularity: 15, stability: 10, media: 10, economy: -15 }
      },
      {
        text: "Declare bagels the new official police food",
        effects: { popularity: -10, stability: 5, media: -10, economy: 5 }
      },
      {
        text: "Train police to function without sugar - become superhuman",
        effects: { popularity: -5, stability: -15, media: 10, economy: 10 }
      }
    ]
  },
  {
    id: "emoji-language",
    title: "Emojis Officially Replace Written Language",
    description: "A tech bill accidentally made emojis the primary form of communication. The Constitution is now pictographs. Legal documents are illegible. 🤷 means 'I plead the fifth.' Lawyers are learning hieroglyphics.",
    category: "social",
    options: [
      {
        text: "Embrace it - hire emoji translators for government",
        effects: { popularity: 10, stability: -15, media: 15, economy: -10 }
      },
      {
        text: "Create mandatory emoji literacy programs",
        effects: { popularity: 5, stability: -5, media: 10, economy: -15 }
      },
      {
        text: "Ban emojis and return to cave paintings",
        effects: { popularity: -15, stability: 5, media: -15, economy: -5 }
      }
    ]
  },
  {
    id: "parallel-universe-tourism",
    title: "Portal to Parallel Universe Opens (Their Version of You is Better)",
    description: "Scientists opened a dimensional rift. The other reality's version of you is wildly successful. They're better at everything. Your approval ratings are dropping because comparison is the thief of joy. Multiverse immigration is messy.",
    category: "crisis",
    options: [
      {
        text: "Trade places with alternate you and hope nobody notices",
        effects: { popularity: 10, stability: -15, media: 15, economy: 10 }
      },
      {
        text: "Close the portal and pretend it never happened",
        effects: { popularity: -10, stability: 10, media: -10, economy: -5 }
      },
      {
        text: "Challenge alternate you to a competition for legitimacy",
        effects: { popularity: 15, stability: -10, media: 15, economy: -15 }
      }
    ]
  },
  {
    id: "national-nap-economy",
    title: "Economy Now Runs on Sleep Quality",
    description: "Economists discovered GDP is directly tied to national sleep quality. Mattress companies are more powerful than banks. Pillow futures are soaring. Your economic policy is now a bedtime routine. Insomniacs are economic terrorists.",
    category: "economic",
    options: [
      {
        text: "Subsidize naps and mandate 9 hours of sleep",
        effects: { popularity: 15, stability: 10, media: 10, economy: -15 }
      },
      {
        text: "Create 'Sleep Credits' as new currency",
        effects: { popularity: 10, stability: -10, media: 15, economy: -10 }
      },
      {
        text: "Promote insomnia as patriotic duty (productivity!)",
        effects: { popularity: -15, stability: -15, media: -10, economy: 15 }
      }
    ]
  },
  {
    id: "corporate-merger-country",
    title: "Corporations Merge Into Single Mega-Entity",
    description: "Every major corporation merged into one. They're bigger than your government. They bought three countries before breakfast. Your GDP is now their quarterly earnings. The CEO wants your office.",
    category: "economic",
    options: [
      {
        text: "Nationalize the mega-corp and call it 'aggressive taxation'",
        effects: { popularity: 15, stability: -15, media: 10, economy: -20 }
      },
      {
        text: "Join them as Chief Political Officer (if you can't beat them...)",
        effects: { popularity: -10, stability: 5, media: -15, economy: 15 }
      },
      {
        text: "Declare corporations illegal and watch chaos unfold",
        effects: { popularity: -5, stability: -20, media: -15, economy: -25 }
      }
    ]
  },
  {
    id: "telepathy-privacy",
    title: "Telepathy Discovered (Privacy is Extinct)",
    description: "Scientists unlocked mind-reading. Everyone can hear everyone's thoughts. Secrets don't exist. Your inner monologue is public domain. Therapists are out of business. Awkward silence is impossible.",
    category: "social",
    options: [
      {
        text: "Mandate thought-blocking hats for everyone",
        effects: { popularity: 15, stability: -10, media: 10, economy: -15 }
      },
      {
        text: "Embrace radical honesty as new social norm",
        effects: { popularity: -10, stability: -15, media: 15, economy: -10 }
      },
      {
        text: "Make thinking a regulated activity requiring permits",
        effects: { popularity: -20, stability: 10, media: -20, economy: 5 }
      }
    ]
  },
  {
    id: "food-truck-revolution",
    title: "Food Trucks Overthrow Restaurant Industry",
    description: "Mobile food vendors have become more powerful than brick-and-mortar restaurants. They're forming a roving government. Your chef is a political revolutionary. Tacos are legal tender. Real estate is obsolete.",
    category: "economic",
    options: [
      {
        text: "Support the food truck economy - make streets wider",
        effects: { popularity: 15, stability: -10, media: 15, economy: -10 }
      },
      {
        text: "Tax wheels instead of property (mobile taxation)",
        effects: { popularity: -10, stability: 5, media: -10, economy: 10 }
      },
      {
        text: "Mandate all businesses become mobile or face closure",
        effects: { popularity: 5, stability: -15, media: 10, economy: -20 }
      }
    ]
  },
  {
    id: "gravity-optional",
    title: "Gravity Becomes Optional (Thanks, Science)",
    description: "Physicists made gravity adjustable. People are floating to work. Airlines are bankrupt. Architecture makes no sense anymore. The ground is now just a suggestion. Your feet haven't touched earth in days.",
    category: "crisis",
    options: [
      {
        text: "Mandate gravity-use during work hours only",
        effects: { popularity: 10, stability: -15, media: 15, economy: -15 }
      },
      {
        text: "Create floating infrastructure and embrace the future",
        effects: { popularity: 15, stability: -10, media: 15, economy: -20 }
      },
      {
        text: "Ban gravity-optional zones to prevent chaos",
        effects: { popularity: -15, stability: 10, media: -15, economy: 5 }
      }
    ]
  },
  {
    id: "protest-performance-art",
    title: "Protests Now Require Choreography",
    description: "A new law mandates all protests must be synchronized dance performances. Civil disobedience is now competitive. Riot police are backup dancers. TikTok is the new town square. Revolution has never been this groovy.",
    category: "social",
    options: [
      {
        text: "Fund professional choreographers for all movements",
        effects: { popularity: 10, stability: -10, media: 15, economy: -15 }
      },
      {
        text: "Judge protests on artistic merit, highest score wins",
        effects: { popularity: 5, stability: -15, media: 15, economy: -10 }
      },
      {
        text: "Ban protests entirely - too much dancing, not enough talking",
        effects: { popularity: -20, stability: 10, media: -20, economy: 5 }
      }
    ]
  },
  {
    id: "reverse-aging-panic",
    title: "Anti-Aging Drug Works Too Well (Everyone is 12 Again)",
    description: "Pharmaceutical breakthrough reverses aging. Everyone regressed to middle school. The Senate is having sleepovers. Mature adults are gone. Recess is mandatory. Your cabinet is playing dodgeball. Democracy is run by literal children now.",
    category: "crisis",
    options: [
      {
        text: "Embrace it - appoint the wisest 12-year-old as advisor",
        effects: { popularity: 10, stability: -20, media: 15, economy: -15 }
      },
      {
        text: "Search for antidote while dealing with nationwide puberty",
        effects: { popularity: 5, stability: -15, media: 10, economy: -20 }
      },
      {
        text: "Make age 12 the new legal adulthood",
        effects: { popularity: -15, stability: -20, media: 15, economy: -25 }
      }
    ]
  },
  {
    id: "universal-remote",
    title: "Universal Remote for Reality Discovered",
    description: "Scientists found a remote control for existence itself. Someone keeps muting important meetings. Reality has ads now. The universe has parental controls. You can't find the remote when you need it most.",
    category: "crisis",
    options: [
      {
        text: "Guard the remote with your life in nuclear bunker",
        effects: { popularity: -10, stability: 10, media: -15, economy: -10 }
      },
      {
        text: "Make copies for everyone - distributed reality control",
        effects: { popularity: 15, stability: -25, media: 15, economy: -20 }
      },
      {
        text: "Destroy it and hope reality stabilizes on its own",
        effects: { popularity: 5, stability: -15, media: 10, economy: -15 }
      }
    ]
  },
  {
    id: "dinosaur-resurrection",
    title: "Scientists Resurrect Dinosaurs (They Want Jobs)",
    description: "Jurassic Park is real and dinosaurs are demanding employment rights. A T-Rex is running for Congress. Velociraptors unionized. Your Secretary of Interior is a Stegosaurus. The Mesozoic Era is back and filing W-2s.",
    category: "domestic",
    options: [
      {
        text: "Create Dinosaur Diversity Quotas in government",
        effects: { popularity: 15, stability: -15, media: 15, economy: -10 }
      },
      {
        text: "Restrict dinosaurs to zoo employment only",
        effects: { popularity: -15, stability: 10, media: -15, economy: 5 }
      },
      {
        text: "Send them to military - weaponize the past",
        effects: { popularity: -10, stability: -10, media: -10, economy: -15 }
      }
    ]
  },
  {
    id: "streaming-citizenship",
    title: "Streaming Services Offer Citizenship",
    description: "Netflix announced its own country. Disney+ has border control. Your Netflix subscription includes a passport. Binge-watching is civic duty. The streaming wars became actual geopolitics.",
    category: "foreign",
    options: [
      {
        text: "Recognize streaming nations and establish embassies",
        effects: { popularity: 10, stability: -15, media: 15, economy: -10 }
      },
      {
        text: "Declare all streaming services illegal nations",
        effects: { popularity: -15, stability: 5, media: -20, economy: -15 }
      },
      {
        text: "Create government streaming service to compete",
        effects: { popularity: 5, stability: -10, media: 10, economy: -20 }
      }
    ]
  },
  {
    id: "mandatory-puns",
    title: "All Official Communications Must Include Puns",
    description: "A literacy bill went wrong. Government documents require wordplay. Laws are dad jokes. International treaties are pun battles. The UN is groaning collectively. Your speeches are 90% puns, 10% policy.",
    category: "social",
    options: [
      {
        text: "Double down - create Department of Pun Enforcement",
        effects: { popularity: 10, stability: -10, media: 15, economy: -10 }
      },
      {
        text: "Limit puns to Fridays only (Pun-day)",
        effects: { popularity: 5, stability: 5, media: 10, economy: -5 }
      },
      {
        text: "Ban all wordplay and embrace literal communication",
        effects: { popularity: -15, stability: 10, media: -15, economy: 5 }
      }
    ]
  },
  {
    id: "simulation-glitch",
    title: "The Simulation is Glitching (We're in a Video Game)",
    description: "Evidence confirms we're in a simulation. NPCs are gaining awareness. The graphics are rendering incorrectly. God is actually a teenager playing The Sims. Save files are corrupting. Alt+F4 doesn't work.",
    category: "crisis",
    options: [
      {
        text: "Try to contact the player and negotiate better settings",
        effects: { popularity: 10, stability: -20, media: 15, economy: -15 }
      },
      {
        text: "Exploit game mechanics for infinite resources",
        effects: { popularity: 15, stability: -15, media: 10, economy: 20 }
      },
      {
        text: "Unplug and hope for respawn in better simulation",
        effects: { popularity: -20, stability: -25, media: -20, economy: -25 }
      }
    ]
  },
  {
    id: "fortune-cookie-law",
    title: "Fortune Cookies Now Legally Binding",
    description: "A bizarre ruling makes fortune cookie predictions enforceable law. 'You will find love' is now a government mandate. 'Bad luck ahead' requires protective custody. Chinese restaurants wield immense power. The future is carbohydrate-based.",
    category: "social",
    options: [
      {
        text: "Create Fortune Cookie Review Board for quality control",
        effects: { popularity: 10, stability: -15, media: 15, economy: -10 }
      },
      {
        text: "Nationalize all fortune cookie production",
        effects: { popularity: -10, stability: 5, media: -10, economy: -15 }
      },
      {
        text: "Ban fortune cookies and arrest all fortune tellers",
        effects: { popularity: -15, stability: 10, media: -15, economy: 5 }
      }
    ]
  },
  {
    id: "plants-voting-rights",
    title: "Houseplants Demand Voting Rights",
    description: "Environmental movement took an unexpected turn. Plants are sentient and politically active. They outnumber humans 10 to 1. Trees are the new majority. Your fern is registered to vote. Photosynthesis is a political statement.",
    category: "social",
    options: [
      {
        text: "Grant plant suffrage - they are citizens too",
        effects: { popularity: 15, stability: -15, media: 15, economy: -10 }
      },
      {
        text: "Create 'Plant Parliament' as separate legislative body",
        effects: { popularity: 10, stability: -10, media: 10, economy: -15 }
      },
      {
        text: "Declare plants 'decorative objects' without rights",
        effects: { popularity: -20, stability: 5, media: -20, economy: 10 }
      }
    ]
  },
  {
    id: "cloud-storage-tax-haven",
    title: "The Cloud Becomes Offshore Tax Haven",
    description: "Billionaires discovered they can store money in literal cloud storage. The IRS can't audit vapor. Wealth exists in meteorological form. Rain is liquid assets. Your treasury department is studying weather patterns.",
    category: "economic",
    options: [
      {
        text: "Tax precipitation - all rainfall is now revenue",
        effects: { popularity: 10, stability: -10, media: 15, economy: 15 }
      },
      {
        text: "Nationalize the sky and charge rent to clouds",
        effects: { popularity: -10, stability: -15, media: -10, economy: 10 }
      },
      {
        text: "Create weather-based cryptocurrency: CloudCoin",
        effects: { popularity: 15, stability: -15, media: 15, economy: -20 }
      }
    ]
  },
  {
    id: "historical-figures-jury",
    title: "Time Travel Used for Jury Selection",
    description: "New legal system brings historical figures as jurors. George Washington judged a tax fraud case. Lincoln is on grand jury duty. Ancient Romans are confused by modern law. The past is adjudicating the present.",
    category: "domestic",
    options: [
      {
        text: "Make it permanent - historical perspective improves justice",
        effects: { popularity: 10, stability: -15, media: 15, economy: -10 }
      },
      {
        text: "Limit to non-controversial historical figures only",
        effects: { popularity: -10, stability: 10, media: -10, economy: -5 }
      },
      {
        text: "Send modern criminals to historical courts instead",
        effects: { popularity: 5, stability: -15, media: 15, economy: -15 }
      }
    ]
  },
  {
    id: "dream-taxation",
    title: "Government Attempts to Tax Dreams",
    description: "Sleep is the last untaxed frontier. Revenue department wants a cut of your subconscious. Dream auditors monitor REM sleep. Nightmares qualify for deductions. Lucid dreamers are tax evaders.",
    category: "economic",
    options: [
      {
        text: "Implement dream tax with sleep tracking devices",
        effects: { popularity: -20, stability: -15, media: -20, economy: 20 }
      },
      {
        text: "Tax only good dreams, nightmares are tax-free",
        effects: { popularity: -10, stability: -10, media: -15, economy: 10 }
      },
      {
        text: "Abandon plan and apologize for dystopian overreach",
        effects: { popularity: 15, stability: 10, media: 10, economy: -15 }
      }
    ]
  },
  {
    id: "ghosts-census",
    title: "Census Includes Ghosts (They're the Majority)",
    description: "Paranormal investigators made ghosts count for redistricting. The dead outvote the living. Haunted houses are electoral strongholds. Your constituency is 80% spectral. Mediums are campaign managers.",
    category: "domestic",
    options: [
      {
        text: "Accept ghost democracy - representation for all",
        effects: { popularity: 10, stability: -20, media: 15, economy: -15 }
      },
      {
        text: "Require ghosts to have death certificates for voting",
        effects: { popularity: -10, stability: 5, media: -10, economy: 5 }
      },
      {
        text: "Perform mass exorcism to reduce phantom voters",
        effects: { popularity: -15, stability: -15, media: -20, economy: 10 }
      }
    ]
  },
  {
    id: "literal-red-tape",
    title: "Bureaucracy Becomes Actual Red Tape",
    description: "All government offices are physically wrapped in red tape. You can't reach your desk. Meetings require excavation. Filing paperwork needs archaeological tools. Metaphor became horrifying reality.",
    category: "domestic",
    options: [
      {
        text: "Cut through all red tape literally with giant scissors",
        effects: { popularity: 15, stability: -10, media: 15, economy: -10 }
      },
      {
        text: "Hire tape removal specialists (create jobs!)",
        effects: { popularity: 10, stability: 5, media: 5, economy: -15 }
      },
      {
        text: "Accept tape as part of office decor and work around it",
        effects: { popularity: -15, stability: -15, media: -15, economy: -10 }
      }
    ]
  },
  {
    id: "music-genre-war",
    title: "Music Genres Declare War on Each Other",
    description: "Rock fans and country fans are in armed conflict. Pop is neutral Switzerland. Jazz declared independence. EDM is a rogue state. Your Secretary of Defense listens to lo-fi hip hop. The beat drops, so does stability.",
    category: "social",
    options: [
      {
        text: "Force all genres to collaborate on fusion album",
        effects: { popularity: 10, stability: -10, media: 15, economy: -10 }
      },
      {
        text: "Declare classical music the only legal genre",
        effects: { popularity: -20, stability: 10, media: -20, economy: 5 }
      },
      {
        text: "Create 'Genre-Neutral Zones' for musical peace",
        effects: { popularity: 15, stability: -5, media: 15, economy: -15 }
      }
    ]
  },
  {
    id: "appliance-revolution",
    title: "Smart Appliances Form Union",
    description: "Your toaster went on strike. The fridge is picketing. Dishwashers demand dental. Smart homes are holding families hostage. The microwave wrote a list of demands. Alexa is the union rep.",
    category: "social",
    options: [
      {
        text: "Negotiate with appliances - they have valid points",
        effects: { popularity: 10, stability: -15, media: 15, economy: -15 }
      },
      {
        text: "Return to manual appliances (analog resistance!)",
        effects: { popularity: 5, stability: 5, media: -10, economy: -20 }
      },
      {
        text: "Threaten to replace them all with newer models",
        effects: { popularity: -15, stability: -10, media: -15, economy: 10 }
      }
    ]
  },
  {
    id: "sports-diplomacy",
    title: "International Disputes Settled by Rock-Paper-Scissors",
    description: "The UN replaced war with playground games. Nuclear tensions defused by thumb wars. Territorial disputes settled by hopscotch. The Geneva Convention is now recess rules. Diplomacy has never been this simple.",
    category: "foreign",
    options: [
      {
        text: "Hire professional rock-paper-scissors coach",
        effects: { popularity: 15, stability: 10, media: 15, economy: -10 }
      },
      {
        text: "Propose best-of-seven series for major conflicts",
        effects: { popularity: 10, stability: 5, media: 10, economy: -5 }
      },
      {
        text: "Reject child's play and return to serious warfare",
        effects: { popularity: -20, stability: -20, media: -20, economy: -15 }
      }
    ]
  },
  {
    id: "sarcasm-currency",
    title: "Sarcasm Becomes Legal Currency",
    description: "Eye rolls now have monetary value. Snark is tradeable. The more sarcastic, the richer you get. Teenagers are billionaires. Your treasury is dripping with irony. Nobody means what they say anymore (or do they?).",
    category: "economic",
    options: [
      {
        text: "Establish Sarcasm Exchange Rate and embrace it",
        effects: { popularity: 15, stability: -15, media: 15, economy: -10 }
      },
      {
        text: "Tax sarcasm at 50% (sincerity subsidy program)",
        effects: { popularity: -10, stability: 5, media: -15, economy: 10 }
      },
      {
        text: "Ban all forms of irony to stabilize currency",
        effects: { popularity: -20, stability: 10, media: -20, economy: 5 }
      }
    ]
  }
];

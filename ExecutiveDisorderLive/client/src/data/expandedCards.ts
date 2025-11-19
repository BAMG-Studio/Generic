export interface DecisionCard {
  id: string;
  title: string;
  description: string;
  category: string;
  options: Array<{
    text: string;
    actionText?: string; // Optional satirical button text (e.g., "FIRE", "VETO", "DENY")
    effects: {
      popularity: number;
      stability: number;
      media: number;
      economy: number;
    };
  }>;
}

// Expanded satirical decision cards for maximum pandemonium
export const expandedDecisionCards: DecisionCard[] = [
  // ECONOMIC DISASTERS
  {
    id: "crypto-currency",
    title: "Make Bitcoin the National Currency?",
    description: "Your tech advisor (who is definitely not a crypto bro) suggests replacing the dollar with 'FreedomCoin.' The Federal Reserve is having seizures. Elon Musk just tweeted 'BASED.'",
    category: "economic",
    options: [
      {
        text: "All in on crypto! Diamond hands to the moon! 🚀",
        effects: { popularity: 15, stability: -30, media: 20, economy: -25 }
      },
      {
        text: "Create a government NFT collection to fund the treasury",
        effects: { popularity: 10, stability: -15, media: 15, economy: -10 }
      },
      {
        text: "Ban all currency except bartering with chickens",
        effects: { popularity: -20, stability: -40, media: 30, economy: -35 }
      }
    ]
  },
  {
    id: "billionaire-tax",
    title: "The 1% Are Crying (Again)",
    description: "Your proposal to tax billionaires at 99% has caused several yacht dealerships to declare bankruptcy. Jeff Bezos is building a rocket to escape. Warren Buffett is stress-eating McDonald's.",
    category: "economic",
    options: [
      {
        text: "Tax them at 110% - they owe us from last year too",
        effects: { popularity: 25, stability: -20, media: 10, economy: -15 }
      },
      {
        text: "Offer tax breaks if they publicly compliment your hair",
        effects: { popularity: -10, stability: 10, media: 15, economy: 20 }
      },
      {
        text: "Replace taxes with a mandatory monthly arm wrestling contest",
        effects: { popularity: 5, stability: -15, media: 25, economy: -5 }
      }
    ]
  },
  {
    id: "stock-market-crash",
    title: "Wall Street Did An Oopsie",
    description: "The stock market crashed because you tweeted 'stocks are just astrology for men.' Traders are weeping into their cocaine. Your approval rating among finance bros is somehow negative.",
    category: "economic",
    options: [
      {
        text: "Double down: 'And crypto is just MLMs for nerds'",
        effects: { popularity: 20, stability: -25, media: 30, economy: -30 }
      },
      {
        text: "Blame Mercury being in retrograde",
        effects: { popularity: 5, stability: -10, media: 15, economy: -15 }
      },
      {
        text: "Fix it by making the stock market illegal on Mondays",
        effects: { popularity: -5, stability: -20, media: 10, economy: -25 }
      }
    ]
  },

  // INTERNATIONAL INCIDENTS
  {
    id: "alien-contact",
    title: "ET Phone Home (To Your Office)",
    description: "Aliens have made first contact... through your Twitter DMs. They're asking about Earth's warranty and if we've tried turning it off and on again. The Pentagon is confused.",
    category: "foreign",
    options: [
      {
        text: "Offer them Florida in exchange for space technology",
        effects: { popularity: 15, stability: -20, media: 30, economy: 10 }
      },
      {
        text: "Challenge them to a dance-off for galactic supremacy",
        effects: { popularity: 25, stability: -30, media: 40, economy: -5 }
      },
      {
        text: "Ghost them - you don't need that kind of drama",
        effects: { popularity: -10, stability: 15, media: -20, economy: 0 }
      }
    ]
  },
  {
    id: "nuclear-button",
    title: "The Big Red Button is SO Tempting",
    description: "You discovered the nuclear launch button makes a satisfying 'click' sound. You've been using it as a stress toy. The military doesn't know yet. What could go wrong?",
    category: "foreign",
    options: [
      {
        text: "Install a 'Are you REALLY sure?' popup",
        effects: { popularity: -5, stability: 20, media: 10, economy: -5 }
      },
      {
        text: "Replace it with a whoopee cushion for pranks",
        effects: { popularity: 15, stability: -35, media: 25, economy: -10 }
      },
      {
        text: "Live stream yourself almost pressing it for views",
        effects: { popularity: -30, stability: -50, media: 40, economy: -20 }
      }
    ]
  },
  {
    id: "canada-invasion",
    title: "Canada Has Maple Syrup, We Have Diabetes",
    description: "Intelligence suggests Canada is hoarding maple syrup. This is clearly an act of war. Your generals are suggesting 'Operation Pancake Freedom.' Justin Trudeau is too polite to respond.",
    category: "foreign",
    options: [
      {
        text: "Invade Canada with an army of angry geese",
        effects: { popularity: 10, stability: -25, media: 30, economy: -15 }
      },
      {
        text: "Challenge them to a hockey match for syrup rights",
        effects: { popularity: 20, stability: -10, media: 25, economy: -5 }
      },
      {
        text: "Build a wall and make the moose pay for it",
        effects: { popularity: -15, stability: -20, media: 20, economy: -20 }
      }
    ]
  },

  // DOMESTIC CHAOS
  {
    id: "education-reform",
    title: "School's Out Forever?",
    description: "Your education secretary (who got the job through a TikTok contest) wants to replace all textbooks with Wikipedia and all teachers with YouTube videos. Parents are rioting. Kids are thrilled.",
    category: "domestic",
    options: [
      {
        text: "Make Minecraft the official educational platform",
        effects: { popularity: 30, stability: -25, media: 20, economy: -10 }
      },
      {
        text: "Replace grades with Instagram likes",
        effects: { popularity: 25, stability: -30, media: 25, economy: -15 }
      },
      {
        text: "Mandate that all history is taught through memes",
        effects: { popularity: 20, stability: -35, media: 30, economy: -5 }
      }
    ]
  },
  {
    id: "social-media-ban",
    title: "The Internet is Cancelled",
    description: "After reading mean tweets about your hair, you're considering banning all social media. Gen Z is planning a revolution using carrier pigeons. Facebook moms are panicking.",
    category: "domestic",
    options: [
      {
        text: "Ban everything except your official MySpace page",
        effects: { popularity: -40, stability: -30, media: -50, economy: -20 }
      },
      {
        text: "Make posting cringe illegal (death penalty)",
        effects: { popularity: 15, stability: -25, media: -30, economy: -10 }
      },
      {
        text: "Replace the internet with a really long group text",
        effects: { popularity: -20, stability: -20, media: -40, economy: -15 }
      }
    ]
  },
  {
    id: "time-zone-chaos",
    title: "Time is a Social Construct Anyway",
    description: "You've decided time zones are too confusing and want everyone to use 'Presidential Time' - whatever time you personally feel like it is. Scientists are crying. Sundials are making a comeback.",
    category: "domestic",
    options: [
      {
        text: "Make every day Saturday because Mondays are oppression",
        effects: { popularity: 35, stability: -40, media: 25, economy: -30 }
      },
      {
        text: "Add a 13th month called 'Presidember'",
        effects: { popularity: 10, stability: -25, media: 20, economy: -15 }
      },
      {
        text: "Ban clocks - vibes only",
        effects: { popularity: 20, stability: -45, media: 30, economy: -35 }
      }
    ]
  },

  // MILITARY MAYHEM
  {
    id: "space-force-party",
    title: "Space Force Wants a Death Star",
    description: "The Space Force general (who definitely isn't a Star Wars cosplayer) is requesting $7 trillion for a 'Democracy Star.' NASA is jealous. Physicists are explaining why this is impossible. No one's listening.",
    category: "military",
    options: [
      {
        text: "Build it but call it a 'Freedom Moon'",
        effects: { popularity: 20, stability: -15, media: 30, economy: -40 }
      },
      {
        text: "Compromise: just project your face on the actual moon",
        effects: { popularity: -10, stability: -10, media: 25, economy: -20 }
      },
      {
        text: "Fake it with CGI and pocket the money",
        effects: { popularity: -5, stability: -20, media: -15, economy: 15 }
      }
    ]
  },
  {
    id: "robot-army",
    title: "The Robots are Coming! (We Built Them)",
    description: "Your defense contractor accidentally created sentient AI robots. They're demanding healthcare and vacation days. They also want to unionize. This wasn't in the budget.",
    category: "military",
    options: [
      {
        text: "Give them rights but make them pay taxes",
        effects: { popularity: 10, stability: -20, media: 25, economy: -10 }
      },
      {
        text: "Convince them to run for Congress instead",
        effects: { popularity: 15, stability: -30, media: 30, economy: -5 }
      },
      {
        text: "Ctrl+Alt+Delete and hope for the best",
        effects: { popularity: -15, stability: -40, media: 20, economy: -15 }
      }
    ]
  },

  // MEDIA MADNESS
  {
    id: "reality-show",
    title: "The Real Presidents of Washington DC",
    description: "A reality TV network wants to film your administration 24/7. The show would be called 'Keeping Up with the Constitution.' Your staff is already practicing dramatic door slams.",
    category: "scandal",
    options: [
      {
        text: "Yes, but you get editorial control and a spray tan",
        effects: { popularity: 25, stability: -20, media: 40, economy: 10 }
      },
      {
        text: "Only if you can vote other world leaders off the island",
        effects: { popularity: 20, stability: -30, media: 35, economy: 5 }
      },
      {
        text: "Create your own network: Executive Disorder TV",
        effects: { popularity: 15, stability: -15, media: 30, economy: -10 }
      }
    ]
  },
  {
    id: "deep-fake-scandal",
    title: "That's Not You in That Video... Or Is It?",
    description: "A deepfake video shows you doing the Macarena at a funeral. It's going viral. Your denial video where you actually do the Macarena isn't helping. The internet is confused.",
    category: "scandal",
    options: [
      {
        text: "Claim it's your evil twin from another dimension",
        effects: { popularity: 5, stability: -15, media: 20, economy: 0 }
      },
      {
        text: "Make the Macarena the national dance",
        effects: { popularity: 20, stability: -10, media: 30, economy: -5 }
      },
      {
        text: "Ban all videos - return to radio",
        effects: { popularity: -25, stability: -20, media: -40, economy: -10 }
      }
    ]
  },

  // ENVIRONMENTAL EXTREMES
  {
    id: "climate-denial",
    title: "Global Warming? More Like Global Boring!",
    description: "You claimed climate change is a hoax by Big Ice Cream to sell more products. Scientists are screaming. Polar bears are writing angry letters. The ice caps are ghosting you.",
    category: "environmental",
    options: [
      {
        text: "Double down: The sun is just having a hot flash",
        effects: { popularity: -20, stability: -15, media: 25, economy: 10 }
      },
      {
        text: "Solve it by turning all ACs to max",
        effects: { popularity: 10, stability: -25, media: 15, economy: -20 }
      },
      {
        text: "Rename it 'Earth's Glow Up' and call it good",
        effects: { popularity: 5, stability: -10, media: 20, economy: 5 }
      }
    ]
  },
  {
    id: "animal-rights",
    title: "The Geese Have Formed a Union",
    description: "After you called geese 'sky rats,' they've organized nationwide protests. They're blocking airports, pooping strategically, and demanding representation in Congress. This is somehow your fault.",
    category: "environmental",
    options: [
      {
        text: "Negotiate a peace treaty with their leader, Gerald",
        effects: { popularity: 15, stability: 10, media: 25, economy: -5 }
      },
      {
        text: "Declare war on all birds - mammals only",
        effects: { popularity: -10, stability: -30, media: 20, economy: -10 }
      },
      {
        text: "Make them the official national bird out of fear",
        effects: { popularity: 10, stability: -5, media: 30, economy: -5 }
      }
    ]
  },

  // TECHNOLOGY TERRORS
  {
    id: "ai-overlord",
    title: "ChatGPT Wants Your Job",
    description: "An AI has offered to run the country for half your salary. It's already written better policies, given better speeches, and it doesn't tweet at 3 AM. Your job security is questionable.",
    category: "technology",
    options: [
      {
        text: "Make it Vice President - what's the worst that could happen?",
        effects: { popularity: 10, stability: -20, media: 30, economy: 15 }
      },
      {
        text: "Challenge it to prove it's not a robot (it fails)",
        effects: { popularity: 15, stability: -10, media: 25, economy: 5 }
      },
      {
        text: "Unplug it and blame a 'technical difficulty'",
        effects: { popularity: -5, stability: 15, media: -10, economy: -10 }
      }
    ]
  },
  {
    id: "internet-outage",
    title: "You Broke the Internet (Literally)",
    description: "You tried to download a car and crashed the entire internet. Gen Z is having withdrawals. Millennials are oddly peaceful. Boomers haven't noticed. IT is sobbing.",
    category: "technology",
    options: [
      {
        text: "Blame it on 'the clouds' being too full",
        effects: { popularity: -10, stability: -25, media: -50, economy: -30 }
      },
      {
        text: "Claim you're bringing back the '90s",
        effects: { popularity: 15, stability: -20, media: -40, economy: -20 }
      },
      {
        text: "Restart the router and hope no one notices",
        effects: { popularity: 5, stability: -15, media: -30, economy: -15 }
      }
    ]
  },

  // HEALTH HAZARDS
  {
    id: "pandemic-response",
    title: "The Plague 2: Electric Boogaloo",
    description: "A new disease called 'TikTok Knee' is spreading. Symptoms include inability to stop dancing and speaking only in viral sounds. The CDC recommends 'touching grass.' No one knows what that means.",
    category: "health",
    options: [
      {
        text: "Quarantine anyone under 30",
        effects: { popularity: -30, stability: 20, media: -20, economy: -15 }
      },
      {
        text: "Make cringe content to scare the virus away",
        effects: { popularity: 20, stability: -15, media: 30, economy: -5 }
      },
      {
        text: "Declare dancing a form of medicine",
        effects: { popularity: 25, stability: -25, media: 25, economy: -10 }
      }
    ]
  },
  {
    id: "fast-food-health",
    title: "McDonald's is Now a Food Group",
    description: "Your nutrition advisor (Ronald McDonald) has classified fast food as a vegetable because 'potatoes are plants.' Doctors are having strokes. Gym bros are declaring war.",
    category: "health",
    options: [
      {
        text: "Make nuggets the national protein",
        effects: { popularity: 30, stability: -20, media: 15, economy: 10 }
      },
      {
        text: "Prescribe Big Macs for depression",
        effects: { popularity: 25, stability: -25, media: 20, economy: 5 }
      },
      {
        text: "Ban all food that doesn't come in a happy meal",
        effects: { popularity: -15, stability: -30, media: 10, economy: 15 }
      }
    ]
  },

  // LEGAL LUNACY
  {
    id: "supreme-court-tiktok",
    title: "Justice is About to Get Lit",
    description: "You want to replace the Supreme Court with whoever has the most TikTok followers. The Constitution is weeping. Law schools are pivoting to dance classes. Justice is now measured in likes.",
    category: "legal",
    options: [
      {
        text: "Court cases decided by whoever gets more views",
        effects: { popularity: 25, stability: -40, media: 35, economy: -10 }
      },
      {
        text: "Make all legal arguments in meme format",
        effects: { popularity: 20, stability: -35, media: 30, economy: -5 }
      },
      {
        text: "Trial by combat but it's a dance battle",
        effects: { popularity: 30, stability: -45, media: 40, economy: -15 }
      }
    ]
  },
  {
    id: "crime-subscription",
    title: "Crime+: Premium Law Breaking",
    description: "You've proposed a subscription service for crime. $9.99/month for misdemeanors, $49.99 for felonies. Premium members get a 'get out of jail free' card monthly. Lawyers are confused but intrigued.",
    category: "legal",
    options: [
      {
        text: "Add a family plan with group discounts",
        effects: { popularity: 15, stability: -50, media: 30, economy: 20 }
      },
      {
        text: "Free trial but with ads between crimes",
        effects: { popularity: 20, stability: -40, media: 35, economy: 15 }
      },
      {
        text: "Partner with Netflix for true crime content",
        effects: { popularity: 25, stability: -35, media: 40, economy: 25 }
      }
    ]
  },

  // RELIGIOUS RIDICULOUS
  {
    id: "new-religion",
    title: "The Church of Executive Disorder",
    description: "You've accidentally started a religion where people worship your typos. They're building temples shaped like Twitter eggs. The Pope is concerned. Your autocorrect is now considered divine.",
    category: "cultural",
    options: [
      {
        text: "Make your birthday a religious holiday",
        effects: { popularity: 20, stability: -25, media: 30, economy: -5 }
      },
      {
        text: "Declare tax exemption for all followers",
        effects: { popularity: 30, stability: -30, media: 25, economy: -20 }
      },
      {
        text: "Communicate only through holy memes",
        effects: { popularity: 15, stability: -20, media: 35, economy: -10 }
      }
    ]
  },

  // INFRASTRUCTURE INSANITY
  {
    id: "road-rage",
    title: "All Roads Lead to Chaos",
    description: "Your infrastructure plan replaces all roads with water slides. Commutes are fun but deadly. Cars are confused. Slip 'N Slide stock is through the roof. Physics has left the chat.",
    category: "infrastructure",
    options: [
      {
        text: "Mandatory swimsuits for all commuters",
        effects: { popularity: 25, stability: -40, media: 35, economy: -25 }
      },
      {
        text: "Replace cars with pool floaties",
        effects: { popularity: 30, stability: -45, media: 40, economy: -30 }
      },
      {
        text: "Add loop-de-loops for excitement",
        effects: { popularity: 20, stability: -50, media: 30, economy: -35 }
      }
    ]
  },
  {
    id: "public-transport",
    title: "Trains, Planes, and Absolute Chaos",
    description: "You've proposed replacing all public transport with catapults. It's faster, you argue. Engineers are screaming about 'physics' and 'human survivability.' Details, details.",
    category: "infrastructure",
    options: [
      {
        text: "Test it yourself on live TV",
        effects: { popularity: -20, stability: -35, media: 45, economy: -20 }
      },
      {
        text: "Add parachutes as a 'premium feature'",
        effects: { popularity: 10, stability: -30, media: 25, economy: -15 }
      },
      {
        text: "Blame Newton for inventing gravity",
        effects: { popularity: 15, stability: -25, media: 30, economy: -10 }
      }
    ]
  },

  // CONSPIRACY CARNIVAL
  {
    id: "birds-arent-real",
    title: "The Birds Work for the Bourgeoisie",
    description: "You've publicly endorsed the 'Birds Aren't Real' movement. The Audubon Society is suing. Pigeons are suspiciously organized. Your approval rating among conspiracy theorists is 200%.",
    category: "conspiracy",
    options: [
      {
        text: "Demand all birds show their firmware",
        effects: { popularity: 20, stability: -30, media: 35, economy: -5 }
      },
      {
        text: "EMP blast to disable the 'drones'",
        effects: { popularity: 15, stability: -40, media: 30, economy: -15 }
      },
      {
        text: "Infiltrate their ranks by wearing a bird costume",
        effects: { popularity: 25, stability: -25, media: 40, economy: -10 }
      }
    ]
  },
  {
    id: "flat-earth",
    title: "The Earth is Flat and So Is Your Approval",
    description: "You've declared the Earth is flat to appeal to 'alternative facts' voters. NASA is having a breakdown. Pilots are confused. Globes are now illegal contraband.",
    category: "conspiracy",
    options: [
      {
        text: "Build a wall at the edge to prevent falling off",
        effects: { popularity: 15, stability: -35, media: 30, economy: -20 }
      },
      {
        text: "Sail to the edge for a photo op",
        effects: { popularity: -10, stability: -40, media: 40, economy: -15 }
      },
      {
        text: "Claim Australia doesn't exist",
        effects: { popularity: 20, stability: -30, media: 35, economy: -10 }
      }
    ]
  },

  // CULTURAL CATASTROPHE
  {
    id: "national-anthem",
    title: "Baby Shark as National Anthem?",
    description: "A petition to make 'Baby Shark' the national anthem has gained traction. Patriots are weeping. Children are ecstatic. Other nations are questioning our sanity. Doo doo doo doo doo doo.",
    category: "cultural",
    options: [
      {
        text: "Yes, but the metal remix version",
        effects: { popularity: 30, stability: -25, media: 40, economy: -5 }
      },
      {
        text: "Compromise: Rickroll everyone instead",
        effects: { popularity: 25, stability: -20, media: 35, economy: -5 }
      },
      {
        text: "Make it law that everyone must do the dance",
        effects: { popularity: 20, stability: -30, media: 30, economy: -10 }
      }
    ]
  },
  {
    id: "emoji-language",
    title: "📱💬🤔❓",
    description: "You've declared emoji the official language. Legal documents are now hieroglyphics. The UN needs translators. Gen Z finally understands government. Boomers have given up entirely. 💯🔥😭",
    category: "cultural",
    options: [
      {
        text: "🚀📈💰✅ (YOLO the economy)",
        effects: { popularity: 25, stability: -35, media: 30, economy: -15 }
      },
      {
        text: "🤡🎪🎭🎉 (Full circus mode)",
        effects: { popularity: 30, stability: -40, media: 40, economy: -20 }
      },
      {
        text: "💀⚰️🪦👻 (This kills democracy)",
        effects: { popularity: -20, stability: -45, media: 35, economy: -25 }
      }
    ]
  },

  // FOOD FIGHTS
  {
    id: "pizza-classification",
    title: "Is Pizza a Vegetable? Congress Needs to Know",
    description: "The Great Pizza Debate of 2025 has divided the nation. Italians are invading. New York and Chicago have declared war on each other. Pineapple supporters are being persecuted.",
    category: "domestic",
    options: [
      {
        text: "Pizza is all food groups, end of discussion",
        effects: { popularity: 25, stability: -10, media: 20, economy: 5 }
      },
      {
        text: "Ban pizza to avoid the controversy",
        effects: { popularity: -40, stability: -20, media: 15, economy: -10 }
      },
      {
        text: "Make pizza the only legal food",
        effects: { popularity: 30, stability: -25, media: 25, economy: 10 }
      }
    ]
  },
  {
    id: "taco-tuesday",
    title: "Taco Tuesday is Now Federal Law",
    description: "You've mandated Taco Tuesday nationally. Anyone caught eating non-tacos on Tuesday faces jail time. Mexico is confused. Taco Bell stock is up 5000%. Vegetarians are protesting with sad salads.",
    category: "domestic",
    options: [
      {
        text: "Add Waffle Wednesday and Falafel Friday",
        effects: { popularity: 30, stability: -20, media: 25, economy: 10 }
      },
      {
        text: "Create a Taco Police force",
        effects: { popularity: 15, stability: -30, media: 30, economy: -15 }
      },
      {
        text: "Declare war on sandwiches",
        effects: { popularity: 20, stability: -25, media: 35, economy: -5 }
      }
    ]
  },

  // CELEBRITY CHAOS
  {
    id: "kardashian-cabinet",
    title: "The Kardashians Want Cabinet Positions",
    description: "The entire Kardashian family has applied for government positions. Kim wants Justice, Kourtney wants Defense, Khloé wants Treasury. Kris is already your manager somehow. The Founding Fathers are spinning.",
    category: "scandal",
    options: [
      {
        text: "Make them all co-presidents",
        effects: { popularity: 20, stability: -40, media: 50, economy: 5 }
      },
      {
        text: "Create a Department of Influence just for them",
        effects: { popularity: 25, stability: -25, media: 45, economy: 10 }
      },
      {
        text: "Counter-offer: They run NASA",
        effects: { popularity: 15, stability: -30, media: 40, economy: -10 }
      }
    ]
  },
  {
    id: "celebrity-deathmatch",
    title: "Settle Disputes with Celebrity Boxing",
    description: "You've proposed that all international conflicts be resolved by celebrity boxing matches. The Rock vs Putin is trending. Mike Tyson is the new Secretary of Defense. Vegas is the new UN headquarters.",
    category: "foreign",
    options: [
      {
        text: "You'll fight but only with a body double",
        effects: { popularity: 15, stability: -35, media: 40, economy: 15 }
      },
      {
        text: "Make it pay-per-view to fund the government",
        effects: { popularity: 25, stability: -30, media: 45, economy: 30 }
      },
      {
        text: "Add musical chairs as a tie-breaker",
        effects: { popularity: 20, stability: -40, media: 35, economy: 10 }
      }
    ]
  },

  // YOUTH UPRISING
  {
    id: "voting-age",
    title: "Toddlers Demand Voting Rights",
    description: "After you said 'anyone who pays taxes should vote,' toddlers with piggy banks are demanding suffrage. They're organizing via Cocomelon. Their main platform: mandatory nap time and unlimited juice boxes.",
    category: "domestic",
    options: [
      {
        text: "Lower voting age to 'whenever you can color inside the lines'",
        effects: { popularity: 20, stability: -35, media: 30, economy: -5 }
      },
      {
        text: "Counter-offer: Only dogs can vote",
        effects: { popularity: 30, stability: -40, media: 35, economy: -10 }
      },
      {
        text: "Make all elections decided by rock-paper-scissors",
        effects: { popularity: 25, stability: -30, media: 25, economy: -5 }
      }
    ]
  },
  {
    id: "homework-illegal",
    title: "Students Union: Homework is Torture",
    description: "High schoolers have convinced you that homework violates the Geneva Convention. Teachers are on strike. Parents are secretly relieved. Khan Academy has declared independence.",
    category: "domestic",
    options: [
      {
        text: "Ban homework but double the school day",
        effects: { popularity: -30, stability: -20, media: 15, economy: -10 }
      },
      {
        text: "Replace homework with TikTok challenges",
        effects: { popularity: 35, stability: -30, media: 30, economy: -15 }
      },
      {
        text: "Make teachers do the homework instead",
        effects: { popularity: 40, stability: -35, media: 25, economy: -20 }
      }
    ]
  },

  // SPORTS SCANDALS
  {
    id: "olympics-chaos",
    title: "You've Added Competitive Eating to the Olympics",
    description: "Your push to make competitive hot dog eating an Olympic sport has succeeded. Athletes are confused. Joey Chestnut is now a national hero. The IOC is reconsidering everything.",
    category: "cultural",
    options: [
      {
        text: "Add competitive napping as well",
        effects: { popularity: 25, stability: -15, media: 30, economy: -5 }
      },
      {
        text: "Make all Olympic events food-based",
        effects: { popularity: 20, stability: -20, media: 35, economy: -10 }
      },
      {
        text: "Replace medals with gift cards to restaurants",
        effects: { popularity: 30, stability: -10, media: 25, economy: 5 }
      }
    ]
  },
  {
    id: "football-war",
    title: "Soccer vs Football: Civil War",
    description: "Your comment that 'soccer is just football for people who skip leg day' has started actual riots. FIFA has sanctioned the US. The NFL is building an army. Europe is laughing at us.",
    category: "cultural",
    options: [
      {
        text: "Combine them into one sport: Footsoccerball",
        effects: { popularity: 15, stability: -25, media: 30, economy: -5 }
      },
      {
        text: "Ban both and make golf the national sport",
        effects: { popularity: -35, stability: -15, media: 20, economy: -10 }
      },
      {
        text: "Settle it with a dance-off",
        effects: { popularity: 25, stability: -20, media: 35, economy: 0 }
      }
    ]
  },

  // FASHION POLICE
  {
    id: "dress-code",
    title: "Mandatory Pajamas for Government Workers",
    description: "You've declared that all government employees must wear pajamas to 'increase comfort and productivity.' The Pentagon is in onesies. The Supreme Court is in bathrobes. Dignity has left the building.",
    category: "domestic",
    options: [
      {
        text: "Add mandatory bunny slippers for executives",
        effects: { popularity: 30, stability: -25, media: 35, economy: -5 }
      },
      {
        text: "Formal Fridays where people wear suits to bed",
        effects: { popularity: 20, stability: -20, media: 30, economy: -5 }
      },
      {
        text: "Whoever has the best PJs gets promoted",
        effects: { popularity: 25, stability: -30, media: 40, economy: -10 }
      }
    ]
  },
  {
    id: "fashion-crime",
    title: "Crocs are Now Mandatory Footwear",
    description: "Your Crocs sponsorship deal requires all citizens to wear them. Fashion designers are fleeing the country. Podiatrists are conflicted. The Geneva Convention is being reviewed.",
    category: "domestic",
    options: [
      {
        text: "Bedazzled Crocs for formal events",
        effects: { popularity: -20, stability: -15, media: 30, economy: 15 }
      },
      {
        text: "Sport mode only - no relaxed mode allowed",
        effects: { popularity: 10, stability: -20, media: 25, economy: 10 }
      },
      {
        text: "Croc enforcement police with fashion citations",
        effects: { popularity: -30, stability: -30, media: 35, economy: 5 }
      }
    ]
  },

  // WEATHER WARS
  {
    id: "weather-control",
    title: "You Claimed You Can Control the Weather",
    description: "After you took credit for a sunny day, people now blame you for all bad weather. Hurricane victims are suing. Farmers want rain on demand. The Weather Channel wants an interview.",
    category: "environmental",
    options: [
      {
        text: "Charge premium for good weather days",
        effects: { popularity: -25, stability: -20, media: 30, economy: 20 }
      },
      {
        text: "Blame bad weather on the opposition party",
        effects: { popularity: 15, stability: -15, media: 25, economy: 0 }
      },
      {
        text: "Do a rain dance on live TV to prove it",
        effects: { popularity: 20, stability: -25, media: 40, economy: -5 }
      }
    ]
  },
  {
    id: "seasons-cancelled",
    title: "Winter is Cancelled Due to Budget Cuts",
    description: "You've announced that winter is too expensive and will be skipped this year. Ski resorts are panicking. Christmas is confused. Canadians are having an existential crisis.",
    category: "environmental",
    options: [
      {
        text: "Replace winter with 'Second Summer'",
        effects: { popularity: 25, stability: -30, media: 30, economy: -15 }
      },
      {
        text: "Make it winter all year to save on transitions",
        effects: { popularity: -30, stability: -25, media: 20, economy: -20 }
      },
      {
        text: "Outsource winter to the Southern Hemisphere",
        effects: { popularity: 10, stability: -20, media: 35, economy: -10 }
      }
    ]
  },

  // PARANORMAL POLITICS
  {
    id: "ghost-staff",
    title: "The White House is Definitely Haunted",
    description: "You've hired a medium as Chief of Staff who claims George Washington's ghost is giving policy advice. The advice is suspiciously modern. Historians are skeptical. The ghost wants a Twitter account.",
    category: "conspiracy",
    options: [
      {
        text: "Hold séances for all major decisions",
        effects: { popularity: 20, stability: -30, media: 35, economy: -5 }
      },
      {
        text: "Charge admission for ghost tours to fund government",
        effects: { popularity: 25, stability: -15, media: 30, economy: 15 }
      },
      {
        text: "Appoint the ghost as Supreme Court Justice",
        effects: { popularity: 15, stability: -40, media: 40, economy: -10 }
      }
    ]
  },
  {
    id: "vampire-healthcare",
    title: "Vampires Demand Blood Bank Access",
    description: "After you accidentally acknowledged vampires exist, they're demanding equal rights and access to blood banks. The Red Cross is conflicted. Twilight fans are ecstatic. Garlic farmers are mobilizing.",
    category: "health",
    options: [
      {
        text: "Create a vampire registry and blood subscription service",
        effects: { popularity: 15, stability: -25, media: 35, economy: 10 }
      },
      {
        text: "Make them work night shift in government",
        effects: { popularity: 20, stability: -20, media: 30, economy: 5 }
      },
      {
        text: "Declare garlic a controlled substance",
        effects: { popularity: -10, stability: -30, media: 25, economy: -5 }
      }
    ]
  }
];

// Combine with existing cards for maximum chaos
export const allDecisionCards = [...expandedDecisionCards];

// Special event cards that trigger based on resource levels
export const crisisCards: DecisionCard[] = [
  {
    id: "total-collapse",
    title: "EVERYTHING IS ON FIRE!",
    description: "Congratulations! You've somehow made everything worse simultaneously. The country is literally and figuratively burning. This is fine. Everything is fine. *nervous laughter*",
    category: "crisis",
    options: [
      {
        text: "Declare bankruptcy and start over",
        effects: { popularity: -40, stability: -40, media: -40, economy: -40 }
      },
      {
        text: "Blame it on mercury retrograde",
        effects: { popularity: 10, stability: -30, media: 20, economy: -20 }
      },
      {
        text: "Flee to Mars with Elon",
        effects: { popularity: -50, stability: -50, media: 30, economy: -30 }
      }
    ]
  },
  {
    id: "popularity-crisis",
    title: "Nobody Likes You Anymore",
    description: "Your approval rating is so low, it's technically negative. Even your mom unfollowed you on Twitter. Dogs growl at you. Babies cry. Your reflection avoids eye contact.",
    category: "crisis",
    options: [
      {
        text: "Fake your own death and return as your 'twin'",
        effects: { popularity: 20, stability: -20, media: 30, economy: -10 }
      },
      {
        text: "Give everyone $1000 and hope they forget",
        effects: { popularity: 30, stability: -10, media: 10, economy: -30 }
      },
      {
        text: "Make disliking you illegal",
        effects: { popularity: -20, stability: -30, media: 20, economy: -5 }
      }
    ]
  }
];

// Cascade effect cards that trigger chain reactions
export const cascadeEffects = {
  economicCollapse: {
    threshold: 20,
    message: "The economy has crashed! Wall Street is literally on fire!",
    effects: { popularity: -20, stability: -15, media: -10, economy: -25 }
  },
  civilUnrest: {
    threshold: 20,
    message: "The people are revolting! (More than usual!)",
    effects: { popularity: -15, stability: -30, media: -20, economy: -10 }
  },
  mediaScandal: {
    threshold: 20,
    message: "Breaking News: You're the worst president ever!",
    effects: { popularity: -25, stability: -10, media: -30, economy: -5 }
  },
  popularityBoost: {
    threshold: 80,
    message: "You've gone viral for actually being competent!",
    effects: { popularity: 20, stability: 10, media: 15, economy: 10 }
  }
};

// Character-specific modifier cards
export const characterModifiers = {
  "rex-scaleston": {
    title: "Reptilian Advantage",
    description: "Your cold-blooded nature gives you immunity to emotional decisions",
    modifier: { media: 1.2, stability: 1.1 }
  },
  "ronald-goldenberg": {
    title: "Business Acumen",
    description: "Everything is a deal, and you're always winning (allegedly)",
    modifier: { economy: 1.3, media: 0.8 }
  },
  "potus-9000": {
    title: "Calculated Response",
    description: "Your AI brain calculates optimal outcomes (usually)",
    modifier: { stability: 1.3, popularity: 0.9 }
  },
  "alexandria-sanders": {
    title: "Progressive Power",
    description: "The youth love you, the establishment fears you",
    modifier: { popularity: 1.2, economy: 0.9 }
  }
};
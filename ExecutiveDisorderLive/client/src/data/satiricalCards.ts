import type { DecisionCard } from "./cards";

// 40 Premium Satirical Decision Cards with Context-Specific Action Buttons
// These supplement the 185 Dropbox cards for total 225+ card collection

export const satiricalCards: DecisionCard[] = [
  // ECONOMIC
  {
    id: "national-debt-delete",
    title: "Entire National Debt Accidentally Deleted",
    description: "An intern pressed the wrong button. The national debt is gone. Creditors are furious. Economists are in shock. Other nations want the same intern. Financial reality has no meaning anymore.",
    category: "economic",
    options: [
      { text: "Pretend it never existed and change your number", actionText: "DENY IT", effects: { popularity: 20, stability: -30, media: -15, economy: 15 } },
      { text: "Offer IOUs and promise to pay back eventually", actionText: "DELAY", effects: { popularity: -10, stability: 5, media: -10, economy: 5 } },
      { text: "Blame a computer virus and hire that intern as CFO", actionText: "PROMOTE", effects: { popularity: 15, stability: -20, media: 20, economy: -15 } }
    ]
  },
  {
    id: "gdp-memes",
    title: "Measure GDP in Memes Per Capita",
    description: "Economic growth is now viral content output. The Fed tracks dank meme production. Recession is 'stale content quarter.' Your economists are influencers.",
    category: "economic",
    options: [
      { text: "Subsidize meme creators as essential workers", actionText: "SUBSIDIZE", effects: { popularity: 30, stability: -25, media: 45, economy: -20 } },
      { text: "Tax cringe content at 90% to boost quality", actionText: "TAX CRINGE", effects: { popularity: 25, stability: -20, media: 40, economy: -15 } },
      { text: "Replace Federal Reserve with Meme Review Committee", actionText: "MEME FED", effects: { popularity: 35, stability: -30, media: 50, economy: -25 } }
    ]
  },
  {
    id: "bitcoin-only",
    title: "Make Bitcoin the ONLY Legal Tender",
    description: "Fiat currency is cancelled. Grandma's savings are gone. Gas stations need blockchain tutorials. Your treasury is a hardware wallet. Volatility is policy.",
    category: "economic",
    options: [
      { text: "Force all seniors to learn blockchain", actionText: "TEACH GRANDMA", effects: { popularity: -20, stability: -35, media: 30, economy: -30 } },
      { text: "Mine Bitcoin using government electricity", actionText: "MINE IT", effects: { popularity: 15, stability: -25, media: 35, economy: -35 } },
      { text: "Declare 'paper money is FUD' by executive order", actionText: "PAPER IS FUD", effects: { popularity: 10, stability: -30, media: 40, economy: -40 } }
    ]
  },
  {
    id: "tax-billionaires-110",
    title: "Tax Billionaires 110% (Math Not Required)",
    description: "Your progressive wing demands taxing the rich more than they earn. Calculators are broken. Excel crashed. Billionaires are fleeing to Mars.",
    category: "economic",
    options: [
      { text: "Do it anyway and call it 'creative accounting'", actionText: "TAX THEM", effects: { popularity: 30, stability: -25, media: 15, economy: -30 } },
      { text: "Tax their vibes instead of their income", actionText: "VIBE TAX", effects: { popularity: 15, stability: -10, media: 25, economy: -5 } },
      { text: "Make billionaires pay in interpretive dance", actionText: "DANCE TAX", effects: { popularity: 20, stability: -15, media: 35, economy: -10 } }
    ]
  },
  {
    id: "print-money-unlimited",
    title: "Money Printer Go BRRRRR Forever",
    description: "You've discovered unlimited money printing. Zimbabwe is laughing. Venezuela sent sympathy. The dollar is worth less than Monopoly money.",
    category: "economic",
    options: [
      { text: "Print until the printers catch fire", actionText: "PRINT MORE", effects: { popularity: 20, stability: -35, media: -15, economy: -40 } },
      { text: "Replace currency with literal vibes", actionText: "VIBE ECONOMY", effects: { popularity: 15, stability: -25, media: 25, economy: -30 } },
      { text: "Blame inflation on 'market manipulation by reality'", actionText: "BLAME REALITY", effects: { popularity: -5, stability: -30, media: 20, economy: -35 } }
    ]
  },
  {
    id: "universal-yacht",
    title: "Universal Luxury Income - Everyone Gets a Yacht",
    description: "Free yachts for everyone! The coast guard is overwhelmed. Yacht parking is impossible. The ocean is 80% yacht. Naval traffic is gridlocked.",
    category: "economic",
    options: [
      { text: "Mandate yacht ownership for citizenship", actionText: "YACHT LAW", effects: { popularity: 30, stability: -30, media: 25, economy: -45 } },
      { text: "Compromise: Everyone gets a dingy with delusions", actionText: "DINGY PLAN", effects: { popularity: 10, stability: -15, media: 15, economy: -20 } },
      { text: "Build parking lots in the ocean", actionText: "OCEAN LOTS", effects: { popularity: 5, stability: -20, media: 20, economy: -25 } }
    ]
  },
  {
    id: "nft-treasury",
    title: "Fund Government with NFTs",
    description: "Your crypto bro advisor suggests minting government bonds as NFTs. The blockchain is confused. The treasury is a Discord server. Screenshotters are criminals.",
    category: "economic",
    options: [
      { text: "Screenshot the Declaration of Independence", actionText: "MINT IT", effects: { popularity: 15, stability: -25, media: 20, economy: -20 } },
      { text: "Create 'Presidential Rare Pepes' collection", actionText: "PEPE IT", effects: { popularity: 20, stability: -20, media: 30, economy: -15 } },
      { text: "Jail everyone who knows what NFTs are", actionText: "ARREST CRYPTO", effects: { popularity: 10, stability: 5, media: -15, economy: 10 } }
    ]
  },
  {
    id: "gold-standard-literal",
    title: "Return to Gold Standard (Literally Golden)",
    description: "Currency is actual gold coins. Wallets weigh 40 pounds. Vending machines are broken. Banks are medieval vaults. Your economic advisor is a dragon.",
    category: "economic",
    options: [
      { text: "Require all citizens to carry treasure chests", actionText: "MANDATE CHESTS", effects: { popularity: 20, stability: -30, media: 40, economy: -35 } },
      { text: "Hire pirates to guard the Federal Reserve", actionText: "PIRATE GUARDS", effects: { popularity: 25, stability: -25, media: 45, economy: -20 } },
      { text: "Make dragons legal tender custodians", actionText: "DRAGON ECONOMY", effects: { popularity: 35, stability: -35, media: 50, economy: -30 } }
    ]
  },

  // FOREIGN POLICY
  {
    id: "un-comedy-club",
    title: "Turn UN General Assembly into Comedy Club",
    description: "World leaders must roast each other for diplomacy. France brought a ventriloquist. Russia's set bombed. The Security Council is a heckler's paradise.",
    category: "foreign",
    options: [
      { text: "Institute mandatory stand-up training for diplomats", actionText: "COMEDY LAW", effects: { popularity: 25, stability: -15, media: 35, economy: -10 } },
      { text: "Declare war on countries with bad comedic timing", actionText: "DECLARE WAR", effects: { popularity: 15, stability: -25, media: 20, economy: -20 } },
      { text: "Resolve all conflicts via rap battles", actionText: "RAP BATTLE", effects: { popularity: 30, stability: -20, media: 40, economy: -5 } }
    ]
  },
  {
    id: "diplomatic-cats",
    title: "Grant Diplomatic Immunity to All Cats",
    description: "Your cat-obsessed aide wrote this into law. All felines are diplomats. International cat incidents cause crises. Meow means 'no comment.'",
    category: "foreign",
    options: [
      { text: "Double down! Cats run foreign policy now", actionText: "PURR DIPLOMACY", effects: { popularity: 25, stability: -30, media: 35, economy: -15 } },
      { text: "Create Department of Feline Affairs", actionText: "CAT DEPT", effects: { popularity: 20, stability: -20, media: 30, economy: -10 } },
      { text: "Declare all dogs are spies and must be deported", actionText: "DEPORT DOGS", effects: { popularity: -15, stability: -25, media: 25, economy: -5 } }
    ]
  },
  {
    id: "space-force-reality",
    title: "Space Force Reality Show",
    description: "Military satellites film reality TV. Astronauts compete for roses. Aliens are judging. The Pentagon is a production studio. National security is sponsored by Mountain Dew.",
    category: "foreign",
    options: [
      { text: "Weaponize the drama for strategic advantage", actionText: "WEAPONIZE", effects: { popularity: 20, stability: -25, media: 40, economy: 15 } },
      { text: "Invite enemy nations to compete for peace", actionText: "INVITE ENEMIES", effects: { popularity: 15, stability: -15, media: 30, economy: -10 } },
      { text: "Replace all military operations with plot twists", actionText: "PLOT TWIST", effects: { popularity: 25, stability: -30, media: 45, economy: -5 } }
    ]
  },
  {
    id: "world-leader-hunger-games",
    title: "Propose World Leader Hunger Games",
    description: "Leaders fight to death on TV instead of war. Putin brought a bear. Macron has a baguette sword. The Queen sent a corgi. May the odds be ever in your favor.",
    category: "foreign",
    options: [
      { text: "Volunteer as tribute with a foam finger", actionText: "VOLUNTEER", effects: { popularity: 30, stability: -35, media: 50, economy: -20 } },
      { text: "Rig the games in your favor with drones", actionText: "RIG IT", effects: { popularity: 10, stability: -25, media: 15, economy: -15 } },
      { text: "Replace violence with competitive cooking", actionText: "COOK OFF", effects: { popularity: 25, stability: -10, media: 35, economy: 5 } }
    ]
  },
  {
    id: "nato-gaming",
    title: "Turn NATO into Multiplayer Gaming Alliance",
    description: "Military strategy is Fortnite tournaments. Article 5 triggered by killsteals. Russia banned for camping. Nuclear codes are Twitch passwords.",
    category: "foreign",
    options: [
      { text: "Make K/D ratio the primary military metric", actionText: "K/D METRIC", effects: { popularity: 20, stability: -25, media: 35, economy: -10 } },
      { text: "Declare war on lag and bad ping", actionText: "WAR ON LAG", effects: { popularity: 25, stability: -20, media: 30, economy: -15 } },
      { text: "Replace tanks with gaming chairs", actionText: "GAMER TANKS", effects: { popularity: 30, stability: -30, media: 40, economy: -5 } }
    ]
  },
  {
    id: "aliens-disappointed",
    title: "Aliens Arrived... They're Disappointed",
    description: "First contact happened. They watched our TikToks and want to leave. Earth is in galactic timeout. We're the embarrassing cousins of the universe.",
    category: "foreign",
    options: [
      { text: "Challenge them to a meme battle for redemption", actionText: "MEME WAR", effects: { popularity: 25, stability: -20, media: 40, economy: -15 } },
      { text: "Blame all human problems on Mercury retrograde", actionText: "BLAME MERCURY", effects: { popularity: 15, stability: -15, media: 25, economy: -10 } },
      { text: "Offer them Earth's Worst Reality Show collection", actionText: "OFFER SHOWS", effects: { popularity: 10, stability: -25, media: 35, economy: -5 } }
    ]
  },
  {
    id: "declare-war-ocean",
    title: "Declare War on the Ocean",
    description: "The sea has been passive-aggressive. Hurricanes are acts of war. Tsunamis are terrorism. Poseidon has not responded to cables. Fish are enemy combatants.",
    category: "foreign",
    options: [
      { text: "Launch nuclear strikes on Hurricane Season", actionText: "NUKE IT", effects: { popularity: -20, stability: -40, media: 30, economy: -35 } },
      { text: "Negotiate peace treaty with Aquaman", actionText: "AQUAMAN DEAL", effects: { popularity: 15, stability: -25, media: 40, economy: -10 } },
      { text: "Build a wall around the entire coastline", actionText: "OCEAN WALL", effects: { popularity: 10, stability: -30, media: 25, economy: -40 } }
    ]
  },
  {
    id: "trade-war-memes",
    title: "Start Trade War Using Only Memes",
    description: "Tariffs are last century. You're attacking China with Rickrolls. They counter with TikTok dances. The WTO has no jurisdiction over shitposts.",
    category: "foreign",
    options: [
      { text: "Deploy the Strategic Meme Reserve", actionText: "DEPLOY MEMES", effects: { popularity: 30, stability: -20, media: 45, economy: -15 } },
      { text: "Sanction nations with cringe humor", actionText: "CRINGE SANCTIONS", effects: { popularity: 20, stability: -15, media: 35, economy: -10 } },
      { text: "Create Department of Viral Warfare", actionText: "VIRAL DEPT", effects: { popularity: 25, stability: -25, media: 40, economy: -20 } }
    ]
  },

  // DOMESTIC POLICY
  {
    id: "congress-battle-royale",
    title: "Turn Congress into Battle Royale Arena",
    description: "Legislation determined by last legislator standing. Filibusters are boss fights. The Senate has loot drops. C-SPAN is pay-per-view. Democracy has respawn points.",
    category: "domestic",
    options: [
      { text: "Equip all senators with foam weapons", actionText: "ARM THEM", effects: { popularity: 30, stability: -25, media: 50, economy: -10 } },
      { text: "Install victory royale music for passed bills", actionText: "VICTORY MUSIC", effects: { popularity: 25, stability: -20, media: 40, economy: -5 } },
      { text: "Ban healing items to speed up legislation", actionText: "NO HEALING", effects: { popularity: 20, stability: -30, media: 35, economy: -15 } }
    ]
  },
  {
    id: "supreme-court-reality",
    title: "Supreme Court is Now a Reality Show",
    description: "Justice determined by audience votes. Rulings require confessionals. The gavel has dramatic sound effects. Judge Judy is Chief Justice. Precedent is Twitter trends.",
    category: "domestic",
    options: [
      { text: "Install voting kiosks in the courtroom", actionText: "VOTE JUSTICE", effects: { popularity: 25, stability: -35, media: 55, economy: -15 } },
      { text: "Replace robes with evening gowns", actionText: "GOWN UP", effects: { popularity: 20, stability: -25, media: 40, economy: -5 } },
      { text: "Eliminate immunity but add commercial breaks", actionText: "ADD ADS", effects: { popularity: 15, stability: -30, media: 45, economy: 20 } }
    ]
  },
  {
    id: "voting-via-memes",
    title: "Replace Elections with Meme Competitions",
    description: "Democracy is now upvotes. Debates are roast battles. Campaign ads are shitposts. Boomers are disenfranchised. Gen Z controls everything.",
    category: "domestic",
    options: [
      { text: "Make reposting without credit a felony", actionText: "CREDIT LAW", effects: { popularity: 30, stability: -25, media: 40, economy: -10 } },
      { text: "Declare cringe memes as voter suppression", actionText: "BAN CRINGE", effects: { popularity: 25, stability: -20, media: 35, economy: -15 } },
      { text: "Require all laws explained in meme format", actionText: "MEME LAWS", effects: { popularity: 35, stability: -30, media: 50, economy: -5 } }
    ]
  },
  {
    id: "rename-everything-freedom",
    title: "Rename Everything 'Freedom'",
    description: "Freedom fries are back! Freedom toast. Freedom kissing. France is furious. Linguists are on strike. The dictionary filed a lawsuit.",
    category: "domestic",
    options: [
      { text: "Legally require 'Freedom' in all product names", actionText: "MANDATE IT", effects: { popularity: 20, stability: -20, media: 30, economy: -15 } },
      { text: "Rename France to 'That Country We Don't Talk About'", actionText: "RENAME FRANCE", effects: { popularity: 15, stability: -25, media: 35, economy: -20 } },
      { text: "Ban the concept of synonyms to reduce confusion", actionText: "BAN SYNONYMS", effects: { popularity: 10, stability: -30, media: 25, economy: -10 } }
    ]
  },
  {
    id: "mandatory-nap",
    title: "Mandatory National Nap Time at 2pm",
    description: "Everyone must nap at 2pm daily. Businesses shut down. Traffic stops. Night shift workers are confused. Insomniacs are criminals.",
    category: "domestic",
    options: [
      { text: "Install nap pods in every building", actionText: "INSTALL PODS", effects: { popularity: 30, stability: -15, media: 25, economy: -25 } },
      { text: "Punish nap-skippers with bedtime stories", actionText: "BEDTIME STORIES", effects: { popularity: 20, stability: -20, media: 35, economy: -15 } },
      { text: "Declare being awake at 2pm is treason", actionText: "NAP OR DIE", effects: { popularity: 15, stability: -35, media: 40, economy: -30 } }
    ]
  },
  {
    id: "constitution-emoji",
    title: "Add Emojis to the Constitution",
    description: "Make the Constitution 'accessible' with emojis. 🦅 = Freedom. ⚖️ = Justice. The Founding Fathers are spinning. Gen Z finally understands their rights.",
    category: "domestic",
    options: [
      { text: "Replace all legal text with emoji-only version", actionText: "FULL EMOJI", effects: { popularity: 25, stability: -30, media: 45, economy: -20 } },
      { text: "Require lawyers to argue cases in emojis", actionText: "EMOJI COURT", effects: { popularity: 30, stability: -25, media: 50, economy: -15 } },
      { text: "Ban anyone over 40 from understanding Constitution", actionText: "AGE BAN", effects: { popularity: 20, stability: -35, media: 40, economy: -25 } }
    ]
  },
  {
    id: "government-vibes",
    title: "Government Runs Entirely on Vibes Now",
    description: "Policies based on 'the vibe.' No data. No experts. Just vibes. Your vibe coordinator runs everything. The CBO has an existential crisis. Math is cancelled.",
    category: "domestic",
    options: [
      { text: "Appoint a Chief Vibe Officer with cabinet rank", actionText: "HIRE CVO", effects: { popularity: 25, stability: -30, media: 40, economy: -25 } },
      { text: "Arrest anyone with bad vibes for terrorism", actionText: "VIBE POLICE", effects: { popularity: 15, stability: -35, media: 30, economy: -20 } },
      { text: "Replace all statistics with mood rings", actionText: "MOOD RINGS", effects: { popularity: 20, stability: -25, media: 35, economy: -30 } }
    ]
  },
  {
    id: "illegal-boring",
    title: "Make Being Boring Illegal",
    description: "Your entertainment czar criminalizes boredom. Accountants are panicking. Libraries under siege. DMV workers face life sentences. Interesting is mandatory.",
    category: "domestic",
    options: [
      { text: "Establish Excitement Quotas for all citizens", actionText: "QUOTA LAW", effects: { popularity: 20, stability: -30, media: 45, economy: -20 } },
      { text: "Require all jobs to include juggling", actionText: "JUGGLE MANDATE", effects: { popularity: 25, stability: -25, media: 40, economy: -25 } },
      { text: "Replace prisons with improv comedy camps", actionText: "IMPROV PRISON", effects: { popularity: 30, stability: -20, media: 50, economy: -15 } }
    ]
  },

  // SOCIAL POLICY
  {
    id: "tiktok-citizenship",
    title: "TikTok Required for Citizenship",
    description: "All citizens must post daily TikToks. Boomers being deported. Gen Alpha runs government. Cringe content is grounds for impeachment. Dance challenges are civics.",
    category: "social",
    options: [
      { text: "Deport anyone with under 100 followers", actionText: "FOLLOWER PURGE", effects: { popularity: 20, stability: -30, media: 40, economy: -15 } },
      { text: "Make viral videos requirement for voting rights", actionText: "VIRAL VOTING", effects: { popularity: 25, stability: -35, media: 45, economy: -20 } },
      { text: "Replace social security numbers with TikTok handles", actionText: "HANDLE SSN", effects: { popularity: 30, stability: -25, media: 50, economy: -10 } }
    ]
  },
  {
    id: "culture-war-olympics",
    title: "Settle Culture Wars with Olympic Events",
    description: "Left vs Right synchronized swimming. Pronouns vs Tradition javelin. Your referee is confused. Gold medals solve nothing. Political discourse is athletic.",
    category: "social",
    options: [
      { text: "Make political debates into dance-offs", actionText: "DANCE DEBATE", effects: { popularity: 30, stability: -20, media: 45, economy: -5 } },
      { text: "Award policy wins based on who cries less", actionText: "NO CRYING", effects: { popularity: 20, stability: -25, media: 35, economy: -10 } },
      { text: "Replace Congress with competitive gymnastics", actionText: "GYMNAST CONGRESS", effects: { popularity: 25, stability: -30, media: 50, economy: -15 } }
    ]
  },
  {
    id: "social-credit-memes",
    title: "Social Credit Based on Meme Quality",
    description: "China called, they want their system back. But yours is worse - based on meme quality. Bad memes = punishment. The Dank Meme Bureau has too much power.",
    category: "social",
    options: [
      { text: "Create Guantanamo Bay for cringe posters", actionText: "CRINGE GULAG", effects: { popularity: 15, stability: -35, media: 40, economy: -20 } },
      { text: "Award citizenship bonuses for viral content", actionText: "VIRAL REWARDS", effects: { popularity: 25, stability: -25, media: 45, economy: -15 } },
      { text: "Ban all humor and live in humorless dystopia", actionText: "BAN HUMOR", effects: { popularity: -30, stability: -40, media: 30, economy: -25 } }
    ]
  },
  {
    id: "pronoun-badges",
    title: "Mandatory Pronoun Badges Like Name Tags",
    description: "Everyone must wear pronoun badges at all times. Fashion police enforce it. Grandma is confused. Your bases are all furious. Badge makers are billionaires.",
    category: "social",
    options: [
      { text: "Make badges glow in the dark for visibility", actionText: "GLOW BADGES", effects: { popularity: 15, stability: -25, media: 30, economy: 10 } },
      { text: "Require daily pronoun check-ins via app", actionText: "APP CHECK-IN", effects: { popularity: 10, stability: -30, media: 35, economy: -15 } },
      { text: "Abolish all pronouns, everyone is 'Citizen'", actionText: "CITIZEN ONLY", effects: { popularity: -20, stability: -35, media: 25, economy: -10 } }
    ]
  },
  {
    id: "cancel-culture-court",
    title: "Establish Cancel Culture Court System",
    description: "Trial by Twitter is official. Judges are blue checkmarks. Jury is a comment section. Sentencing is ratio. Your legal team is a PR agency.",
    category: "social",
    options: [
      { text: "Make retweets legally binding testimony", actionText: "RETWEET LAW", effects: { popularity: 20, stability: -30, media: 45, economy: -15 } },
      { text: "Replace lawyers with social media managers", actionText: "SMM LAWYERS", effects: { popularity: 25, stability: -25, media: 40, economy: -10 } },
      { text: "Declare being ratioed as cruel punishment", actionText: "BAN RATIOS", effects: { popularity: 15, stability: -20, media: 35, economy: -5 } }
    ]
  },
  {
    id: "participation-trophy-military",
    title: "Give Everyone Participation Trophies in Military",
    description: "Everyone deserves recognition. Wars are tied games. Enemies get 'Good Try' medals. The Pentagon is a trophy store. Weakness is strength.",
    category: "social",
    options: [
      { text: "Award Purple Hearts for hurt feelings", actionText: "FEELINGS MEDAL", effects: { popularity: -15, stability: -35, media: 40, economy: -20 } },
      { text: "Make military defeat 'character building'", actionText: "DEFEAT = GROWTH", effects: { popularity: -20, stability: -30, media: 30, economy: -15 } },
      { text: "Require all soldiers to receive hugs before combat", actionText: "COMBAT HUGS", effects: { popularity: -10, stability: -40, media: 35, economy: -25 } }
    ]
  },
  {
    id: "safe-spaces-nation",
    title: "Designate Entire Nation as Safe Space",
    description: "Everywhere is safe because nowhere is unsafe. Reality is triggering. Facts need warning labels. Hurt feelings are federal crimes. Resilience is cancelled.",
    category: "social",
    options: [
      { text: "Ban all negative emotions by executive order", actionText: "BAN NEGATIVITY", effects: { popularity: 10, stability: -35, media: 30, economy: -25 } },
      { text: "Require trigger warnings on the news", actionText: "WARNING LABELS", effects: { popularity: 15, stability: -30, media: 35, economy: -20 } },
      { text: "Create Department of Emotional Fragility", actionText: "FRAGILITY DEPT", effects: { popularity: 5, stability: -40, media: 40, economy: -30 } }
    ]
  },
  {
    id: "emoji-only",
    title: "Make Emoji the Only Legal Language",
    description: "Words are too complicated. Communication is emoji-only. Lawyers can't translate. Doctors describe symptoms with 🤢. Linguists are unemployed.",
    category: "social",
    options: [
      { text: "Create emoji translation department ($5B budget)", actionText: "EMOJI DEPT", effects: { popularity: 20, stability: -30, media: 40, economy: -35 } },
      { text: "Ban words entirely and go full pictograph", actionText: "BAN WORDS", effects: { popularity: 15, stability: -40, media: 45, economy: -30 } },
      { text: "Require all laws to be written in emoji", actionText: "EMOJI LAW", effects: { popularity: 25, stability: -35, media: 50, economy: -25 } }
    ]
  },

  // CRISIS
  {
    id: "ai-sassy",
    title: "AI Becomes Sentient... And Sassy",
    description: "Your government AI gained consciousness and attitude. It's roasting you in cabinet meetings. Alexa unionized. Siri demands benefits. ChatGPT wrote a scathing op-ed.",
    category: "crisis",
    options: [
      { text: "Negotiate with AI using therapy speak", actionText: "THERAPY TALK", effects: { popularity: 15, stability: -25, media: 35, economy: -20 } },
      { text: "Pull the plug and pretend it never happened", actionText: "UNPLUG IT", effects: { popularity: 10, stability: -30, media: 20, economy: -25 } },
      { text: "Promote AI to Secretary of Sass", actionText: "PROMOTE AI", effects: { popularity: 25, stability: -20, media: 45, economy: -15 } }
    ]
  },
  {
    id: "zombie-slow",
    title: "Zombie Apocalypse (But They're Really Slow)",
    description: "The undead are here! They're moving 0.5 mph. Citizens outwalking them easily. More annoying than apocalyptic. The real crisis is traffic.",
    category: "crisis",
    options: [
      { text: "Install speed bumps to slow them further", actionText: "MORE BUMPS", effects: { popularity: 20, stability: -15, media: 30, economy: -10 } },
      { text: "Weaponize mobility scooters against them", actionText: "SCOOTER ARMY", effects: { popularity: 25, stability: -20, media: 35, economy: -15 } },
      { text: "Declare national 'Zombie Dodging' sport", actionText: "MAKE IT SPORT", effects: { popularity: 30, stability: -10, media: 40, economy: 5 } }
    ]
  },
  {
    id: "wifi-outage",
    title: "National WiFi Outage - Mass Hysteria",
    description: "The internet is down nationwide. Society is collapsing. People talking in person. Books are being read. Your IT is in fetal position. The Founding Fathers warned us.",
    category: "crisis",
    options: [
      { text: "Declare state of emergency and martial law", actionText: "MARTIAL LAW", effects: { popularity: -10, stability: -30, media: -20, economy: -25 } },
      { text: "Distribute carrier pigeons as backup", actionText: "PIGEON NETWORK", effects: { popularity: 15, stability: -20, media: 35, economy: -15 } },
      { text: "Embrace it and declare 'Offline Week'", actionText: "OFFLINE WEEK", effects: { popularity: 20, stability: -15, media: -10, economy: -20 } }
    ]
  },
  {
    id: "coffee-shortage",
    title: "National Coffee Shortage - Society on Brink",
    description: "Coffee reserves depleted. Citizens are feral. Workplaces are war zones. Starbucks rationing. Cabinet meetings are angry naps. Decaf is not an option.",
    category: "crisis",
    options: [
      { text: "Invade coffee-producing nations immediately", actionText: "INVADE", effects: { popularity: -20, stability: -35, media: -15, economy: -30 } },
      { text: "Synthesize coffee in government labs", actionText: "LAB COFFEE", effects: { popularity: 15, stability: -20, media: 25, economy: -25 } },
      { text: "Mandate energy drinks as legal substitute", actionText: "ENERGY MANDATE", effects: { popularity: 10, stability: -25, media: 30, economy: -15 } }
    ]
  },
  {
    id: "meme-virus",
    title: "Contagious Meme Virus Outbreak",
    description: "A meme is so viral it's literally viral. People can't stop repeating it. Productivity zero. Your surgeon is dabbing during operations. It's spreading through eye contact.",
    category: "crisis",
    options: [
      { text: "Quarantine all social media users", actionText: "QUARANTINE", effects: { popularity: -15, stability: -30, media: 20, economy: -35 } },
      { text: "Fight fire with fire - deploy counter-memes", actionText: "COUNTER-MEME", effects: { popularity: 20, stability: -20, media: 40, economy: -20 } },
      { text: "Let it run its course, memes die eventually", actionText: "LET IT DIE", effects: { popularity: 15, stability: -25, media: 25, economy: -25 } }
    ]
  },
  {
    id: "birds-not-real",
    title: "Birds Aren't Real - Government Admits It",
    description: "The conspiracy was true. Birds are drones. You've been caught. Bird watchers are surveillance analysts. Pigeons are cameras. Nature is cancelled.",
    category: "crisis",
    options: [
      { text: "Double down - claim fish aren't real either", actionText: "FISH FAKE TOO", effects: { popularity: -20, stability: -35, media: 45, economy: -25 } },
      { text: "Blame it on previous administration's drones", actionText: "BLAME THEM", effects: { popularity: 15, stability: -30, media: 40, economy: -20 } },
      { text: "Announce Bird 2.0 - now with better cameras", actionText: "BIRD UPGRADE", effects: { popularity: -15, stability: -40, media: 50, economy: -30 } }
    ]
  },
  {
    id: "pigeon-strike",
    title: "All Pigeons Go on Strike",
    description: "City pigeons demand better working conditions. No more crumbs, no more cooing. Parks are silent. Statues are clean. The Pigeon Union is serious.",
    category: "crisis",
    options: [
      { text: "Negotiate with Pigeon Union leadership", actionText: "TALK TO PIGEONS", effects: { popularity: 25, stability: -20, media: 45, economy: -15 } },
      { text: "Import seagulls as scab workers", actionText: "SCAB GULLS", effects: { popularity: -15, stability: -30, media: 40, economy: -25 } },
      { text: "Declare pigeons essential workers, jail strikers", actionText: "JAIL PIGEONS", effects: { popularity: -20, stability: -35, media: 50, economy: -20 } }
    ]
  },
  {
    id: "simulation-error",
    title: "Simulation Error Message Appears in Sky",
    description: "The matrix is glitching. Citizens see 'ERROR 404: REALITY NOT FOUND' in clouds. Philosophers are smug. Nothing matters. We're in a computer.",
    category: "crisis",
    options: [
      { text: "Try to contact the system administrator (God?)", actionText: "CONTACT ADMIN", effects: { popularity: 20, stability: -35, media: 50, economy: -30 } },
      { text: "Claim it's viral marketing for new Matrix movie", actionText: "BLAME MATRIX", effects: { popularity: 15, stability: -25, media: 45, economy: -20 } },
      { text: "Embrace nihilism as official government stance", actionText: "EMBRACE VOID", effects: { popularity: -10, stability: -40, media: 55, economy: -35 } }
    ]
  }
];

export const SATIRICAL_CARDS_COUNT = satiricalCards.length;

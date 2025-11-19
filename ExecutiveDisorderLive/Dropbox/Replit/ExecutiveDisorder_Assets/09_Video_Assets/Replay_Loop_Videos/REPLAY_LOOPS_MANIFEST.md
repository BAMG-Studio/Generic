# Replay Loop Videos - Complete Manifest
**Date:** October 11, 2025  
**Status:** ✅ 9 of 15 Generated (Partial)  
**Purpose:** Seamless looping background videos for Executive Disorder gameplay

---

## 📊 Overview

Successfully generated **9 high-quality seamless loop videos** for use as dynamic backgrounds during Executive Disorder gameplay. These AI-generated cinematics provide immersive political satire atmosphere for various game moments.

**Note:** Generation stopped at 9/15 videos due to Runway ML API credit limits. The 9 completed videos provide comprehensive coverage of core political themes.

---

## 🎬 Generated Replay Loop Videos

### 1. Government Office Ambient
- **File:** `government-office-ambient.mp4`
- **Duration:** 8 seconds
- **Size:** 5.20 MB
- **Description:** Professional government office interior with American flags, mahogany desk, dim lighting, subtle papers moving
- **Use Case:** Background for decision-making screens, character office scenes
- **Atmosphere:** Formal, authoritative, political power

### 2. Political Rally Crowd
- **File:** `political-rally-crowd.mp4`
- **Duration:** 8 seconds
- **Size:** 19.04 MB
- **Description:** Energetic political rally crowd waving signs and flags, cheering supporters, red/white/blue colors
- **Use Case:** Campaign events, popularity score displays, election moments
- **Atmosphere:** Enthusiastic, patriotic, grassroots energy

### 3. Breaking News Ticker
- **File:** `breaking-news-ticker.mp4`
- **Duration:** 8 seconds
- **Size:** 13.04 MB
- **Description:** Modern newsroom with multiple TV screens, scrolling news tickers, dynamic graphics
- **Use Case:** Media perception events, breaking news moments, scandal reveals
- **Atmosphere:** Urgent, media-focused, 24/7 news cycle

### 4. Capitol Building Exterior
- **File:** `capitol-building-exterior.mp4`
- **Duration:** 8 seconds
- **Size:** 12.35 MB
- **Description:** US Capitol building exterior with dramatic cloudy sky, American flag waving, golden hour
- **Use Case:** Legislative decisions, government authority moments, establishing shots
- **Atmosphere:** Majestic, democratic, institutional power

### 5. Press Conference Room
- **File:** `press-conference-room.mp4`
- **Duration:** 8 seconds
- **Size:** 7.16 MB
- **Description:** White House press conference room with podium, presidential seal, camera flashes
- **Use Case:** Public statements, media interaction events, official announcements
- **Atmosphere:** Official, scrutinized, high-stakes communication

### 6. Protest Demonstration
- **File:** `protest-demonstration.mp4`
- **Duration:** 8 seconds
- **Size:** 18.65 MB
- **Description:** Peaceful political protest with diverse people holding satirical signs, democratic demonstration
- **Use Case:** Low stability events, civil unrest moments, public dissent
- **Atmosphere:** Activist, democratic, people-power

### 7. Campaign Headquarters
- **File:** `campaign-headquarters.mp4`
- **Duration:** 8 seconds
- **Size:** 11.24 MB
- **Description:** Busy campaign war room with TV screens, volunteers on phones, election maps, chaotic energy
- **Use Case:** Election events, campaign strategy moments, political planning
- **Atmosphere:** Hectic, strategic, behind-the-scenes politics

### 8. Stock Market Displays
- **File:** `stock-market-displays.mp4`
- **Duration:** 8 seconds
- **Size:** 14.34 MB
- **Description:** Wall Street trading floor screens, stock tickers scrolling, economic data displays, financial charts
- **Use Case:** Economy resource displays, financial crisis events, market reactions
- **Atmosphere:** Corporate, financial, economic pressure

### 9. Media Circus Exterior
- **File:** `media-circus-exterior.mp4`
- **Duration:** 8 seconds
- **Size:** 11.40 MB
- **Description:** Outside government building with news vans, satellite dishes, reporters preparing
- **Use Case:** Scandal moments, high media attention events, breaking story reveals
- **Atmosphere:** Chaotic, journalistic frenzy, scandal energy

---

## 📋 Videos Not Generated (Due to API Credits)

The following 6 videos were planned but not generated:

1. **debate-stage-empty** - Presidential debate stage setup
2. **crisis-situation-room** - White House situation room
3. **oval-office-view** - Oval Office interior perspective
4. **legislative-chamber** - Congressional chamber interior
5. **international-summit** - Diplomatic summit room
6. **election-night-boards** - Election broadcast studio

**Future Option:** These can be generated when additional API credits are available.

---

## 🎯 Technical Specifications

**Video Format:**
- Container: MP4 (H.264)
- Resolution: 1280x720 HD
- Frame Rate: 24 fps
- Duration: 8 seconds each
- Video Codec: H.264, optimized for web
- Total Size: ~112 MB (9 videos)

**Generation Details:**
- AI Model: Google Veo3 via Runway ML API
- Prompt Style: Seamless loop optimized
- Quality: High-definition cinematic
- Theme: Political satire backgrounds

**Loop Optimization:**
- Videos designed with seamless loop prompts
- Can be set to `loop` attribute in video tags
- 8-second duration provides smooth repetition
- No jarring transitions when looping

---

## 📂 File Locations

**Dropbox Cloud Storage:**
```
/Replit/ExecutiveDisorder_Assets/09_Video_Assets/Replay_Loop_Videos/
├── government-office-ambient.mp4
├── political-rally-crowd.mp4
├── breaking-news-ticker.mp4
├── capitol-building-exterior.mp4
├── press-conference-room.mp4
├── protest-demonstration.mp4
├── campaign-headquarters.mp4
├── stock-market-displays.mp4
└── media-circus-exterior.mp4
```

**Local Development:**
```
Dropbox/Replit/ExecutiveDisorder_Assets/09_Video_Assets/Replay_Loop_Videos/
```

**Game Integration:**
```
client/public/videos/replay-loops/
```

---

## 💡 Integration Recommendations

### Option A: Event-Triggered Backgrounds
Use specific loops for matching game events:
```tsx
// Economy crisis event
<video src="/videos/replay-loops/stock-market-displays.mp4" autoPlay muted loop className="absolute inset-0 object-cover" />

// Media scandal event
<video src="/videos/replay-loops/media-circus-exterior.mp4" autoPlay muted loop className="absolute inset-0 object-cover" />

// Low stability event
<video src="/videos/replay-loops/protest-demonstration.mp4" autoPlay muted loop className="absolute inset-0 object-cover" />
```

### Option B: Resource-Based Backgrounds
Show background based on current resource state:
```tsx
function GameBackground({ resources }) {
  const getBackgroundVideo = () => {
    if (resources.media < 30) return '/videos/replay-loops/media-circus-exterior.mp4';
    if (resources.economy < 30) return '/videos/replay-loops/stock-market-displays.mp4';
    if (resources.stability < 30) return '/videos/replay-loops/protest-demonstration.mp4';
    if (resources.popularity > 70) return '/videos/replay-loops/political-rally-crowd.mp4';
    return '/videos/replay-loops/government-office-ambient.mp4';
  };

  return <video src={getBackgroundVideo()} autoPlay muted loop />;
}
```

### Option C: Phase-Based Backgrounds
Different loops for different game phases:
```tsx
const phaseBackgrounds = {
  'character-selection': '/videos/replay-loops/capitol-building-exterior.mp4',
  'gameplay': '/videos/replay-loops/government-office-ambient.mp4',
  'crisis': '/videos/replay-loops/press-conference-room.mp4',
  'election': '/videos/replay-loops/campaign-headquarters.mp4'
};
```

### Option D: Random Rotation
Randomly cycle through loops for variety:
```tsx
const backgrounds = [
  'government-office-ambient',
  'political-rally-crowd',
  'breaking-news-ticker',
  'capitol-building-exterior',
  'press-conference-room',
  'campaign-headquarters'
];

const randomBg = backgrounds[Math.floor(Math.random() * backgrounds.length)];
```

---

## 🎮 Usage Examples

### React Component Example:
```tsx
interface BackgroundLoopProps {
  scene: 'office' | 'rally' | 'news' | 'capitol' | 'press' | 'protest' | 'campaign' | 'market' | 'media';
  opacity?: number;
}

export function BackgroundLoop({ scene, opacity = 0.5 }: BackgroundLoopProps) {
  const videoMap = {
    office: 'government-office-ambient.mp4',
    rally: 'political-rally-crowd.mp4',
    news: 'breaking-news-ticker.mp4',
    capitol: 'capitol-building-exterior.mp4',
    press: 'press-conference-room.mp4',
    protest: 'protest-demonstration.mp4',
    campaign: 'campaign-headquarters.mp4',
    market: 'stock-market-displays.mp4',
    media: 'media-circus-exterior.mp4'
  };

  return (
    <div className="absolute inset-0 overflow-hidden">
      <video
        src={`/videos/replay-loops/${videoMap[scene]}`}
        autoPlay
        muted
        loop
        playsInline
        className="w-full h-full object-cover"
        style={{ opacity }}
      />
      <div className="absolute inset-0 bg-gradient-to-b from-black/50 to-transparent" />
    </div>
  );
}
```

### Performance Optimization:
```tsx
// Preload videos for smooth playback
useEffect(() => {
  const videos = [
    '/videos/replay-loops/government-office-ambient.mp4',
    '/videos/replay-loops/political-rally-crowd.mp4',
    // ... other videos
  ];

  videos.forEach(src => {
    const video = document.createElement('video');
    video.src = src;
    video.preload = 'auto';
  });
}, []);
```

---

## 🎨 Thematic Mapping

**Power & Authority:**
- government-office-ambient.mp4
- capitol-building-exterior.mp4
- press-conference-room.mp4

**Public Engagement:**
- political-rally-crowd.mp4
- protest-demonstration.mp4
- campaign-headquarters.mp4

**Media & Communication:**
- breaking-news-ticker.mp4
- media-circus-exterior.mp4

**Economy & Finance:**
- stock-market-displays.mp4

---

## 📊 Asset Summary

| Video | Duration | Size | Primary Use | Atmosphere |
|-------|----------|------|-------------|------------|
| Government Office | 8s | 5.2 MB | Decision screens | Formal |
| Political Rally | 8s | 19 MB | Popularity events | Energetic |
| Breaking News | 8s | 13 MB | Media events | Urgent |
| Capitol Building | 8s | 12 MB | Legislative moments | Majestic |
| Press Conference | 8s | 7.2 MB | Public statements | Official |
| Protest Demo | 8s | 18.7 MB | Stability crisis | Activist |
| Campaign HQ | 8s | 11.2 MB | Election events | Strategic |
| Stock Market | 8s | 14.3 MB | Economy display | Corporate |
| Media Circus | 8s | 11.4 MB | Scandal moments | Chaotic |

**Total:** 9 videos, 112.1 MB, 72 seconds of looping content

---

## 🚀 Next Steps

1. **Implement in Game:** Integrate loops into gameplay screens using recommended options
2. **Test Performance:** Ensure smooth playback across devices
3. **Optimize Loading:** Implement preloading strategy for seamless transitions
4. **Consider Music:** Add subtle background audio to enhance atmosphere
5. **Future Generation:** Generate remaining 6 videos when API credits available

---

## 📝 Production Notes

- **Generation Method:** Runway ML Veo3 text-to-video AI
- **Total Cost:** ~$4.50 (9 videos × $0.50 each)
- **Generation Time:** ~45 minutes total
- **Credit Limitation:** Stopped at 9/15 due to API credit depletion
- **Quality:** High-definition cinematic, optimized for web playback

---

*These replay loop videos provide dynamic, thematically appropriate backgrounds that enhance Executive Disorder's political satire gameplay experience.*

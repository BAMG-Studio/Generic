# Executive Disorder - Opening Cinematics
## 5 AI-Generated Cinematic Videos

**Generated:** October 11, 2025  
**Total Videos:** 5  
**Total Size:** ~49 MB  
**Model:** Google Veo3 (via Runway ML)  
**Format:** MP4, 1280x720, 8 seconds each  

---

## 🎬 The Cinematics

### 1. **Political Chaos** (8.8 MB)
A cinematic slow zoom through a grandiose presidential office with papers flying dramatically, red alert lights pulsing, and shadowy figures arguing. Sets the tone for the game's chaotic political environment.

### 2. **Media Frenzy** (13 MB)
Dynamic tracking shot through a chaotic newsroom with breaking news banners, reporters frantically typing, and emergency broadcast lights strobing. Highlights the media's role in amplifying political drama.

### 3. **Power Ascension** (8.8 MB)
Epic dolly shot rising up government building steps at golden hour with dramatic shadows and American flags waving. Represents the player's journey to political leadership.

### 4. **Critical Decision** (6.1 MB)
Intense close-up of a desk with policy documents and a hand hovering over APPROVED/REJECTED stamps while a red phone rings ominously. Shows the weight of decision-making.

### 5. **Absurd Spectacle** (13 MB)
Surreal tracking shot through a bizarre political rally with confetti, balloons, and an empty podium. Captures the game's satirical and absurd tone.

---

## 📂 File Locations

**Primary Location:**
```
Dropbox/Replit/ExecutiveDisorder_Assets/09_Video_Assets/Opening_Cinematics/
```

**Game Integration Location:**
```
client/public/videos/opening-cinematics/
```

---

## 🚀 Integration Examples

### Single Cinematic
```typescript
<video autoPlay muted onEnded={() => navigate('/game')}>
  <source src="/videos/opening-cinematics/opening-01-political-chaos.mp4" />
</video>
```

### Random Selection
```typescript
const cinematics = [
  'opening-01-political-chaos.mp4',
  'opening-02-media-frenzy.mp4',
  'opening-03-power-ascension.mp4',
  'opening-04-critical-decision.mp4',
  'opening-05-absurd-spectacle.mp4',
];

const randomVideo = cinematics[Math.floor(Math.random() * cinematics.length)];
```

### Sequential Montage (40 seconds total)
Play all 5 videos in sequence for a complete opening experience.

---

## 📊 Generation Details

**Runway ML Task IDs:**
- Political Chaos: `69a37a51-2ee4-4f6a-bec1-f6ca880151e0`
- Media Frenzy: `38fbf8c6-4f82-4586-a06d-df7f47b4b3c8`
- Power Ascension: `439b524d-7769-486e-8b15-3cb907784dcf`
- Critical Decision: `27f98b18-ee26-4fba-8ab8-402637c0c75b`
- Absurd Spectacle: `dd422281-8067-4723-90d4-1e2c77cb74cc`

**Generation Cost:** ~$2.50 (50 credits per 8-second video)

---

For detailed integration guidance and thematic analysis, see `OPENING_CINEMATICS_MANIFEST.md`.

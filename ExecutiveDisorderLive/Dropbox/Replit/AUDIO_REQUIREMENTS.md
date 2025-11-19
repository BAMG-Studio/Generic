# Executive Disorder - Audio Requirements & Solutions

**Status:** Audio files need replacement  
**Issue:** Current files are 32-byte placeholders with no audio data  
**Date:** October 10, 2025

---

## 🚨 Critical Missing Audio Files

### Essential SFX (Game Won't Work Without These)
1. **`/sounds/success.mp3`** - Success/decision confirmation sound
   - Used when player makes a card decision
   - Referenced in: `GameplayScene2D.tsx`, `useAudio.tsx`
   - Recommended: Pleasant chime, 0.3-0.5 seconds

2. **`/sounds/hit.mp3`** - Negative feedback/impact sound  
   - Used for negative events or failed actions
   - Referenced in: `useAudio.tsx`
   - Recommended: Low impact sound, 0.2-0.3 seconds

3. **`/sounds/background.mp3`** - Background music loop
   - Main background music for gameplay
   - Referenced in: `AudioManager.tsx`, `BackgroundMusic.tsx`
   - Recommended: 15-30 second loopable ambient track

### Background Music (Currently 32-byte Placeholders)
4-13. **Ten themed music tracks** in `/audio/music/`:
   - `main_theme.mp3` - Main menu music (20-30 sec loop)
   - `character_selection.mp3` - Character select (15-20 sec loop)
   - `gameplay_ambient.mp3` - Main gameplay (30-60 sec loop)
   - `crisis_mode.mp3` - Crisis events (10-15 sec loop)
   - `victory_fanfare.mp3` - Victory screen (5-8 sec)
   - `defeat_theme.mp3` - Game over (6-10 sec)
   - `diplomatic_tension.mp3` - International events (12-20 sec loop)
   - `media_chaos.mp3` - Media scandals (10-15 sec loop)
   - `economic_disaster.mp3` - Economic crisis (8-12 sec loop)
   - `campaign_rally.mp3` - Rally events (12-18 sec loop)

---

## 🎯 Recommended Solutions

### Option 1: Royalty-Free Audio Libraries (FREE - RECOMMENDED)
**Immediate solution - no cost, legally safe**

#### For SFX:
- **Freesound.org** (https://freesound.org)
  - Filter by CC0 license (public domain)
  - Search terms: "button click", "success chime", "error beep"
  - Download MP3, place in `client/public/sounds/`

- **Zapsplat.com** (https://zapsplat.com)
  - Free account required
  - High-quality UI sounds
  - "Game UI" category

- **Mixkit.co** (https://mixkit.co/free-sound-effects)
  - No attribution required
  - Clean interface
  - Direct MP3 downloads

#### For Music:
- **Incompetech.com** (https://incompetech.com/music)
  - Kevin MacLeod's royalty-free music
  - Attribution required (add to credits)
  - Search by mood/genre

- **Purple Planet Music** (https://purple-planet.com)
  - 100% free, royalty-free
  - Great for game background music
  - Various genres and moods

- **Bensound.com** (https://bensound.com)
  - Free with attribution
  - Professional quality
  - Loopable tracks

### Option 2: AI Music Generation (PAID - HIGH QUALITY)
**Professional quality, custom-tailored**

1. **Mubert AI** (https://mubert.com)
   - Generate custom loops by mood/genre
   - Royalty-free for commercial use
   - ~$14/month starter plan
   - Perfect for game music

2. **Soundraw.io** (https://soundraw.io)
   - AI music composition
   - Customize tempo, mood, instruments
   - ~$16.99/month
   - Download unlimited tracks

3. **AIVA** (https://aiva.ai)
   - AI composer for soundtracks
   - Multiple genres and styles
   - Free tier available (limited)
   - Pro: $11/month

### Option 3: ElevenLabs Sound Effects (EXPERIMENTAL)
**Use existing API integration**

ElevenLabs has beta sound effects generation:
- Can generate short SFX (beeps, chimes, impacts)
- Already have API key: `ELEVENLABS_API_KEY`
- Service: `server/services/elevenlabs.ts`
- **Limitation**: Cannot generate music, only short effects

Test generation:
```bash
tsx scripts/generateGameAudio.ts
```

### Option 4: Commission Original Audio (PREMIUM)
**Highest quality, fully custom**

- Fiverr.com - $50-200 per track
- Upwork.com - $500-2000 for full game soundtrack
- SoundBetter.com - Professional composers
- Ensure work-for-hire contract for full rights

---

## 📋 Implementation Checklist

### Immediate Fix (1 hour)
- [ ] Download 3 essential SFX from Freesound.org (CC0)
  - success.mp3
  - hit.mp3  
  - background.mp3 (or use one of the themed tracks)
- [ ] Place in `client/public/sounds/`
- [ ] Test in-game: Start game, make a decision, listen for sounds

### Full Audio (2-4 hours)
- [ ] Download or generate 10 themed music tracks
- [ ] Replace placeholder files in `client/public/audio/music/`
- [ ] Ensure all tracks loop seamlessly
- [ ] Upload to Dropbox: `/Replit/Art/Audio/`
- [ ] Update music_metadata.json with real file info

### Quality Check
- [ ] All files > 32 bytes (currently all are 32 bytes)
- [ ] Files play in browser
- [ ] Volumes balanced (0.3-0.5 for music, 0.3-0.7 for SFX)
- [ ] Smooth loops (no clicks/pops at loop point)
- [ ] Attribution documented (if using CC-BY content)

---

## 🎵 Detailed Track Specifications

### Main Theme (main_theme.mp3)
- **Mood:** Grandiose yet comedic, satirical
- **Instruments:** Pompous brass, orchestral strings, subtle humor
- **Tempo:** 120 BPM
- **Duration:** 20-30 seconds (loopable)
- **Usage:** Main menu, game intro
- **Reference:** Political satire, presidential theme parody

### Character Selection (character_selection.mp3)  
- **Mood:** Upbeat, quirky, playful
- **Instruments:** Lighthearted melody, comedic undertones
- **Tempo:** 130 BPM
- **Duration:** 15-20 seconds (loopable)
- **Usage:** Character selection screen

### Gameplay Ambient (gameplay_ambient.mp3)
- **Mood:** Contemplative with underlying chaos/tension
- **Instruments:** Ambient pads, subtle drums, light tension
- **Tempo:** 90 BPM
- **Duration:** 30-60 seconds (loopable)
- **Usage:** Main gameplay loop, card decisions

### Crisis Mode (crisis_mode.mp3)
- **Mood:** Urgent, chaotic, intense
- **Instruments:** Fast strings, dramatic percussion
- **Tempo:** 150 BPM
- **Duration:** 10-15 seconds (loopable)
- **Usage:** Crisis events, low resources, emergencies

### Victory Fanfare (victory_fanfare.mp3)
- **Mood:** Triumphant with ironic twist
- **Instruments:** Brass fanfare, celebratory with satirical edge
- **Tempo:** 140 BPM
- **Duration:** 5-8 seconds (one-shot)
- **Usage:** Game victory, successful term completion

### Defeat Theme (defeat_theme.mp3)
- **Mood:** Melancholic yet comedic, dark humor
- **Instruments:** Sad trombone, descending strings
- **Tempo:** 70 BPM
- **Duration:** 6-10 seconds (one-shot)
- **Usage:** Game over, impeachment, failed objectives

### Diplomatic Tension (diplomatic_tension.mp3)
- **Mood:** Suspenseful, tense diplomatic atmosphere
- **Instruments:** World instruments, suspense strings
- **Tempo:** 100 BPM
- **Duration:** 12-20 seconds (loopable)
- **Usage:** International crisis cards, foreign relations

### Media Chaos (media_chaos.mp3)
- **Mood:** Frantic media frenzy, fast-paced
- **Instruments:** News theme parody, comedic breaks
- **Tempo:** 135 BPM
- **Duration:** 10-15 seconds (loopable)
- **Usage:** Media scandal events, press disasters

### Economic Disaster (economic_disaster.mp3)
- **Mood:** Ominous financial doom, descending
- **Instruments:** Descending scales, market crash sounds
- **Tempo:** 110 BPM
- **Duration:** 8-12 seconds (loopable)
- **Usage:** Economic crisis, budget disasters

### Campaign Rally (campaign_rally.mp3)
- **Mood:** Energetic populist excitement
- **Instruments:** Upbeat campaign music, crowd energy
- **Tempo:** 125 BPM
- **Duration:** 12-18 seconds (loopable)
- **Usage:** Campaign events, popularity boosts

---

## 🔧 Technical Requirements

### File Specifications
- **Format:** MP3 or WAV (MP3 preferred for size)
- **Sample Rate:** 44100 Hz (CD quality)
- **Bit Rate:** 128-192 kbps (MP3)
- **Channels:** Stereo (2 channels)
- **Normalization:** -3dB to -6dB (prevent clipping)

### Integration
```typescript
// Example usage in game
const audio = new Audio('/sounds/success.mp3');
audio.volume = 0.5;
audio.play().catch(console.error);
```

### Looping
For seamless loops, ensure:
1. Track starts and ends at zero-crossing
2. Same amplitude at start/end
3. Test in browser: `audio.loop = true`

---

## 📦 File Upload Process

### After obtaining audio files:

1. **Place locally:**
   ```bash
   # SFX
   client/public/sounds/
   ├── success.mp3
   ├── hit.mp3
   └── background.mp3

   # Music
   client/public/audio/music/
   ├── main_theme.mp3
   ├── character_selection.mp3
   └── [... 8 more tracks]
   ```

2. **Upload to Dropbox:**
   ```bash
   tsx scripts/uploadMusicToDropbox.ts
   ```

3. **Update metadata:**
   ```bash
   # Edit music_metadata.json with actual file sizes, durations
   ```

4. **Test in-game:**
   ```bash
   npm run dev
   # Play game, verify all sounds work
   ```

---

## 📝 Attribution Requirements

### If using CC-BY content:
Create `client/public/AUDIO_CREDITS.md`:

```markdown
# Audio Credits

## Sound Effects
- success.mp3 - "Success Chime" by [Artist] (Freesound.org)
- hit.mp3 - "Impact Sound" by [Artist] (Freesound.org)

## Music
- main_theme.mp3 - "Title" by Kevin MacLeod (incompetech.com)
  Licensed under Creative Commons: By Attribution 3.0 License
  http://creativecommons.org/licenses/by/3.0/

[... additional credits]
```

---

## 🎮 Current Status

**Audio System:** ✅ Fully implemented  
**ElevenLabs Voice:** ✅ Ready for character voices  
**Music Files:** ❌ 32-byte placeholders (need replacement)  
**Essential SFX:** ❌ Missing (game won't work)  

**Next Steps:**
1. Download audio from recommended sources
2. Replace placeholder files  
3. Test in-game
4. Upload to Dropbox backup

---

**Last Updated:** October 10, 2025  
**Priority:** HIGH - Game cannot function without audio files  
**Estimated Fix Time:** 1-4 hours depending on approach
# Audio Requirements - Executive Disorder

## ⚠️ CRITICAL ISSUE: Audio Files Are Placeholders

### Problem
All audio files in `/client/public/audio/music/` are **empty 32-byte placeholders** - they contain no actual audio data. This causes distorted sound output instead of proper English-language music.

### Current Placeholder Files (Need Replacement)
```
client/public/audio/music/
├── main_theme.mp3 (32 bytes - PLACEHOLDER)
├── campaign_rally.mp3 (32 bytes - PLACEHOLDER)
├── character_selection.mp3 (32 bytes - PLACEHOLDER)
├── crisis_mode.mp3 (32 bytes - PLACEHOLDER)
├── defeat_theme.mp3 (32 bytes - PLACEHOLDER)
├── diplomatic_tension.mp3 (32 bytes - PLACEHOLDER)
├── economic_disaster.mp3 (32 bytes - PLACEHOLDER)
├── gameplay_ambient.mp3 (32 bytes - PLACEHOLDER)
├── media_chaos.mp3 (32 bytes - PLACEHOLDER)
└── victory_fanfare.mp3 (32 bytes - PLACEHOLDER)
```

### Required Audio Specifications
- **Format:** MP3 (audio/mpeg)
- **Language:** English
- **Quality:** 128-192 kbps recommended
- **Duration:** Varies by track (loops for ambient music)
- **Style:** Political satire theme - dramatic, comedic, engaging
- **Volume:** Normalized to prevent clipping

### Audio Usage in Game
1. **Title Page:** `main_theme.mp3` - plays on START button click, loops
2. **Character Selection:** `character_selection.mp3` (if implemented)
3. **Gameplay:** `gameplay_ambient.mp3` (background music)
4. **Crisis Events:** `crisis_mode.mp3` (dramatic alerts)
5. **Endings:** `victory_fanfare.mp3` or `defeat_theme.mp3`

### Implementation Notes
- Audio plays via HTML5 `<audio>` element with ref
- Volume controlled programmatically (default 0.6)
- Mute toggle available in UI
- Audio autoplay requires user interaction (handled via START button)

### Next Steps
1. **Option A:** Generate English audio using AI music generation (e.g., ElevenLabs, Suno AI)
2. **Option B:** Use royalty-free music libraries with proper licensing
3. **Option C:** Commission custom political satire music tracks

### File Locations
- **Current placeholders:** `/client/public/audio/music/`
- **Backup to Dropbox:** `/Dropbox/Replit/ExecutiveDisorder_Assets/06_Audio/Music/`
- **Metadata reference:** `/client/public/audio/music/music_metadata.json`

---

**Status:** ⚠️ Blocking issue for audio experience  
**Priority:** High  
**Impact:** Users hear distorted/silent audio instead of intended soundtrack

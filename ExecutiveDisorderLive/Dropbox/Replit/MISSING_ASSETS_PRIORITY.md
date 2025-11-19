# Executive Disorder - Missing Assets Priority List

**Audit Date:** October 10, 2025  
**Status:** Comprehensive asset gap analysis complete  
**Dropbox Current:** 497 files, 650.49 MB

---

## 🚨 CRITICAL - Game Cannot Function Without

### 1. Music Files (10 tracks) - HIGH PRIORITY
**Status:** ❌ Placeholder files (32 bytes each, no audio)  
**Location:** `client/public/audio/music/` & `Dropbox/Replit/Audio/Music/`

**Required Files:**
1. `main_theme.mp3` - Main menu music (20-30 sec loop)
2. `character_selection.mp3` - Character select (15-20 sec loop)
3. `gameplay_ambient.mp3` - Main gameplay (30-60 sec loop)
4. `crisis_mode.mp3` - Crisis events (10-15 sec loop)
5. `victory_fanfare.mp3` - Victory screen (5-8 sec)
6. `defeat_theme.mp3` - Game over (6-10 sec)
7. `diplomatic_tension.mp3` - International events (12-20 sec loop)
8. `media_chaos.mp3` - Media scandals (10-15 sec loop)
9. `economic_disaster.mp3` - Economic crisis (8-12 sec loop)
10. `campaign_rally.mp3` - Rally events (12-18 sec loop)

**Solution:** See `AUDIO_REQUIREMENTS.md` for sourcing options (royalty-free libraries, AI generation, etc.)

**Note:** ✅ SFX already working! (success.mp3, hit.mp3, background.mp3)

---

## 🎨 HIGH PRIORITY - Visual Assets Needed for Polish

### 2. Scene Backgrounds (5 categories) - HIGH PRIORITY
**Status:** ❌ All empty folders  
**Impact:** Game lacks environmental context

**Required:**
- **Backgrounds** (`Dropbox/Replit/Scenes/Backgrounds/`)
  - Oval Office
  - White House exterior
  - Press room
  - Situation room
  - _Estimated: 4-6 background images_

- **Crisis Scenes** (`Dropbox/Replit/Scenes/CrisisScenes/`)
  - Economic meltdown visuals
  - International conflict
  - Natural disaster
  - _Estimated: 3-5 crisis backgrounds_

- **Meeting Rooms** (`Dropbox/Replit/Scenes/MeetingRooms/`)
  - Cabinet room
  - Conference room
  - _Estimated: 2-3 meeting backgrounds_

- **News Scenes** (`Dropbox/Replit/Scenes/NewsScenes/`)
  - TV news studio
  - Breaking news backdrop
  - _Estimated: 2-3 news backgrounds_

- **Public Spaces** (`Dropbox/Replit/Scenes/PublicSpaces/`)
  - Rally stage
  - Public square
  - Airport/travel
  - _Estimated: 2-4 public backgrounds_

**Total Backgrounds Needed:** ~15-20 images

---

### 3. Additional Character Portraits - MEDIUM PRIORITY
**Status:** Main characters complete (60 portraits), but missing supporting characters  
**Currently Empty:**

- **Executives** (`Dropbox/Replit/Portraits/Executives/`)
  - Alternative executive portraits beyond main 10 characters
  - _Estimated: 0 needed (main characters already exist)_

- **Staff** (`Dropbox/Replit/Portraits/Staff/`)
  - Chief of Staff
  - Press Secretary
  - National Security Advisor
  - Economic Advisor
  - _Estimated: 4-6 staff portraits_

- **Citizens** (`Dropbox/Replit/Portraits/Citizens/`)
  - Everyday Americans for events
  - _Estimated: 3-5 citizen portraits_

- **International** (`Dropbox/Replit/Portraits/International/`)
  - Foreign leaders
  - Diplomats
  - _Estimated: 3-5 international portraits_

- **Stakeholders** (`Dropbox/Replit/Portraits/Stakeholders/`)
  - Lobbyists
  - Corporate executives
  - Union leaders
  - _Estimated: 3-5 stakeholder portraits_

**Total Character Portraits Needed:** ~15-25 images

---

### 4. Crisis Characters - MEDIUM PRIORITY
**Status:** ❌ Empty folder  
**Location:** `Dropbox/Replit/Crisis/`

**All Subcategories Empty:**
- Activists
- Extremists
- Hackers
- Infiltrators
- Journalists
- Protesters
- Rebels
- Rivals
- Spies
- Whistleblowers

**Estimated Needed:** 10-20 crisis character portraits (1-2 per category)

---

### 5. Extended Card Assets - MEDIUM PRIORITY
**Status:** Base EDX Series complete (10 cards), extended series empty

**Missing:**
- **EDX1 Series** (`Dropbox/Replit/Art/Cards/EDX1_Series/`)
  - Cards 26-50 (if planned)
  
- **EDX2 Series** (`Dropbox/Replit/Art/Cards/EDX2_Series/`)
  - Cards 51-75 (if planned)
  
- **EDX3 Series** (`Dropbox/Replit/Art/Cards/EDX3_Series/`)
  - Cards 76-100 (if planned)

**Note:** May not be needed if game uses only base 25 cards

---

## 🎯 MEDIUM PRIORITY - Brand & UI Assets

### 6. Main Logo - MEDIUM PRIORITY
**Status:** ❌ Empty  
**Location:** `Dropbox/Replit/Brand/Logos/`  
**Current:** Only 2 logo variations exist in `/logos/`

**Needed:**
- Main "Executive Disorder" logo (primary)
- Logo variations for different contexts
- _Estimated: 1 main logo + 3-5 variations_

---

### 7. 3D Models - LOW PRIORITY
**Status:** ❌ Empty  
**Locations:** 
- `Dropbox/Replit/Art/3D/Models/`
- `Dropbox/Replit/models/`

**Potential 3D Assets:**
- Oval Office desk (decorative)
- Presidential podium
- Briefcase
- Nuclear football
- _Estimated: 0-5 models (only if 3D mode is used)_

---

### 8. Video Assets - LOW PRIORITY
**Status:** ❌ Empty  
**Location:** `Dropbox/Replit/Art/Video/Openings/`

**Potential Videos:**
- Game intro/splash screen video
- Character intro animations
- _Estimated: 0-2 videos (optional enhancement)_

---

## 📊 Asset Generation Priority Summary

### Phase 1: Critical (Game Function)
1. ✅ **SFX** - Already complete!
2. ❌ **Music** - 10 files (use royalty-free sources)

### Phase 2: Visual Polish (High Impact)
3. ❌ **Scene Backgrounds** - 15-20 images (game environments)
4. ❌ **Main Logo** - 1 primary logo

### Phase 3: Character Depth (Medium Impact)
5. ❌ **Supporting Characters** - 15-25 portraits (staff, citizens, international, stakeholders)
6. ❌ **Crisis Characters** - 10-20 portraits

### Phase 4: Extended Content (Low Priority)
7. ❌ **Extended Card Series** - Variable (only if needed)
8. ❌ **3D Models** - 0-5 models (optional)
9. ❌ **Video Intros** - 0-2 videos (optional)

---

## 🎨 Asset Generation Recommendations

### For Images (Portraits, Backgrounds, Logos):
**Use Image Generation Tool:**
```typescript
generate_image_tool({
  prompt: "Detailed description here",
  aspect_ratio: "16:9", // or "1:1" for portraits
  one_line_summary: "brief description"
})
```

**Best for:**
- Character portraits (political satire style)
- Scene backgrounds (realistic or stylized)
- Logos and branding
- Card artwork

### For Music:
**Use Royalty-Free Sources:**
- Incompetech.com (Kevin MacLeod)
- Purple Planet Music
- Bensound.com
- Or AI music: Mubert, Soundraw, AIVA

See `AUDIO_REQUIREMENTS.md` for complete guide

### For 3D Models:
**Use 3D Generation Tool (if needed):**
```typescript
generate_3d_model({
  requests: [{
    description: "Model description",
    file_path_save_to: "path/to/save.glb",
    quality: "medium"
  }]
})
```

---

## 📝 Current Asset Inventory (What Exists)

### ✅ Already Complete:
- **Character Portraits - Main:** 60 PNG files (10 characters × 6 emotions)
- **Character Portraits - Variations:** 60 PNG files (duplicates in Dropbox)
- **SFX Audio:** 3 working MP3 files (success, hit, background)
- **Card Assets - Base:** 10 EDX series cards
- **UI Assets:** 13 files (icons + general)
- **Textures:** 5 files
- **Generated Images:** 342 files (various assets)
- **Fonts:** 1 file
- **Code Backups:** 4 TypeScript files

**Total Existing:** 497 files, 650.49 MB in Dropbox

---

## 🚀 Next Steps

### Immediate (This Session):
1. ✅ Audit complete - gaps identified
2. ⏳ Generate scene backgrounds (15-20 images)
3. ⏳ Generate main logo
4. ⏳ Generate supporting character portraits
5. ⏳ Upload all to Dropbox automatically

### User Action Required:
1. 📥 Download real music files from royalty-free sources
2. 📂 Replace 10 placeholder MP3s in `client/public/audio/music/`
3. 📤 Re-upload music to Dropbox backend

### Future Enhancements:
- Extended card series (if needed for more content)
- 3D models (if 3D mode is implemented)
- Video intros (polish/marketing)

---

## 💾 Dropbox Auto-Upload

All generated assets will be automatically uploaded to Dropbox using:
```bash
tsx scripts/syncAllToDropbox.ts
```

**Target folders:**
- Characters → `/Dropbox/Replit/Portraits/`
- Backgrounds → `/Dropbox/Replit/Scenes/`
- Logos → `/Dropbox/Replit/Brand/Logos/`
- Any new assets → Appropriate category folders

---

**Last Updated:** October 10, 2025  
**Next Review:** After Phase 2 generation complete  
**Estimated Generation Time:** 2-4 hours for high-priority assets
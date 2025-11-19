# Executive Disorder - Music Track Usage Guide

## Track List (10 Tracks)

### 1. Executive Disorder Main Theme
**File:** main_theme.mp3  
**Description:** Satirical orchestral piece with pompous brass and comedic undertones  
**Mood:** Grandiose yet comedic  
**Tempo:** 120 BPM  
**Duration:** 3:30  
**Usage:** Main menu, game intro  

### 2. Choose Your Chaos
**File:** character_selection.mp3  
**Description:** Upbeat, quirky music with political undertones  
**Mood:** Playful and satirical  
**Tempo:** 130 BPM  
**Duration:** 2:45  
**Usage:** Character selection screen  

### 3. Oval Office Blues
**File:** gameplay_ambient.mp3  
**Description:** Ambient background music with subtle tension  
**Mood:** Contemplative with underlying chaos  
**Tempo:** 90 BPM  
**Duration:** 5:00  
**Usage:** Main gameplay loop  

### 4. Political Meltdown
**File:** crisis_mode.mp3  
**Description:** Intense, fast-paced crisis music with dramatic strings  
**Mood:** Urgent and chaotic  
**Tempo:** 150 BPM  
**Duration:** 2:00  
**Usage:** Crisis events, low resources  

### 5. Democracy Prevails
**File:** victory_fanfare.mp3  
**Description:** Triumphant orchestral victory theme with ironic twist  
**Mood:** Celebratory with satirical edge  
**Tempo:** 140 BPM  
**Duration:** 1:30  
**Usage:** Game victory, achievements  

### 6. Impeachment Blues
**File:** defeat_theme.mp3  
**Description:** Melancholic yet comedic defeat music  
**Mood:** Somber with dark humor  
**Tempo:** 70 BPM  
**Duration:** 2:00  
**Usage:** Game over, defeat scenarios  

### 7. International Incidents
**File:** diplomatic_tension.mp3  
**Description:** Suspenseful music with world instruments  
**Mood:** Tense diplomatic atmosphere  
**Tempo:** 100 BPM  
**Duration:** 3:00  
**Usage:** International crisis cards  

### 8. Breaking News Bedlam
**File:** media_chaos.mp3  
**Description:** Fast-paced news theme with comedic breaks  
**Mood:** Frantic media frenzy  
**Tempo:** 135 BPM  
**Duration:** 2:30  
**Usage:** Media scandal events  

### 9. Market Meltdown Melody
**File:** economic_disaster.mp3  
**Description:** Descending scales representing economic collapse  
**Mood:** Ominous financial doom  
**Tempo:** 110 BPM  
**Duration:** 2:15  
**Usage:** Economic crisis events  

### 10. Rally Round the Nonsense
**File:** campaign_rally.mp3  
**Description:** Energetic campaign music with crowd sounds  
**Mood:** Populist excitement  
**Tempo:** 125 BPM  
**Duration:** 3:00  
**Usage:** Campaign events, popularity boosts  


## Implementation Example

```typescript
// In your game component
import { useState, useEffect } from 'react';

function GameMusic({ gamePhase }) {
  const [currentTrack, setCurrentTrack] = useState<HTMLAudioElement | null>(null);

  useEffect(() => {
    // Load appropriate track based on game phase
    let trackName = 'main_theme.mp3';
    
    switch(gamePhase) {
      case 'menu': trackName = 'main_theme.mp3'; break;
      case 'character_selection': trackName = 'character_selection.mp3'; break;
      case 'playing': trackName = 'gameplay_ambient.mp3'; break;
      case 'crisis': trackName = 'crisis_mode.mp3'; break;
      case 'victory': trackName = 'victory_fanfare.mp3'; break;
      case 'defeat': trackName = 'defeat_theme.mp3'; break;
    }

    const audio = new Audio(`/audio/music/${trackName}`);
    audio.loop = true;
    audio.volume = 0.5;
    audio.play().catch(e => console.log('Audio play prevented:', e));
    
    setCurrentTrack(audio);

    return () => {
      audio.pause();
      audio.src = '';
    };
  }, [gamePhase]);

  return null;
}
```

## Notes
- These are placeholder files until actual music is composed/generated
- Consider using Mubert AI or other music generation APIs
- Each track should loop seamlessly
- Implement volume controls and mute options
- Add fade transitions between tracks

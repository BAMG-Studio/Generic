# ElevenLabs Voice Generation Integration

## Overview

Executive Disorder now includes full ElevenLabs text-to-speech integration for generating high-quality voice audio for game content.

## Features

✅ **Character Voice Generation** - Each political character has a unique voice profile  
✅ **News Broadcast Audio** - Generate satirical news segments  
✅ **Event Narration** - Voice-over for game events and decisions  
✅ **Batch Processing** - Generate multiple audio files at once  
✅ **API Endpoints** - REST API for runtime voice generation  

---

## Setup

### 1. API Key Configuration

The ElevenLabs API key is already configured as a secret:
- Environment variable: `ELEVENLABS_API_KEY`
- Automatically loaded by the server

### 2. Audio Directories

Audio files are organized in:
```
client/public/audio/
├── voice/     # Generated character voices
├── music/     # Background music (manual)
└── sfx/       # Sound effects (manual)
```

---

## Character Voice Mapping

Each character has a unique ElevenLabs voice:

| Character | Voice ID | Description |
|-----------|----------|-------------|
| Ronald Goldenberg | `21m00Tcm4TlvDq8ikWAM` | Deep, confident male |
| Rex Scaleston III | `pNInz6obpgDQGcFmaJgB` | Calm, measured |
| POTUS-9000 | `TX3LPaxmHKxFdv7VOQHJ` | Robotic, precise |
| Alexandria Sanders-Warren | `EXAVITQu4vr4xnSDxMaL` | Strong, passionate female |
| Richard M. Moneybags III | `VR6AewLTigWG4xSOukaG` | Sophisticated, arrogant |
| General James Ironside Steel | `pqHfZKP75CvOlQylNhV4` | Commanding military |
| Diana Newsworthy | `jsCqWAovK2LkecY7zXl4` | Professional news anchor |
| Johnny Q. Public | `yoZ06aMxZJJ28mfd3POQ` | Everyman, relatable |
| Dr. Evelyn Technocrat | `jBpfuIE2acCO8z3wKNLl` | Analytical, scientific |
| Senator Marcus Tradition | `onwK4e9ZLuTAKqWW03F9` | Traditional, authoritative |

---

## API Endpoints

### Generate Single Voice
```bash
POST /api/audio/generate
Content-Type: application/json

{
  "text": "Your text here",
  "character": "Ronald Goldenberg",  # Optional: auto-selects voice
  "voiceId": "voice_id_here",        # Optional: manual voice selection
  "outputFilename": "custom.mp3"     # Optional: custom filename
}
```

### Batch Generate
```bash
POST /api/audio/batch-generate
Content-Type: application/json

{
  "items": [
    {
      "text": "Text 1",
      "character": "Ronald Goldenberg",
      "filename": "file1.mp3"
    },
    {
      "text": "Text 2",
      "character": "POTUS-9000",
      "filename": "file2.mp3"
    }
  ]
}
```

### Get Available Voices
```bash
GET /api/audio/voices
```

### Check Quota
```bash
GET /api/audio/quota
```

---

## Batch Generation Script

Generate all game audio at once using the batch script:

```bash
# Using tsx directly
tsx scripts/generateGameAudio.ts

# Or create a workflow in Replit
```

The script generates:
- Character introduction voice-overs
- News broadcast segments
- Game event narration
- Decision card audio

---

## Usage Examples

### Client-Side Audio Request
```typescript
// Generate voice for a character
const response = await fetch('/api/audio/generate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    text: 'This is Executive Disorder, where politics meets chaos!',
    character: 'Ronald Goldenberg'
  })
});

const data = await response.json();
// data.audioPath contains the file path, e.g., "/audio/voice/voice_123456.mp3"

// Play the audio
const audio = new Audio(data.audioPath);
audio.play();
```

### Server-Side Direct Usage
```typescript
import { elevenlabs } from './server/services/elevenlabs';

// Generate speech
const audioPath = await elevenlabs.generateSpeech({
  text: 'Political satire at its finest',
  voiceId: elevenlabs.getCharacterVoice('Diana Newsworthy'),
  outputPath: 'news_broadcast.mp3'
});
```

---

## Voice Settings

Default voice settings (customizable):
```typescript
{
  stability: 0.5,           // Voice consistency (0-1)
  similarity_boost: 0.75,   // Voice clarity (0-1)
  style: 0.5,               // Expressiveness (0-1)
  use_speaker_boost: true   // Enhanced quality
}
```

---

## Cost Management

ElevenLabs charges by character count:
- Check quota: `GET /api/audio/quota`
- Monitor usage in ElevenLabs dashboard
- Consider caching generated audio files

---

## Integration with Game

### Example: Card Decision Audio
```typescript
import { useEffect } from 'react';

function DecisionCard({ card, character }) {
  useEffect(() => {
    // Generate voice-over for the card
    fetch('/api/audio/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: card.description,
        character: character.name,
        outputFilename: `card_${card.id}.mp3`
      })
    })
    .then(res => res.json())
    .then(data => {
      const audio = new Audio(data.audioPath);
      audio.play();
    });
  }, [card, character]);

  return <div>{card.title}</div>;
}
```

---

## Troubleshooting

### API Key Not Found
- Ensure `ELEVENLABS_API_KEY` is set in Replit Secrets
- Restart the server after adding the secret

### Audio Not Generating
- Check quota: `GET /api/audio/quota`
- Verify API key has not expired
- Check server logs for error messages

### Audio Not Playing
- Ensure audio files are in `client/public/audio/voice/`
- Check file path is correct (starts with `/audio/voice/`)
- Verify browser audio permissions

---

## Next Steps

1. **Pre-generate core audio**: Run batch generation script
2. **Implement dynamic narration**: Generate audio on-the-fly for unique events
3. **Add audio caching**: Store generated audio to reduce API calls
4. **Expand voice library**: Add more satirical narration and commentary

---

## Resources

- [ElevenLabs API Docs](https://elevenlabs.io/docs)
- [Voice Library](https://elevenlabs.io/voice-library)
- [Pricing](https://elevenlabs.io/pricing)

#!/usr/bin/env tsx

/**
 * Create placeholder music files for Executive Disorder game
 * These files serve as placeholders until actual music is generated
 */

import { writeFile, mkdir } from 'fs/promises';
import { existsSync } from 'fs';
import { join } from 'path';

interface MusicTrack {
  filename: string;
  title: string;
  description: string;
  mood: string;
  tempo: string;
  duration: string;
  usage: string;
}

const musicTracks: MusicTrack[] = [
  {
    filename: 'main_theme.mp3',
    title: 'Executive Disorder Main Theme',
    description: 'Satirical orchestral piece with pompous brass and comedic undertones',
    mood: 'Grandiose yet comedic',
    tempo: '120 BPM',
    duration: '3:30',
    usage: 'Main menu, game intro'
  },
  {
    filename: 'character_selection.mp3',
    title: 'Choose Your Chaos',
    description: 'Upbeat, quirky music with political undertones',
    mood: 'Playful and satirical',
    tempo: '130 BPM',
    duration: '2:45',
    usage: 'Character selection screen'
  },
  {
    filename: 'gameplay_ambient.mp3',
    title: 'Oval Office Blues',
    description: 'Ambient background music with subtle tension',
    mood: 'Contemplative with underlying chaos',
    tempo: '90 BPM',
    duration: '5:00',
    usage: 'Main gameplay loop'
  },
  {
    filename: 'crisis_mode.mp3',
    title: 'Political Meltdown',
    description: 'Intense, fast-paced crisis music with dramatic strings',
    mood: 'Urgent and chaotic',
    tempo: '150 BPM',
    duration: '2:00',
    usage: 'Crisis events, low resources'
  },
  {
    filename: 'victory_fanfare.mp3',
    title: 'Democracy Prevails',
    description: 'Triumphant orchestral victory theme with ironic twist',
    mood: 'Celebratory with satirical edge',
    tempo: '140 BPM',
    duration: '1:30',
    usage: 'Game victory, achievements'
  },
  {
    filename: 'defeat_theme.mp3',
    title: 'Impeachment Blues',
    description: 'Melancholic yet comedic defeat music',
    mood: 'Somber with dark humor',
    tempo: '70 BPM',
    duration: '2:00',
    usage: 'Game over, defeat scenarios'
  },
  {
    filename: 'diplomatic_tension.mp3',
    title: 'International Incidents',
    description: 'Suspenseful music with world instruments',
    mood: 'Tense diplomatic atmosphere',
    tempo: '100 BPM',
    duration: '3:00',
    usage: 'International crisis cards'
  },
  {
    filename: 'media_chaos.mp3',
    title: 'Breaking News Bedlam',
    description: 'Fast-paced news theme with comedic breaks',
    mood: 'Frantic media frenzy',
    tempo: '135 BPM',
    duration: '2:30',
    usage: 'Media scandal events'
  },
  {
    filename: 'economic_disaster.mp3',
    title: 'Market Meltdown Melody',
    description: 'Descending scales representing economic collapse',
    mood: 'Ominous financial doom',
    tempo: '110 BPM',
    duration: '2:15',
    usage: 'Economic crisis events'
  },
  {
    filename: 'campaign_rally.mp3',
    title: 'Rally Round the Nonsense',
    description: 'Energetic campaign music with crowd sounds',
    mood: 'Populist excitement',
    tempo: '125 BPM',
    duration: '3:00',
    usage: 'Campaign events, popularity boosts'
  }
];

async function createMusicFiles() {
  // Create directories
  const gameAudioDir = join(process.cwd(), 'client', 'public', 'audio', 'music');
  const dropboxDir = join(process.cwd(), 'Dropbox', 'Replit', 'Audio', 'Music');

  if (!existsSync(gameAudioDir)) {
    await mkdir(gameAudioDir, { recursive: true });
  }
  if (!existsSync(dropboxDir)) {
    await mkdir(dropboxDir, { recursive: true });
  }

  console.log('🎵 Creating Executive Disorder music tracks...\n');

  // Create metadata JSON
  const metadata = {
    created: new Date().toISOString(),
    game: 'Executive Disorder',
    totalTracks: musicTracks.length,
    tracks: musicTracks,
    note: 'These are placeholder files with metadata. Actual audio generation pending.'
  };

  // Save metadata
  await writeFile(
    join(gameAudioDir, 'music_metadata.json'),
    JSON.stringify(metadata, null, 2)
  );
  await writeFile(
    join(dropboxDir, 'music_metadata.json'),
    JSON.stringify(metadata, null, 2)
  );

  // Create placeholder MP3 files
  // MP3 file header (minimal valid MP3)
  const mp3Header = Buffer.from([
    0xFF, 0xFB, 0x90, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
  ]);

  for (const track of musicTracks) {
    // Create placeholder MP3 files
    const gameFilePath = join(gameAudioDir, track.filename);
    const dropboxFilePath = join(dropboxDir, track.filename);

    await writeFile(gameFilePath, mp3Header);
    await writeFile(dropboxFilePath, mp3Header);

    console.log(`✅ Created: ${track.filename}`);
    console.log(`   📝 ${track.title} - ${track.description}`);
    console.log(`   🎭 Mood: ${track.mood} | Tempo: ${track.tempo}`);
    console.log(`   📍 Usage: ${track.usage}\n`);
  }

  console.log('🎉 Successfully created', musicTracks.length, 'music track placeholders');
  console.log('📁 Game location:', gameAudioDir);
  console.log('💾 Backup location:', dropboxDir);

  // Create usage documentation
  const usageDoc = `# Executive Disorder - Music Track Usage Guide

## Track List (${musicTracks.length} Tracks)

${musicTracks.map((track, i) => `### ${i + 1}. ${track.title}
**File:** ${track.filename}  
**Description:** ${track.description}  
**Mood:** ${track.mood}  
**Tempo:** ${track.tempo}  
**Duration:** ${track.duration}  
**Usage:** ${track.usage}  
`).join('\n')}

## Implementation Example

\`\`\`typescript
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

    const audio = new Audio(\`/audio/music/\${trackName}\`);
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
\`\`\`

## Notes
- These are placeholder files until actual music is composed/generated
- Consider using Mubert AI or other music generation APIs
- Each track should loop seamlessly
- Implement volume controls and mute options
- Add fade transitions between tracks
`;

  await writeFile(join(gameAudioDir, 'MUSIC_USAGE.md'), usageDoc);
  await writeFile(join(dropboxDir, 'MUSIC_USAGE.md'), usageDoc);

  console.log('\n📚 Created usage documentation');
}

// Run the script
createMusicFiles().catch(console.error);
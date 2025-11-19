#!/usr/bin/env tsx

/**
 * Generate real playable audio using FFmpeg
 * More stable than SoX for procedural audio generation
 */

import { execSync } from 'child_process';
import { mkdirSync, existsSync } from 'fs';
import { join } from 'path';

function hasFFmpeg(): boolean {
  try {
    execSync('which ffmpeg', { stdio: 'ignore' });
    return true;
  } catch {
    return false;
  }
}

interface AudioSpec {
  filename: string;
  directory: string;
  description: string;
  duration: number;
  frequency: string; // Can be single freq or complex expression
  type: 'sine' | 'square' | 'triangle';
}

const audioSpecs: AudioSpec[] = [
  // Essential SFX
  {
    filename: 'success.mp3',
    directory: 'client/public/sounds',
    description: 'Success chime - pleasant confirmation',
    duration: 0.5,
    frequency: '800+1000',
    type: 'sine'
  },
  {
    filename: 'hit.mp3',
    directory: 'client/public/sounds',
    description: 'Hit sound - negative feedback',
    duration: 0.3,
    frequency: '200',
    type: 'square'
  },
  {
    filename: 'background.mp3',
    directory: 'client/public/sounds',
    description: 'Background ambient loop',
    duration: 15,
    frequency: '440+550',
    type: 'sine'
  },
  
  // Music tracks
  {
    filename: 'main_theme.mp3',
    directory: 'client/public/audio/music',
    description: 'Main theme - grandiose intro',
    duration: 20,
    frequency: '523+659',
    type: 'sine'
  },
  {
    filename: 'character_selection.mp3',
    directory: 'client/public/audio/music',
    description: 'Character selection - upbeat',
    duration: 15,
    frequency: '659+784',
    type: 'triangle'
  },
  {
    filename: 'gameplay_ambient.mp3',
    directory: 'client/public/audio/music',
    description: 'Gameplay ambient - subtle',
    duration: 25,
    frequency: '220+330',
    type: 'sine'
  },
  {
    filename: 'crisis_mode.mp3',
    directory: 'client/public/audio/music',
    description: 'Crisis mode - intense',
    duration: 10,
    frequency: '440+587',
    type: 'square'
  },
  {
    filename: 'victory_fanfare.mp3',
    directory: 'client/public/audio/music',
    description: 'Victory fanfare',
    duration: 6,
    frequency: '784+988',
    type: 'sine'
  },
  {
    filename: 'defeat_theme.mp3',
    directory: 'client/public/audio/music',
    description: 'Defeat theme - melancholic',
    duration: 8,
    frequency: '294+247',
    type: 'sine'
  },
  {
    filename: 'diplomatic_tension.mp3',
    directory: 'client/public/audio/music',
    description: 'Diplomatic tension',
    duration: 12,
    frequency: '330+440',
    type: 'sine'
  },
  {
    filename: 'media_chaos.mp3',
    directory: 'client/public/audio/music',
    description: 'Media chaos - frantic',
    duration: 10,
    frequency: '880+1047',
    type: 'triangle'
  },
  {
    filename: 'economic_disaster.mp3',
    directory: 'client/public/audio/music',
    description: 'Economic disaster - ominous',
    duration: 9,
    frequency: '392+330',
    type: 'sine'
  },
  {
    filename: 'campaign_rally.mp3',
    directory: 'client/public/audio/music',
    description: 'Campaign rally - energetic',
    duration: 12,
    frequency: '523+659',
    type: 'triangle'
  }
];

async function generateAudioWithFFmpeg() {
  console.log('🎵 Executive Disorder - FFmpeg Audio Generation\n');
  
  if (!hasFFmpeg()) {
    console.log('📦 Installing FFmpeg...');
    try {
      execSync('nix-env -iA nixpkgs.ffmpeg', { stdio: 'inherit' });
      console.log('✅ FFmpeg installed!\n');
    } catch (error) {
      console.error('❌ Failed to install FFmpeg');
      return;
    }
  }

  let generated = 0;
  let failed = 0;

  for (const spec of audioSpecs) {
    try {
      if (!existsSync(spec.directory)) {
        mkdirSync(spec.directory, { recursive: true });
      }

      const outputPath = join(spec.directory, spec.filename);
      
      console.log(`🎼 ${spec.filename}`);
      console.log(`   ${spec.description}`);
      
      // Generate simple tone using FFmpeg
      const cmd = `ffmpeg -f lavfi -i "sine=frequency=${spec.frequency}:duration=${spec.duration}" ` +
                  `-af "volume=0.3" -y "${outputPath}" 2>/dev/null`;
      
      execSync(cmd, { stdio: 'pipe' });
      
      console.log(`   ✅ Created\n`);
      generated++;
      
    } catch (error: any) {
      console.error(`   ❌ Failed\n`);
      failed++;
    }
  }

  console.log('='.repeat(60));
  console.log(`✅ Generated: ${generated}/${audioSpecs.length} files`);
  if (failed > 0) console.log(`❌ Failed: ${failed} files`);
  console.log('='.repeat(60));
  
  console.log('\n🎉 Audio generation complete!');
}

generateAudioWithFFmpeg().catch(console.error);
import { writeFile, mkdir } from 'fs/promises';
import { existsSync } from 'fs';
import { join, basename, normalize } from 'path';

interface VoiceSettings {
  stability: number;
  similarity_boost: number;
  style?: number;
  use_speaker_boost?: boolean;
}

interface GenerateVoiceOptions {
  text: string;
  voiceId?: string;
  modelId?: string;
  voiceSettings?: VoiceSettings;
  outputPath?: string;
}

export class ElevenLabsService {
  private apiKey: string;
  private baseUrl = 'https://api.elevenlabs.io/v1';

  constructor() {
    this.apiKey = process.env.ELEVENLABS_API_KEY || '';
    if (!this.apiKey) {
      console.warn('⚠️ ELEVENLABS_API_KEY not found in environment variables');
    }
  }

  /**
   * Generate speech from text using ElevenLabs API
   */
  async generateSpeech(options: GenerateVoiceOptions): Promise<string> {
    const {
      text,
      voiceId = 'EXAVITQu4vr4xnSDxMaL', // Default: Sarah (Professional Female)
      modelId = 'eleven_multilingual_v2',
      voiceSettings = {
        stability: 0.5,
        similarity_boost: 0.75,
        style: 0.5,
        use_speaker_boost: true
      },
      outputPath
    } = options;

    if (!this.apiKey) {
      throw new Error('ElevenLabs API key not configured');
    }

    const url = `${this.baseUrl}/text-to-speech/${voiceId}`;

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Accept': 'audio/mpeg',
          'xi-api-key': this.apiKey,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text,
          model_id: modelId,
          voice_settings: voiceSettings
        })
      });

      if (!response.ok) {
        const error = await response.text();
        throw new Error(`ElevenLabs API error: ${response.status} - ${error}`);
      }

      // Get audio data as buffer
      const audioBuffer = Buffer.from(await response.arrayBuffer());

      // Determine output path with security validation
      const audioDir = join(process.cwd(), 'client', 'public', 'audio', 'voice');
      if (!existsSync(audioDir)) {
        await mkdir(audioDir, { recursive: true });
      }

      // SECURITY: Sanitize filename to prevent path traversal
      let sanitizedFilename: string;
      if (outputPath) {
        // Extract only the filename, strip any path components
        const baseName = basename(outputPath);
        // Remove any potentially dangerous characters
        sanitizedFilename = baseName.replace(/[^a-zA-Z0-9_\-\.]/g, '_');
        // Ensure .mp3 extension
        if (!sanitizedFilename.endsWith('.mp3')) {
          sanitizedFilename = sanitizedFilename.replace(/\.[^.]*$/, '') + '.mp3';
        }
      } else {
        sanitizedFilename = `voice_${Date.now()}.mp3`;
      }

      const fullPath = join(audioDir, sanitizedFilename);
      
      // SECURITY: Verify the resolved path is still within audioDir
      const normalizedFullPath = normalize(fullPath);
      const normalizedAudioDir = normalize(audioDir);
      if (!normalizedFullPath.startsWith(normalizedAudioDir)) {
        throw new Error('Invalid file path: path traversal detected');
      }

      // Save audio file
      await writeFile(fullPath, audioBuffer);

      console.log(`✅ Generated voice audio: ${sanitizedFilename}`);
      return `/audio/voice/${sanitizedFilename}`;
    } catch (error) {
      console.error('❌ ElevenLabs generation failed:', error);
      throw error;
    }
  }

  /**
   * Get available voices from ElevenLabs
   */
  async getVoices(): Promise<any[]> {
    if (!this.apiKey) {
      throw new Error('ElevenLabs API key not configured');
    }

    try {
      const response = await fetch(`${this.baseUrl}/voices`, {
        headers: {
          'xi-api-key': this.apiKey
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch voices: ${response.status}`);
      }

      const data = await response.json();
      return data.voices || [];
    } catch (error) {
      console.error('❌ Failed to fetch voices:', error);
      throw error;
    }
  }

  /**
   * Get user info and quota from ElevenLabs
   */
  async getUserInfo(): Promise<any> {
    if (!this.apiKey) {
      throw new Error('ElevenLabs API key not configured');
    }

    try {
      const response = await fetch(`${this.baseUrl}/user`, {
        headers: {
          'xi-api-key': this.apiKey
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch user info: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('❌ Failed to fetch user info:', error);
      throw error;
    }
  }

  /**
   * Preset voices for game characters
   */
  getCharacterVoice(characterName: string): string {
    const voiceMap: Record<string, string> = {
      'Ronald Goldenberg': '21m00Tcm4TlvDq8ikWAM', // Deep, confident male voice (Rachel)
      'Rex Scaleston III': 'pNInz6obpgDQGcFmaJgB', // Calm, measured voice (Adam)
      'POTUS-9000': 'TX3LPaxmHKxFdv7VOQHJ', // Robotic, precise voice (Elli)
      'Alexandria Sanders-Warren': 'EXAVITQu4vr4xnSDxMaL', // Strong, passionate female voice (Sarah)
      'Richard M. Moneybags III': 'VR6AewLTigWG4xSOukaG', // Sophisticated, arrogant voice (Arnold)
      'General James Ironside Steel': 'pqHfZKP75CvOlQylNhV4', // Commanding military voice (Bill)
      'Diana Newsworthy': 'jsCqWAovK2LkecY7zXl4', // Professional news anchor voice (Freya)
      'Johnny Q. Public': 'yoZ06aMxZJJ28mfd3POQ', // Everyman, relatable voice (Sam)
      'Dr. Evelyn Technocrat': 'jBpfuIE2acCO8z3wKNLl', // Analytical, scientific voice (Gigi)
      'Senator Marcus Tradition': 'onwK4e9ZLuTAKqWW03F9', // Traditional, authoritative voice (Daniel)
    };

    return voiceMap[characterName] || voiceMap['Johnny Q. Public']; // Default to everyman voice
  }
}

// Export singleton instance
export const elevenlabs = new ElevenLabsService();

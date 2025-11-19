import { Router, Request, Response } from 'express';
import { elevenlabs } from '../services/elevenlabs';

const router = Router();

/**
 * POST /api/audio/generate
 * Generate speech from text using ElevenLabs
 */
router.post('/generate', async (req: Request, res: Response) => {
  try {
    const { text, character, voiceId, outputFilename } = req.body;

    // Input validation
    if (!text || typeof text !== 'string') {
      return res.status(400).json({ error: 'Valid text string is required' });
    }

    if (text.length > 5000) {
      return res.status(400).json({ error: 'Text exceeds maximum length of 5000 characters' });
    }

    // SECURITY: Validate filename if provided
    if (outputFilename && typeof outputFilename === 'string') {
      // Only allow alphanumeric, dash, underscore, and .mp3 extension
      const filenamePattern = /^[a-zA-Z0-9_\-]+\.mp3$/;
      if (!filenamePattern.test(outputFilename)) {
        return res.status(400).json({ 
          error: 'Invalid filename. Use only letters, numbers, dash, underscore, and .mp3 extension' 
        });
      }
    }

    // Get voice ID for character if specified
    const selectedVoiceId = character 
      ? elevenlabs.getCharacterVoice(character)
      : voiceId;

    const audioPath = await elevenlabs.generateSpeech({
      text,
      voiceId: selectedVoiceId,
      outputPath: outputFilename
    });

    res.json({
      success: true,
      audioPath,
      message: 'Voice generated successfully'
    });
  } catch (error: any) {
    console.error('Voice generation error:', error);
    res.status(500).json({ 
      error: 'Failed to generate voice',
      details: error.message 
    });
  }
});

/**
 * GET /api/audio/voices
 * Get available voices from ElevenLabs
 */
router.get('/voices', async (req: Request, res: Response) => {
  try {
    const voices = await elevenlabs.getVoices();
    res.json({ voices });
  } catch (error: any) {
    res.status(500).json({ 
      error: 'Failed to fetch voices',
      details: error.message 
    });
  }
});

/**
 * GET /api/audio/quota
 * Get user quota information
 */
router.get('/quota', async (req: Request, res: Response) => {
  try {
    const userInfo = await elevenlabs.getUserInfo();
    res.json({
      characterCount: userInfo.subscription?.character_count || 0,
      characterLimit: userInfo.subscription?.character_limit || 0,
      canUseApi: userInfo.subscription?.can_use_api || false
    });
  } catch (error: any) {
    res.status(500).json({ 
      error: 'Failed to fetch quota',
      details: error.message 
    });
  }
});

/**
 * POST /api/audio/batch-generate
 * Generate multiple audio files for game content
 */
router.post('/batch-generate', async (req: Request, res: Response) => {
  try {
    const { items } = req.body; // Array of { text, character, filename }

    if (!Array.isArray(items) || items.length === 0) {
      return res.status(400).json({ error: 'Items array is required' });
    }

    if (items.length > 50) {
      return res.status(400).json({ error: 'Maximum 50 items per batch request' });
    }

    const results = [];
    const filenamePattern = /^[a-zA-Z0-9_\-]+\.mp3$/;

    for (const item of items) {
      try {
        // Validate each item
        if (!item.text || typeof item.text !== 'string') {
          results.push({
            success: false,
            filename: item.filename,
            error: 'Invalid or missing text'
          });
          continue;
        }

        if (item.text.length > 5000) {
          results.push({
            success: false,
            filename: item.filename,
            error: 'Text exceeds maximum length'
          });
          continue;
        }

        // SECURITY: Validate filename
        if (item.filename && !filenamePattern.test(item.filename)) {
          results.push({
            success: false,
            filename: item.filename,
            error: 'Invalid filename format'
          });
          continue;
        }

        const voiceId = item.character 
          ? elevenlabs.getCharacterVoice(item.character)
          : item.voiceId;

        const audioPath = await elevenlabs.generateSpeech({
          text: item.text,
          voiceId,
          outputPath: item.filename
        });

        results.push({
          success: true,
          filename: item.filename,
          audioPath,
          text: item.text.substring(0, 50) + '...'
        });
      } catch (error: any) {
        results.push({
          success: false,
          filename: item.filename,
          error: error.message
        });
      }
    }

    res.json({
      success: true,
      results,
      total: results.length,
      successful: results.filter(r => r.success).length
    });
  } catch (error: any) {
    res.status(500).json({ 
      error: 'Batch generation failed',
      details: error.message 
    });
  }
});

export default router;

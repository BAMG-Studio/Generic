import { Router } from "express";
import { getDropboxClient } from "../lib/dropbox";

const router = Router();

// Cache for loaded cards to avoid repeated Dropbox requests
let cardsCache: any[] | null = null;
let cacheTimestamp = 0;
const CACHE_DURATION = 10 * 60 * 1000; // 10 minutes

// List files in a Dropbox folder
router.get("/list/:path(*)", async (req, res) => {
  try {
    const dbx = await getDropboxClient();
    const path = req.params.path ? `/${req.params.path}` : '';
    
    const response = await dbx.filesListFolder({ path });
    res.json(response.result);
  } catch (error: any) {
    console.error('Dropbox list error:', error);
    res.status(500).json({ error: error.message });
  }
});

// Get a temporary link to a Dropbox file
router.get("/link/:path(*)", async (req, res) => {
  try {
    const dbx = await getDropboxClient();
    const path = `/${req.params.path}`;
    
    const response = await dbx.filesGetTemporaryLink({ path });
    res.json({ link: response.result.link });
  } catch (error: any) {
    console.error('Dropbox link error:', error);
    res.status(500).json({ error: error.message });
  }
});

// Download a file from Dropbox
router.get("/download/:path(*)", async (req, res) => {
  try {
    const dbx = await getDropboxClient();
    const path = `/${req.params.path}`;
    
    const response = await dbx.filesDownload({ path });
    const fileBlob = (response.result as any).fileBinary;
    
    res.setHeader('Content-Type', 'application/octet-stream');
    res.send(fileBlob);
  } catch (error: any) {
    console.error('Dropbox download error:', error);
    res.status(500).json({ error: error.message });
  }
});

// Serve image from Dropbox
router.get("/image/:path(*)", async (req, res) => {
  try {
    const dbx = await getDropboxClient();
    const path = `/${req.params.path}`;
    
    const response = await dbx.filesDownload({ path });
    const fileBlob = (response.result as any).fileBinary;
    
    // Determine content type from file extension
    const ext = path.split('.').pop()?.toLowerCase();
    const contentType = ext === 'png' ? 'image/png' : 
                       ext === 'jpg' || ext === 'jpeg' ? 'image/jpeg' :
                       ext === 'gif' ? 'image/gif' :
                       ext === 'webp' ? 'image/webp' : 'image/png';
    
    res.setHeader('Content-Type', contentType);
    res.setHeader('Cache-Control', 'public, max-age=3600');
    res.send(fileBlob);
  } catch (error: any) {
    console.error('Dropbox image error:', error);
    // Return a 1x1 transparent PNG on error
    const transparentPng = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==', 'base64');
    res.setHeader('Content-Type', 'image/png');
    res.send(transparentPng);
  }
});

// Get JSON data from Dropbox
router.get("/json/:path(*)", async (req, res) => {
  try {
    const dbx = await getDropboxClient();
    const path = `/${req.params.path}`;
    
    const response = await dbx.filesDownload({ path });
    const fileBlob = (response.result as any).fileBinary;
    
    // Convert ArrayBuffer/Buffer to string properly
    let textContent: string;
    if (Buffer.isBuffer(fileBlob)) {
      textContent = fileBlob.toString('utf8');
    } else if (fileBlob instanceof ArrayBuffer) {
      textContent = Buffer.from(fileBlob).toString('utf8');
    } else {
      textContent = String(fileBlob);
    }
    
    // Parse JSON and return
    const jsonData = JSON.parse(textContent);
    
    res.setHeader('Content-Type', 'application/json');
    res.setHeader('Cache-Control', 'public, max-age=300'); // 5 minutes cache
    res.json(jsonData);
  } catch (error: any) {
    console.error('Dropbox JSON error:', error);
    res.status(404).json({ error: 'JSON file not found', message: error.message });
  }
});

// Load all cards from Dropbox and convert to game format
router.get("/cards/all", async (req, res) => {
  try {
    // Check cache first
    const now = Date.now();
    if (cardsCache && (now - cacheTimestamp < CACHE_DURATION)) {
      console.log(`✅ Serving ${cardsCache.length} cards from cache`);
      res.setHeader('Content-Type', 'application/json');
      res.setHeader('Cache-Control', 'public, max-age=300');
      return res.json(cardsCache);
    }
    
    const dbx = await getDropboxClient();
    const cardsPath = '/Replit/ExecutiveDisorder_Assets/10_Game_Data/JSON/cards';
    
    // List all card files
    const listResponse = await dbx.filesListFolder({ path: cardsPath });
    const cardFiles = listResponse.result.entries.filter(entry => 
      entry['.tag'] === 'file' && entry.name.endsWith('.json')
    );
    
    console.log(`Found ${cardFiles.length} card files in Dropbox, converting...`);
    
    // Download and convert each card
    const gameCards = [];
    for (const file of cardFiles) {
      try {
        const filePath = (file as any).path_lower || (file as any).path_display;
        if (!filePath) continue;
        
        const downloadResponse = await dbx.filesDownload({ path: filePath });
        const fileBlob = (downloadResponse.result as any).fileBinary;
        
        let textContent: string;
        if (Buffer.isBuffer(fileBlob)) {
          textContent = fileBlob.toString('utf8');
        } else if (fileBlob instanceof ArrayBuffer) {
          textContent = Buffer.from(fileBlob).toString('utf8');
        } else {
          textContent = String(fileBlob);
        }
        
        const dropboxCard = JSON.parse(textContent);
        
        // Map theme to category
        const themeToCategory: Record<string, string> = {
          'economic_crisis': 'economic',
          'budget_crisis': 'economic',
          'trade_war': 'foreign',
          'diplomatic_disaster': 'foreign',
          'constitutional_crisis': 'domestic',
          'bureaucratic_nightmare': 'domestic',
          'legislative_chaos': 'domestic',
          'social_media': 'social',
          'culture_war': 'social',
          'nuclear_option': 'crisis',
          'war_games': 'crisis',
          'space_force_shenanigans': 'crisis',
          'military_industrial_complex': 'foreign'
        };
        
        const category = themeToCategory[dropboxCard.theme] || 'domestic';
        
        // Convert to game card format with safe defaults
        const choices = dropboxCard.choices || dropboxCard.options || [];
        
        // Build game card with optional image URL
        const gameCard: any = {
          id: dropboxCard.id || file.name.replace('.json', ''),
          title: dropboxCard.title || 'Untitled Decision',
          description: dropboxCard.description || 'A critical decision awaits...',
          category: category,
          options: choices.map((choice: any) => {
            // Handle different field name variations
            const choiceText = choice.text || choice.choiceText || 'Make a choice';
            const actionText = choice.actionText || choice.action || choice.buttonText || undefined;
            const effects = choice.effects || choice.resourceEffects || {};
            
            return {
              text: choiceText,
              actionText: actionText, // Optional satirical action button text
              effects: {
                popularity: effects.Popularity || effects.popularity || 0,
                stability: effects.Stability || effects.stability || 0,
                media: effects.MediaTrust || effects.media || 0,
                economy: effects.EconomicHealth || effects.economy || 0
              }
            };
          }).filter((opt: any) => opt && opt.text) // Remove any invalid options
        };
        
        // Add image URL if available from various possible fields
        if (dropboxCard.imageUrl || dropboxCard.image || dropboxCard.media || dropboxCard.cardImage) {
          gameCard.imageUrl = dropboxCard.imageUrl || dropboxCard.image || dropboxCard.media || dropboxCard.cardImage;
        }
        
        // VALIDATION: Only add cards with at least 2 valid options
        if (gameCard.options && gameCard.options.length >= 2) {
          gameCards.push(gameCard);
        } else {
          console.warn(`⚠️ Skipping invalid card "${gameCard.title}" - needs at least 2 options, has ${gameCard.options?.length || 0}`);
        }
      } catch (error) {
        console.error(`Error processing card ${file.name}:`, error);
      }
    }
    
    console.log(`✅ Successfully converted ${gameCards.length} cards`);
    
    // Cache the results
    cardsCache = gameCards;
    cacheTimestamp = Date.now();
    
    res.setHeader('Content-Type', 'application/json');
    res.setHeader('Cache-Control', 'public, max-age=300');
    res.json(gameCards);
  } catch (error: any) {
    console.error('❌ Error loading cards from Dropbox:', error);
    res.status(500).json({ error: 'Failed to load cards', message: error.message });
  }
});

// Update a card file with new data (for adding actionText)
router.post("/cards/update/:filename", async (req, res) => {
  try {
    const dbx = await getDropboxClient();
    const filename = req.params.filename;
    const cardData = req.body;
    
    const cardsPath = '/Replit/ExecutiveDisorder_Assets/10_Game_Data/JSON/cards';
    const filePath = `${cardsPath}/${filename}`;
    
    // Convert card data to JSON string
    const jsonContent = JSON.stringify(cardData, null, 2);
    
    // Upload the updated file (overwrite mode)
    await dbx.filesUpload({
      path: filePath,
      contents: jsonContent,
      mode: { '.tag': 'overwrite' }
    });
    
    // Clear cache to force reload
    cardsCache = null;
    
    console.log(`✅ Updated card file: ${filename}`);
    res.json({ success: true, filename });
  } catch (error: any) {
    console.error('❌ Error updating card:', error);
    res.status(500).json({ error: 'Failed to update card', message: error.message });
  }
});

// Batch update all cards with actionText
router.post("/cards/batch-update-actiontext", async (req, res) => {
  try {
    const dbx = await getDropboxClient();
    const cardsPath = '/Replit/ExecutiveDisorder_Assets/10_Game_Data/JSON/cards';
    
    // List all card files
    const listResponse = await dbx.filesListFolder({ path: cardsPath });
    const cardFiles = listResponse.result.entries.filter(entry => 
      entry['.tag'] === 'file' && entry.name.endsWith('.json')
    );
    
    console.log(`Processing ${cardFiles.length} cards for actionText update...`);
    
    let updatedCount = 0;
    
    for (const file of cardFiles) {
      try {
        const filePath = (file as any).path_lower || (file as any).path_display;
        if (!filePath) continue;
        
        // Download card
        const downloadResponse = await dbx.filesDownload({ path: filePath });
        const fileBlob = (downloadResponse.result as any).fileBinary;
        
        let textContent: string;
        if (Buffer.isBuffer(fileBlob)) {
          textContent = fileBlob.toString('utf8');
        } else if (fileBlob instanceof ArrayBuffer) {
          textContent = Buffer.from(fileBlob).toString('utf8');
        } else {
          textContent = String(fileBlob);
        }
        
        const cardData = JSON.parse(textContent);
        
        // Check if card already has actionText
        const choices = cardData.choices || cardData.options || [];
        const hasActionText = choices.some((c: any) => c.actionText || c.action || c.buttonText);
        
        if (hasActionText) {
          console.log(`⏭️ Skipping ${file.name} - already has actionText`);
          continue;
        }
        
        // Generate actionText based on scenario
        const updatedChoices = choices.map((choice: any, index: number) => {
          const actionText = generateActionText(cardData, choice, index);
          return {
            ...choice,
            actionText
          };
        });
        
        cardData.choices = updatedChoices;
        if (cardData.options) cardData.options = updatedChoices;
        
        // Upload updated card
        const jsonContent = JSON.stringify(cardData, null, 2);
        await dbx.filesUpload({
          path: filePath,
          contents: jsonContent,
          mode: { '.tag': 'overwrite' }
        });
        
        updatedCount++;
        console.log(`✅ Updated ${file.name} with actionText`);
        
      } catch (error) {
        console.error(`❌ Error processing ${file.name}:`, error);
      }
    }
    
    // Clear cache
    cardsCache = null;
    
    console.log(`🎉 Batch update complete: ${updatedCount}/${cardFiles.length} cards updated`);
    res.json({ success: true, updated: updatedCount, total: cardFiles.length });
    
  } catch (error: any) {
    console.error('❌ Batch update error:', error);
    res.status(500).json({ error: 'Batch update failed', message: error.message });
  }
});

// Helper function to generate satirical actionText based on scenario
function generateActionText(card: any, choice: any, index: number): string {
  const title = (card.title || '').toLowerCase();
  const desc = (card.description || '').toLowerCase();
  const choiceText = (choice.text || choice.choiceText || '').toLowerCase();
  const theme = (card.theme || '').toLowerCase();
  
  // Context-aware satirical button text
  if (choiceText.includes('blame') || choiceText.includes('fault')) return 'BLAME IT';
  if (choiceText.includes('deny') || choiceText.includes('ignore')) return 'DENY IT';
  if (choiceText.includes('fire') || choiceText.includes('dismiss')) return 'FIRE';
  if (choiceText.includes('hire') || choiceText.includes('appoint')) return 'HIRE';
  if (choiceText.includes('promote')) return 'PROMOTE';
  if (choiceText.includes('veto') || choiceText.includes('reject')) return 'VETO';
  if (choiceText.includes('sign') || choiceText.includes('approve')) return 'APPROVE';
  if (choiceText.includes('tweet') || choiceText.includes('post')) return 'TWEET IT';
  if (choiceText.includes('investigate')) return 'INVESTIGATE';
  if (choiceText.includes('pardon') || choiceText.includes('forgive')) return 'PARDON';
  if (choiceText.includes('sanction') || choiceText.includes('punish')) return 'SANCTION';
  if (choiceText.includes('negotiate') || choiceText.includes('deal')) return 'NEGOTIATE';
  if (choiceText.includes('declare') || choiceText.includes('announce')) return 'DECLARE';
  if (choiceText.includes('ban') || choiceText.includes('forbid')) return 'BAN IT';
  if (choiceText.includes('tax')) return 'TAX IT';
  if (choiceText.includes('cut') || choiceText.includes('reduce')) return 'CUT IT';
  if (choiceText.includes('increase') || choiceText.includes('raise')) return 'RAISE IT';
  if (choiceText.includes('cancel') || choiceText.includes('end')) return 'CANCEL';
  if (choiceText.includes('expand') || choiceText.includes('grow')) return 'EXPAND';
  if (choiceText.includes('attack') || choiceText.includes('strike')) return 'STRIKE';
  if (choiceText.includes('retreat') || choiceText.includes('withdraw')) return 'RETREAT';
  if (choiceText.includes('spin') || choiceText.includes('propaganda')) return 'SPIN IT';
  if (choiceText.includes('cover') || choiceText.includes('hide')) return 'COVER UP';
  if (choiceText.includes('leak') || choiceText.includes('reveal')) return 'LEAK IT';
  if (choiceText.includes('bribe') || choiceText.includes('pay')) return 'PAY OFF';
  if (choiceText.includes('threaten')) return 'THREATEN';
  if (choiceText.includes('compromise')) return 'COMPROMISE';
  if (choiceText.includes('double down') || choiceText.includes('commit')) return 'DOUBLE DOWN';
  if (choiceText.includes('flip') || choiceText.includes('reverse')) return 'FLIP-FLOP';
  
  // Theme-based defaults
  if (theme.includes('economic') || theme.includes('budget')) {
    return index === 0 ? 'SPEND' : 'SAVE';
  }
  if (theme.includes('war') || theme.includes('military') || theme.includes('nuclear')) {
    return index === 0 ? 'ATTACK' : 'DEFEND';
  }
  if (theme.includes('social') || theme.includes('culture')) {
    return index === 0 ? 'SUPPORT' : 'OPPOSE';
  }
  if (theme.includes('diplomatic') || theme.includes('foreign')) {
    return index === 0 ? 'ALLY' : 'ENEMY';
  }
  
  // Generic fallbacks
  const genericActions = ['DO IT', 'PASS', 'BLOCK', 'ACT NOW', 'WAIT', 'GO BIG', 'PLAY SAFE'];
  return genericActions[index % genericActions.length];
}

export default router;

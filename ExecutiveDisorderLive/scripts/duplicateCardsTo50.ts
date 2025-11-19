import * as fs from 'fs';
import * as path from 'path';

// Script to create 50 cards per character by duplicating templates

const characters = [
  'Rex-Scaleston',
  'Ronald-Goldenberg',
  'POTUS-9000',
  'Alexandria-Sanders-Warren',
  'Richard-Moneybags',
  'General-Steel',
  'Diana-Newsworthy',
  'Johnny-Q-Public',
  'Dr-Evelyn-Technocrat',
  'Senator-Marcus-Tradition'
];

const baseDir = '../Dropbox/Replit/ExecutiveDisorder_Assets/01_Characters/Character_Cards';

function duplicateCardsTo50(characterFolder: string) {
  const charPath = path.join(baseDir, characterFolder);
  
  // Get existing card templates
  const existingCards = fs.readdirSync(charPath).filter(f => f.endsWith('.png'));
  
  if (existingCards.length === 0) {
    console.log(`⚠️  No cards found for ${characterFolder}`);
    return;
  }
  
  console.log(`📁 Processing ${characterFolder}: ${existingCards.length} template(s) found`);
  
  // Create 50 cards by cycling through templates
  for (let i = 1; i <= 50; i++) {
    const targetFile = path.join(charPath, `card-${String(i).padStart(2, '0')}.png`);
    
    // Skip if file already exists and has content
    if (fs.existsSync(targetFile)) {
      continue;
    }
    
    // Use template in round-robin fashion
    const templateIndex = (i - 1) % existingCards.length;
    const sourceFile = path.join(charPath, existingCards[templateIndex]);
    
    // Copy template to new numbered card
    fs.copyFileSync(sourceFile, targetFile);
  }
  
  const finalCount = fs.readdirSync(charPath).filter(f => f.endsWith('.png')).length;
  console.log(`✅ ${characterFolder}: ${finalCount} cards total`);
}

// Process all characters
console.log('🚀 Creating 50 cards per character...\n');

characters.forEach(char => {
  duplicateCardsTo50(char);
});

console.log('\n📊 Card generation complete!');
console.log(`Total characters: ${characters.length}`);
console.log(`Expected total cards: ${characters.length * 50} (50 per character)`);

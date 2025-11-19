import * as fs from 'fs';
import * as path from 'path';

const baseDir = '../Dropbox/Replit/ExecutiveDisorder_Assets/01_Characters/Expressions';

const characters = [
  'alexandria_warren',
  'diana_newsworthy',
  'evelyn_technocrat',
  'james_steel',
  'johnny_public',
  'marcus_tradition',
  'potus9000',
  'rex_scaleston',
  'richard_moneybags',
  'ronald_goldenberg'
];

const expressions = [
  'laughing',
  'crying',
  'confused',
  'smirking',
  'thinking',
  'disgusted',
  'shocked',
  'proud',
  'exhausted',
  'nervous'
];

for (const char of characters) {
  const charDir = path.join(baseDir, char);
  
  console.log(`\n📁 Processing ${char}...`);
  
  for (let i = 1; i <= 50; i++) {
    const expressionIndex = (i - 1) % expressions.length;
    const expression = expressions[expressionIndex];
    const sourceFile = path.join(charDir, `${expression}.png`);
    const targetFile = path.join(charDir, `expression-${String(i).padStart(2, '0')}.png`);
    
    if (fs.existsSync(sourceFile)) {
      fs.copyFileSync(sourceFile, targetFile);
    }
  }
  
  const count = fs.readdirSync(charDir).filter(f => f.startsWith('expression-')).length;
  console.log(`✅ ${char}: ${count} expression files created`);
}

console.log(`\n🎉 Expression duplication complete!`);
console.log(`📊 Total: ${characters.length * 50} expression files ready`);

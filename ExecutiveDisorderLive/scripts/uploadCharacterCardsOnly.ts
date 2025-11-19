import { Dropbox } from 'dropbox';
import * as fs from 'fs';
import * as path from 'path';

let connectionSettings: any;

async function getAccessToken() {
  if (connectionSettings && connectionSettings.settings.expires_at && new Date(connectionSettings.settings.expires_at).getTime() > Date.now()) {
    return connectionSettings.settings.access_token;
  }
  
  const hostname = process.env.REPLIT_CONNECTORS_HOSTNAME
  const xReplitToken = process.env.REPL_IDENTITY 
    ? 'repl ' + process.env.REPL_IDENTITY 
    : process.env.WEB_REPL_RENEWAL 
    ? 'depl ' + process.env.WEB_REPL_RENEWAL 
    : null;

  if (!xReplitToken) {
    throw new Error('X_REPLIT_TOKEN not found');
  }

  connectionSettings = await fetch(
    'https://' + hostname + '/api/v2/connection?include_secrets=true&connector_names=dropbox',
    {
      headers: {
        'Accept': 'application/json',
        'X_REPLIT_TOKEN': xReplitToken
      }
    }
  ).then(res => res.json()).then(data => data.items?.[0]);

  const accessToken = connectionSettings?.settings?.access_token || connectionSettings.settings?.oauth?.credentials?.access_token;

  if (!connectionSettings || !accessToken) {
    throw new Error('Dropbox not connected');
  }
  return accessToken;
}

async function uploadFile(dbx: Dropbox, localPath: string, dropboxPath: string) {
  try {
    const fileContent = fs.readFileSync(localPath);
    await dbx.filesUpload({
      path: dropboxPath,
      contents: fileContent,
      mode: { '.tag': 'overwrite' }
    });
    return true;
  } catch (error) {
    console.error(`❌ Failed: ${dropboxPath}`);
    return false;
  }
}

async function uploadCharacterCards() {
  console.log('🚀 Uploading character cards to Dropbox...\n');
  
  const accessToken = await getAccessToken();
  const dbx = new Dropbox({ accessToken });
  
  const baseDir = '../Dropbox/Replit/ExecutiveDisorder_Assets/01_Characters/Character_Cards';
  const dropboxBase = '/Replit/ExecutiveDisorder_Assets/01_Characters/Character_Cards';
  
  const characters = fs.readdirSync(baseDir);
  
  let totalUploaded = 0;
  let totalFailed = 0;
  
  for (const char of characters) {
    const charPath = path.join(baseDir, char);
    const stat = fs.statSync(charPath);
    
    if (!stat.isDirectory()) continue;
    
    const cards = fs.readdirSync(charPath).filter(f => f.endsWith('.png'));
    console.log(`📁 ${char}: uploading ${cards.length} cards...`);
    
    for (const card of cards) {
      const localPath = path.join(charPath, card);
      const dropboxPath = `${dropboxBase}/${char}/${card}`;
      
      const success = await uploadFile(dbx, localPath, dropboxPath);
      if (success) {
        totalUploaded++;
      } else {
        totalFailed++;
      }
    }
    
    console.log(`✅ ${char}: complete\n`);
  }
  
  console.log(`\n📊 Upload Summary:`);
  console.log(`✅ Uploaded: ${totalUploaded} cards`);
  console.log(`❌ Failed: ${totalFailed} cards`);
  console.log(`\n🎉 Character cards upload complete!`);
}

uploadCharacterCards().catch(console.error);

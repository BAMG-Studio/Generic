#!/usr/bin/env tsx

/**
 * Upload all 90 scene variations to Dropbox backend
 * October 10, 2025
 */

import { Dropbox } from 'dropbox';
import { readFileSync, readdirSync, statSync } from 'fs';
import { join } from 'path';

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

async function getDropboxClient() {
  const accessToken = await getAccessToken();
  return new Dropbox({ accessToken });
}

function delay(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function uploadVariations() {
  console.log('📤 Uploading 90 Scene Variations to Dropbox Backend\n');
  console.log('='.repeat(70) + '\n');

  const dbx = await getDropboxClient();
  
  const variationFolders = [
    { local: 'Dropbox/Replit/Scenes/Backgrounds/Variations', remote: '/Replit/Art/Scenes/Backgrounds/Variations' },
    { local: 'Dropbox/Replit/Scenes/CrisisScenes/Variations', remote: '/Replit/Art/Scenes/CrisisScenes/Variations' },
    { local: 'Dropbox/Replit/Scenes/MeetingRooms/Variations', remote: '/Replit/Art/Scenes/MeetingRooms/Variations' },
    { local: 'Dropbox/Replit/Scenes/NewsScenes/Variations', remote: '/Replit/Art/Scenes/NewsScenes/Variations' },
    { local: 'Dropbox/Replit/Scenes/PublicSpaces/Variations', remote: '/Replit/Art/Scenes/PublicSpaces/Variations' }
  ];

  let uploaded = 0;
  let failed = 0;
  let totalFiles = 0;
  let retryDelay = 3000;

  for (const folder of variationFolders) {
    const files = readdirSync(folder.local).filter(f => f.endsWith('.png'));
    totalFiles += files.length;
    
    console.log(`📁 ${folder.local}`);
    console.log(`   → ${files.length} variations\n`);

    for (const [index, file] of files.entries()) {
      const localPath = join(folder.local, file);
      const remotePath = `${folder.remote}/${file}`;
      
      try {
        const fileContent = readFileSync(localPath);
        const fileSize = (fileContent.length / 1024 / 1024).toFixed(2);
        
        console.log(`   [${uploaded + failed + 1}/${totalFiles}] ${file}`);
        console.log(`   📊 ${fileSize} MB`);
        
        let attempts = 0;
        const maxAttempts = 3;
        let success = false;

        while (attempts < maxAttempts && !success) {
          try {
            await dbx.filesUpload({
              path: remotePath,
              contents: fileContent,
              mode: { '.tag': 'overwrite' }
            });
            
            uploaded++;
            success = true;
            console.log(`   ✅ Uploaded\n`);
            
            await delay(retryDelay);
          } catch (error: any) {
            attempts++;
            
            if (error.message?.includes('429')) {
              console.log(`   ⏳ Rate limited, waiting ${retryDelay/1000}s...`);
              await delay(retryDelay);
              retryDelay = Math.min(retryDelay * 1.5, 15000);
            } else if (error.message?.includes('conflict')) {
              console.log(`   ℹ️  Already exists, overwriting...`);
              await delay(retryDelay);
            } else {
              console.error(`   ❌ Error: ${error.message}`);
              if (attempts >= maxAttempts) {
                failed++;
                console.log(`   ⚠️  Failed after ${maxAttempts} attempts\n`);
              }
            }
          }
        }
      } catch (error: any) {
        console.error(`   ❌ Failed to read file: ${error.message}\n`);
        failed++;
      }
    }
    
    console.log(`   ✅ Folder complete\n`);
  }

  console.log('='.repeat(70));
  console.log(`✅ Uploaded: ${uploaded} files`);
  console.log(`❌ Failed: ${failed} files`);
  console.log(`📊 Total: ${totalFiles} variations`);
  console.log('='.repeat(70));
  
  return { uploaded, failed, totalFiles };
}

uploadVariations()
  .then(result => {
    if (result.failed === 0) {
      console.log('\n🎉 ALL 90 VARIATIONS UPLOADED TO DROPBOX BACKEND!');
      process.exit(0);
    } else {
      console.log(`\n⚠️  ${result.failed} files failed to upload`);
      process.exit(1);
    }
  })
  .catch(error => {
    console.error('❌ Upload failed:', error);
    process.exit(1);
  });
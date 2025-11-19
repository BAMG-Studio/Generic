#!/usr/bin/env tsx

import { Dropbox } from 'dropbox';
import { readFile, readdir } from 'fs/promises';
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
    throw new Error('X_REPLIT_TOKEN not found for repl/depl');
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

async function uploadMusicFiles() {
  try {
    console.log('🎵 Uploading music files to Dropbox...\n');

    const dbx = await getDropboxClient();
    const musicDir = join(process.cwd(), 'client', 'public', 'audio', 'music');
    
    // Get all files in music directory
    const files = await readdir(musicDir);
    const musicFiles = files.filter(f => f.endsWith('.mp3') || f.endsWith('.json') || f.endsWith('.md'));

    console.log(`Found ${musicFiles.length} files to upload\n`);

    for (const filename of musicFiles) {
      try {
        const filePath = join(musicDir, filename);
        const fileContents = await readFile(filePath);
        
        // Upload to Dropbox at /Replit/Art/Audio/Music/
        const dropboxPath = `/Replit/Art/Audio/Music/${filename}`;
        
        await dbx.filesUpload({
          path: dropboxPath,
          contents: fileContents,
          mode: { '.tag': 'overwrite' },
          autorename: false,
          mute: false
        });

        console.log(`✅ Uploaded: ${filename} → ${dropboxPath}`);
      } catch (error: any) {
        console.error(`❌ Failed to upload ${filename}:`, error.message);
      }
    }

    console.log('\n🎉 All music files uploaded to Dropbox successfully!');
    console.log('📁 Location: Dropbox/Replit/Art/Audio/Music/');
    
  } catch (error) {
    console.error('❌ Upload failed:', error);
    throw error;
  }
}

// Run the upload
uploadMusicFiles().catch(console.error);
#!/usr/bin/env tsx

/**
 * Upload newly generated assets to Dropbox backend
 * October 10, 2025 - Scene backgrounds, logo, character portraits
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

interface UploadSpec {
  localPath: string;
  dropboxPath: string;
  description: string;
}

async function uploadNewAssets() {
  console.log('📤 Uploading New Assets to Dropbox Backend\n');
  console.log('='.repeat(60) + '\n');

  const dbx = await getDropboxClient();
  
  // Define all new assets to upload
  const uploads: UploadSpec[] = [
    // Scene Backgrounds
    { localPath: 'Dropbox/Replit/Scenes/Backgrounds/oval-office.png', dropboxPath: '/Replit/Art/Scenes/Backgrounds/oval-office.png', description: 'Oval Office background' },
    { localPath: 'Dropbox/Replit/Scenes/Backgrounds/white-house-exterior.png', dropboxPath: '/Replit/Art/Scenes/Backgrounds/white-house-exterior.png', description: 'White House exterior' },
    { localPath: 'Dropbox/Replit/Scenes/Backgrounds/press-room.png', dropboxPath: '/Replit/Art/Scenes/Backgrounds/press-room.png', description: 'Press briefing room' },
    { localPath: 'Dropbox/Replit/Scenes/Backgrounds/situation-room.png', dropboxPath: '/Replit/Art/Scenes/Backgrounds/situation-room.png', description: 'Situation room' },
    
    // Crisis Scenes
    { localPath: 'Dropbox/Replit/Scenes/CrisisScenes/economic-crisis.png', dropboxPath: '/Replit/Art/Scenes/CrisisScenes/economic-crisis.png', description: 'Economic crisis scene' },
    { localPath: 'Dropbox/Replit/Scenes/CrisisScenes/natural-disaster.png', dropboxPath: '/Replit/Art/Scenes/CrisisScenes/natural-disaster.png', description: 'Natural disaster' },
    { localPath: 'Dropbox/Replit/Scenes/CrisisScenes/cyber-attack.png', dropboxPath: '/Replit/Art/Scenes/CrisisScenes/cyber-attack.png', description: 'Cyber attack scene' },
    
    // Meeting Rooms
    { localPath: 'Dropbox/Replit/Scenes/MeetingRooms/cabinet-room.png', dropboxPath: '/Replit/Art/Scenes/MeetingRooms/cabinet-room.png', description: 'Cabinet room' },
    { localPath: 'Dropbox/Replit/Scenes/MeetingRooms/international-summit.png', dropboxPath: '/Replit/Art/Scenes/MeetingRooms/international-summit.png', description: 'International summit' },
    { localPath: 'Dropbox/Replit/Scenes/MeetingRooms/un-assembly.png', dropboxPath: '/Replit/Art/Scenes/MeetingRooms/un-assembly.png', description: 'UN Assembly hall' },
    
    // News Scenes
    { localPath: 'Dropbox/Replit/Scenes/NewsScenes/tv-studio.png', dropboxPath: '/Replit/Art/Scenes/NewsScenes/tv-studio.png', description: 'TV news studio' },
    { localPath: 'Dropbox/Replit/Scenes/NewsScenes/breaking-news-set.png', dropboxPath: '/Replit/Art/Scenes/NewsScenes/breaking-news-set.png', description: 'Breaking news set' },
    
    // Public Spaces
    { localPath: 'Dropbox/Replit/Scenes/PublicSpaces/rally-stage.png', dropboxPath: '/Replit/Art/Scenes/PublicSpaces/rally-stage.png', description: 'Rally stage' },
    { localPath: 'Dropbox/Replit/Scenes/PublicSpaces/protest-square.png', dropboxPath: '/Replit/Art/Scenes/PublicSpaces/protest-square.png', description: 'Protest square' },
    { localPath: 'Dropbox/Replit/Scenes/PublicSpaces/airport-arrival.png', dropboxPath: '/Replit/Art/Scenes/PublicSpaces/airport-arrival.png', description: 'Airport arrival' },
    
    // Logo
    { localPath: 'Dropbox/Replit/Brand/Logos/main-logo.png', dropboxPath: '/Replit/Art/Brand/Logos/main-logo.png', description: 'Main game logo' },
    
    // Character Portraits - Staff
    { localPath: 'Dropbox/Replit/Portraits/Staff/chief-of-staff.png', dropboxPath: '/Replit/Art/Portraits/Staff/chief-of-staff.png', description: 'Chief of Staff' },
    { localPath: 'Dropbox/Replit/Portraits/Staff/press-secretary.png', dropboxPath: '/Replit/Art/Portraits/Staff/press-secretary.png', description: 'Press Secretary' },
    { localPath: 'Dropbox/Replit/Portraits/Staff/national-security-advisor.png', dropboxPath: '/Replit/Art/Portraits/Staff/national-security-advisor.png', description: 'National Security Advisor' },
    { localPath: 'Dropbox/Replit/Portraits/Staff/economic-advisor.png', dropboxPath: '/Replit/Art/Portraits/Staff/economic-advisor.png', description: 'Economic Advisor' },
    
    // Character Portraits - Other
    { localPath: 'Dropbox/Replit/Portraits/Citizens/everyday-citizen.png', dropboxPath: '/Replit/Art/Portraits/Citizens/everyday-citizen.png', description: 'Everyday citizen' },
    { localPath: 'Dropbox/Replit/Portraits/International/foreign-diplomat.png', dropboxPath: '/Replit/Art/Portraits/International/foreign-diplomat.png', description: 'Foreign diplomat' },
    { localPath: 'Dropbox/Replit/Portraits/International/asian-leader.png', dropboxPath: '/Replit/Art/Portraits/International/asian-leader.png', description: 'Asian leader' },
    { localPath: 'Dropbox/Replit/Portraits/Stakeholders/corporate-lobbyist.png', dropboxPath: '/Replit/Art/Portraits/Stakeholders/corporate-lobbyist.png', description: 'Corporate lobbyist' },
    { localPath: 'Dropbox/Replit/Portraits/Stakeholders/union-leader.png', dropboxPath: '/Replit/Art/Portraits/Stakeholders/union-leader.png', description: 'Union leader' },
    { localPath: 'Dropbox/Replit/Portraits/Crisis/investigative-journalist.png', dropboxPath: '/Replit/Art/Portraits/Crisis/investigative-journalist.png', description: 'Investigative journalist' }
  ];

  let uploaded = 0;
  let failed = 0;
  let skipped = 0;
  let retryDelay = 5000; // Start with 5 second delay

  console.log(`📋 ${uploads.length} assets to upload\n`);

  for (const [index, upload] of uploads.entries()) {
    const fileNum = `[${index + 1}/${uploads.length}]`;
    
    try {
      // Read file
      const fileContent = readFileSync(upload.localPath);
      const fileSize = (fileContent.length / 1024 / 1024).toFixed(2);
      
      console.log(`${fileNum} ${upload.description}`);
      console.log(`   📁 ${upload.dropboxPath}`);
      console.log(`   📊 ${fileSize} MB`);
      
      let attempts = 0;
      const maxAttempts = 3;
      let success = false;

      while (attempts < maxAttempts && !success) {
        try {
          await dbx.filesUpload({
            path: upload.dropboxPath,
            contents: fileContent,
            mode: { '.tag': 'overwrite' }
          });
          
          uploaded++;
          success = true;
          console.log(`   ✅ Uploaded\n`);
          
          // Wait between uploads to avoid rate limiting
          if (index < uploads.length - 1) {
            await delay(retryDelay);
          }
        } catch (error: any) {
          attempts++;
          
          if (error.message?.includes('429')) {
            console.log(`   ⏳ Rate limited, waiting ${retryDelay/1000}s...`);
            await delay(retryDelay);
            retryDelay = Math.min(retryDelay * 1.5, 30000); // Increase delay, max 30s
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

  console.log('\n' + '='.repeat(60));
  console.log(`✅ Uploaded: ${uploaded} files`);
  console.log(`❌ Failed: ${failed} files`);
  if (skipped > 0) console.log(`⏭️  Skipped: ${skipped} files`);
  console.log('='.repeat(60));
  
  return { uploaded, failed, skipped };
}

uploadNewAssets()
  .then(result => {
    if (result.failed === 0) {
      console.log('\n🎉 ALL NEW ASSETS UPLOADED TO DROPBOX BACKEND!');
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
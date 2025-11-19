#!/usr/bin/env tsx

import { Dropbox } from 'dropbox';
import { readFile, readdir, stat } from 'fs/promises';
import { join, relative } from 'path';

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

async function getAllFiles(dir: string): Promise<string[]> {
  const files: string[] = [];
  
  async function walk(currentDir: string) {
    const items = await readdir(currentDir);
    
    for (const item of items) {
      const fullPath = join(currentDir, item);
      const stats = await stat(fullPath);
      
      if (stats.isDirectory()) {
        await walk(fullPath);
      } else {
        files.push(fullPath);
      }
    }
  }
  
  await walk(dir);
  return files;
}

async function syncAllFiles() {
  try {
    console.log('🔄 Starting comprehensive Dropbox sync...\n');

    const dbx = await getDropboxClient();
    const localBaseDir = join(process.cwd(), 'Dropbox', 'Replit');
    
    // Get all files recursively
    console.log('📂 Scanning local files...');
    const allFiles = await getAllFiles(localBaseDir);
    console.log(`Found ${allFiles.length} files to upload\n`);

    let uploaded = 0;
    let failed = 0;
    let skipped = 0;

    for (const localFilePath of allFiles) {
      try {
        // Get relative path from Dropbox/Replit
        const relativePath = relative(localBaseDir, localFilePath);
        
        // Convert to Dropbox path
        const dropboxPath = `/Replit/${relativePath.replace(/\\/g, '/')}`;
        
        // Skip very large files or temporary files
        const stats = await stat(localFilePath);
        if (stats.size > 150 * 1024 * 1024) { // Skip files > 150MB
          console.log(`⏭️  Skipped (too large): ${relativePath}`);
          skipped++;
          continue;
        }

        // Read and upload file
        const fileContents = await readFile(localFilePath);
        
        await dbx.filesUpload({
          path: dropboxPath,
          contents: fileContents,
          mode: { '.tag': 'overwrite' },
          autorename: false,
          mute: true // Don't notify for every file
        });

        uploaded++;
        if (uploaded % 50 === 0) {
          console.log(`✅ Progress: ${uploaded}/${allFiles.length} files uploaded...`);
        }
      } catch (error: any) {
        failed++;
        console.error(`❌ Failed: ${relative(localBaseDir, localFilePath)} - ${error.message}`);
      }
    }

    console.log('\n' + '='.repeat(60));
    console.log('📊 Sync Complete!');
    console.log('='.repeat(60));
    console.log(`✅ Uploaded: ${uploaded} files`);
    console.log(`❌ Failed: ${failed} files`);
    console.log(`⏭️  Skipped: ${skipped} files`);
    console.log('='.repeat(60));
    console.log('\n📁 All files synced to: Dropbox/Replit/');
    
  } catch (error) {
    console.error('❌ Sync failed:', error);
    throw error;
  }
}

async function renameDonaldExecutiveFiles() {
  try {
    console.log('\n🔍 Checking for donald-executive files in Dropbox...\n');
    
    const dbx = await getDropboxClient();
    
    // Search for files with 'donald-executive' in the name
    const searchResult = await dbx.filesSearchV2({
      query: 'donald-executive',
      options: {
        path: '/Replit',
        file_status: { '.tag': 'active' },
        filename_only: true
      }
    });

    if (searchResult.result.matches.length === 0) {
      console.log('✅ No donald-executive files found in Dropbox!');
      return;
    }

    console.log(`Found ${searchResult.result.matches.length} donald-executive files to rename\n`);

    for (const match of searchResult.result.matches) {
      if (match.metadata['.tag'] === 'metadata' && match.metadata.metadata['.tag'] === 'file') {
        const oldPath = match.metadata.metadata.path_display || '';
        const newPath = oldPath.replace(/donald-executive/g, 'ronald-goldenberg');
        
        if (oldPath !== newPath) {
          try {
            await dbx.filesMoveV2({
              from_path: oldPath,
              to_path: newPath,
              autorename: false
            });
            console.log(`✅ Renamed: ${oldPath} → ${newPath}`);
          } catch (error: any) {
            console.error(`❌ Failed to rename ${oldPath}:`, error.message);
          }
        }
      }
    }

    console.log('\n✅ All donald-executive files renamed to ronald-goldenberg!');
    
  } catch (error) {
    console.error('❌ Rename operation failed:', error);
  }
}

// Run both operations
async function main() {
  await syncAllFiles();
  await renameDonaldExecutiveFiles();
  console.log('\n🎉 Complete! All files synced and renamed.');
}

main().catch(console.error);
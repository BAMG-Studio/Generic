#!/usr/bin/env tsx

import { Dropbox } from 'dropbox';
import { readFile, readdir, stat, writeFile } from 'fs/promises';
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
    try {
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
    } catch (error) {
      console.error(`Error walking ${currentDir}:`, error);
    }
  }
  
  await walk(dir);
  return files;
}

async function batchSync(batchSize = 100) {
  try {
    const dbx = await getDropboxClient();
    const localBaseDir = join(process.cwd(), 'Dropbox', 'Replit');
    const progressFile = join(process.cwd(), '.dropbox-sync-progress.json');
    
    // Load progress
    let uploadedFiles: Set<string> = new Set();
    try {
      const progressData = await readFile(progressFile, 'utf-8');
      uploadedFiles = new Set(JSON.parse(progressData));
      console.log(`📂 Resuming from ${uploadedFiles.size} previously uploaded files\n`);
    } catch {
      console.log('📂 Starting fresh upload\n');
    }

    // Get all files
    console.log('🔍 Scanning local files...');
    const allFiles = await getAllFiles(localBaseDir);
    const filesToUpload = allFiles.filter(f => !uploadedFiles.has(f));
    
    console.log(`📊 Total: ${allFiles.length} files`);
    console.log(`✅ Already uploaded: ${uploadedFiles.size} files`);
    console.log(`📤 Remaining: ${filesToUpload.length} files\n`);

    if (filesToUpload.length === 0) {
      console.log('🎉 All files already uploaded!');
      return;
    }

    // Upload in batches
    const batchesToProcess = filesToUpload.slice(0, batchSize);
    console.log(`🚀 Uploading batch of ${batchesToProcess.length} files...\n`);

    let uploaded = 0;
    let failed = 0;

    for (const localFilePath of batchesToProcess) {
      try {
        const relativePath = relative(localBaseDir, localFilePath);
        const dropboxPath = `/Replit/${relativePath.replace(/\\/g, '/')}`;
        
        const stats = await stat(localFilePath);
        if (stats.size > 150 * 1024 * 1024) {
          console.log(`⏭️  Skipped (too large): ${relativePath}`);
          uploadedFiles.add(localFilePath);
          continue;
        }

        const fileContents = await readFile(localFilePath);
        
        await dbx.filesUpload({
          path: dropboxPath,
          contents: fileContents,
          mode: { '.tag': 'overwrite' },
          autorename: false,
          mute: true
        });

        uploaded++;
        uploadedFiles.add(localFilePath);
        
        if (uploaded % 10 === 0) {
          console.log(`✅ ${uploaded}/${batchesToProcess.length} uploaded...`);
        }
      } catch (error: any) {
        failed++;
        console.error(`❌ Failed: ${relative(localBaseDir, localFilePath)}`);
      }
    }

    // Save progress
    await writeFile(progressFile, JSON.stringify([...uploadedFiles], null, 2));

    console.log('\n' + '='.repeat(60));
    console.log(`✅ Uploaded: ${uploaded} files`);
    console.log(`❌ Failed: ${failed} files`);
    console.log(`📊 Total progress: ${uploadedFiles.size}/${allFiles.length}`);
    console.log(`📝 Remaining: ${allFiles.length - uploadedFiles.size} files`);
    console.log('='.repeat(60));

    if (uploadedFiles.size < allFiles.length) {
      console.log('\n💡 Run this script again to continue uploading remaining files');
    } else {
      console.log('\n🎉 ALL FILES UPLOADED!');
    }
    
  } catch (error) {
    console.error('❌ Batch sync failed:', error);
    throw error;
  }
}

// Upload 200 files per run
batchSync(200).catch(console.error);
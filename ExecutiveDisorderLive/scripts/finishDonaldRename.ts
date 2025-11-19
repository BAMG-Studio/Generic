#!/usr/bin/env tsx

import { Dropbox } from 'dropbox';

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

function delay(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function renameWithRetry() {
  try {
    console.log('🔄 Renaming remaining donald-executive files with delays...\n');
    
    const dbx = await getDropboxClient();
    
    // Get all files
    let allFiles: any[] = [];
    let hasMore = true;
    let cursor: string | undefined;

    while (hasMore) {
      const result: any = cursor 
        ? await dbx.filesListFolderContinue({ cursor })
        : await dbx.filesListFolder({ path: '/Replit', recursive: true });

      allFiles = allFiles.concat(result.result.entries);
      hasMore = result.result.has_more;
      cursor = result.result.cursor;
    }

    // Find remaining donald-executive files
    const donaldFiles = allFiles.filter((entry: any) => 
      entry['.tag'] === 'file' && 
      (entry.path_lower || '').includes('donald-executive')
    );

    console.log(`Found ${donaldFiles.length} donald-executive files remaining\n`);

    if (donaldFiles.length === 0) {
      console.log('✅ All files already renamed to ronald-goldenberg!');
      return;
    }

    let renamed = 0;
    let failed = 0;

    for (const [index, file] of donaldFiles.entries()) {
      const oldPath = file.path_display || file.path_lower;
      const newPath = oldPath.replace(/donald-executive/gi, 'ronald-goldenberg');
      
      try {
        console.log(`[${index + 1}/${donaldFiles.length}] Renaming...`);
        console.log(`  ${oldPath.split('/').pop()}`);
        
        await dbx.filesMoveV2({
          from_path: oldPath,
          to_path: newPath,
          autorename: false
        });
        
        renamed++;
        console.log(`  ✅ Success\n`);
        
        // Wait 2 seconds between renames to avoid rate limiting
        if (index < donaldFiles.length - 1) {
          await delay(2000);
        }
      } catch (error: any) {
        failed++;
        console.error(`  ❌ Failed: ${error.message}\n`);
        
        // If rate limited, wait longer
        if (error.message.includes('429')) {
          console.log('  ⏳ Rate limited, waiting 10 seconds...\n');
          await delay(10000);
        }
      }
    }

    console.log('='.repeat(60));
    console.log(`✅ Renamed: ${renamed} files`);
    console.log(`❌ Failed: ${failed} files`);
    console.log('='.repeat(60));
    
  } catch (error) {
    console.error('❌ Operation failed:', error);
    throw error;
  }
}

renameWithRetry().catch(console.error);
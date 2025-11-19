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

async function renameWithExponentialBackoff() {
  try {
    console.log('🔄 Final donald-executive rename with exponential backoff...\n');
    
    const dbx = await getDropboxClient();
    
    // Get all files
    console.log('📂 Scanning Dropbox...');
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

    // Find donald-executive files
    const donaldFiles = allFiles.filter((entry: any) => 
      entry['.tag'] === 'file' && 
      (entry.path_lower || '').includes('donald-executive')
    );

    console.log(`Found ${donaldFiles.length} donald-executive files\n`);

    if (donaldFiles.length === 0) {
      console.log('✅ All files already renamed to ronald-goldenberg!');
      return { success: true, renamed: 0, failed: 0 };
    }

    let renamed = 0;
    let failed = 0;
    let retryDelay = 15000; // Start with 15 second delay

    for (const [index, file] of donaldFiles.entries()) {
      const oldPath = file.path_display || file.path_lower;
      const newPath = oldPath.replace(/donald-executive/gi, 'ronald-goldenberg');
      
      let attempts = 0;
      const maxAttempts = 3;
      let success = false;

      while (attempts < maxAttempts && !success) {
        try {
          console.log(`[${index + 1}/${donaldFiles.length}] Attempt ${attempts + 1}/${maxAttempts}`);
          console.log(`  ${oldPath.split('/').slice(-2).join('/')}`);
          
          await dbx.filesMoveV2({
            from_path: oldPath,
            to_path: newPath,
            autorename: false
          });
          
          renamed++;
          success = true;
          console.log(`  ✅ Success\n`);
          
          // Wait between successful renames
          if (index < donaldFiles.length - 1) {
            await delay(retryDelay);
          }
        } catch (error: any) {
          attempts++;
          
          if (error.message.includes('429')) {
            console.log(`  ⏳ Rate limited, waiting ${retryDelay/1000}s...`);
            await delay(retryDelay);
            
            // Exponential backoff - double the delay
            retryDelay = Math.min(retryDelay * 2, 120000); // Max 2 minutes
          } else if (error.message.includes('not_found')) {
            console.log(`  ℹ️  File already renamed or moved\n`);
            success = true; // Count as success, file doesn't exist anymore
            renamed++;
            break;
          } else {
            console.error(`  ❌ Error: ${error.message}`);
            if (attempts >= maxAttempts) {
              failed++;
              console.log(`  ⚠️  Giving up after ${maxAttempts} attempts\n`);
            }
          }
        }
      }
    }

    console.log('\n' + '='.repeat(60));
    console.log(`✅ Renamed: ${renamed} files`);
    console.log(`❌ Failed: ${failed} files`);
    console.log('='.repeat(60));
    
    return { success: failed === 0, renamed, failed };
    
  } catch (error) {
    console.error('❌ Operation failed:', error);
    throw error;
  }
}

renameWithExponentialBackoff()
  .then(result => {
    if (result.success) {
      console.log('\n🎉 ALL DONALD-EXECUTIVE FILES SUCCESSFULLY RENAMED!');
      process.exit(0);
    } else {
      console.log(`\n⚠️  ${result.failed} files still need manual rename`);
      process.exit(1);
    }
  })
  .catch(error => {
    console.error(error);
    process.exit(1);
  });
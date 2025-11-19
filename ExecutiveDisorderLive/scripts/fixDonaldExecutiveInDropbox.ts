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

async function listAndRenameDonaldExecutive() {
  try {
    console.log('🔍 Searching for donald-executive files in Dropbox...\n');
    
    const dbx = await getDropboxClient();
    
    // List all files in /Replit directory recursively
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

    console.log(`📊 Total files in Dropbox /Replit: ${allFiles.length}\n`);

    // Find donald-executive files
    const donaldFiles = allFiles.filter((entry: any) => 
      entry['.tag'] === 'file' && 
      (entry.path_lower || '').includes('donald-executive')
    );

    if (donaldFiles.length === 0) {
      console.log('✅ No donald-executive files found!');
      console.log('✨ All files already use ronald-goldenberg naming!');
      return;
    }

    console.log(`Found ${donaldFiles.length} donald-executive files to rename:\n`);

    let renamed = 0;
    let failed = 0;

    for (const file of donaldFiles) {
      const oldPath = file.path_display || file.path_lower;
      const newPath = oldPath.replace(/donald-executive/gi, 'ronald-goldenberg');
      
      if (oldPath !== newPath) {
        try {
          console.log(`📝 ${oldPath}`);
          console.log(`   → ${newPath}`);
          
          await dbx.filesMoveV2({
            from_path: oldPath,
            to_path: newPath,
            autorename: false
          });
          
          renamed++;
          console.log(`   ✅ Renamed successfully\n`);
        } catch (error: any) {
          failed++;
          console.error(`   ❌ Failed: ${error.message}\n`);
        }
      }
    }

    console.log('='.repeat(60));
    console.log(`✅ Successfully renamed: ${renamed} files`);
    console.log(`❌ Failed: ${failed} files`);
    console.log('='.repeat(60));
    
  } catch (error) {
    console.error('❌ Operation failed:', error);
    throw error;
  }
}

listAndRenameDonaldExecutive().catch(console.error);
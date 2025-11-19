import { Dropbox } from 'dropbox';

let connectionSettings;

async function getAccessToken() {
  const hostname = process.env.REPLIT_CONNECTORS_HOSTNAME
  const xReplitToken = process.env.REPL_IDENTITY 
    ? 'repl ' + process.env.REPL_IDENTITY 
    : process.env.WEB_REPL_RENEWAL 
    ? 'depl ' + process.env.WEB_REPL_RENEWAL 
    : null;

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
  return accessToken;
}

async function checkDropboxFiles() {
  const accessToken = await getAccessToken();
  const client = new Dropbox({ accessToken });
  
  try {
    // Check main Replit folder
    const result = await client.filesListFolder({ path: '/Replit', recursive: true });
    
    const files = result.result.entries.filter(entry => entry['.tag'] === 'file');
    const folders = result.result.entries.filter(entry => entry['.tag'] === 'folder');
    
    console.log('=== DROPBOX UPLOAD STATUS ===');
    console.log(`✅ Successfully uploaded to Dropbox:/Replit`);
    console.log(`📁 Folders created: ${folders.length}`);
    console.log(`📄 Files uploaded: ${files.length}`);
    console.log('');
    console.log('Sample uploaded files:');
    files.slice(0, 10).forEach(file => {
      console.log(`  ✓ ${file.path_display}`);
    });
    if (files.length > 10) {
      console.log(`  ... and ${files.length - 10} more files`);
    }
    
  } catch (error) {
    if (error.error?.error?.['.tag'] === 'path' && error.error?.error?.path?.['.tag'] === 'not_found') {
      console.log('Replit folder not found in Dropbox yet. Upload may still be in progress.');
    } else {
      console.error('Error checking Dropbox:', error.message);
    }
  }
}

checkDropboxFiles().catch(console.error);

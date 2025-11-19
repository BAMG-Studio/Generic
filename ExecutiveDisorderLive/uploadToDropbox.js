import { Dropbox } from 'dropbox';
import fs from 'fs';
import path from 'path';

let connectionSettings;

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

async function getUncachableDropboxClient() {
  const accessToken = await getAccessToken();
  return new Dropbox({ accessToken });
}

async function uploadFile(client, localPath, dropboxPath) {
  try {
    const content = fs.readFileSync(localPath);
    await client.filesUpload({
      path: dropboxPath,
      contents: content,
      mode: { '.tag': 'overwrite' }
    });
    console.log(`✓ Uploaded: ${dropboxPath}`);
    return true;
  } catch (error) {
    console.error(`✗ Failed to upload ${localPath}: ${error.message}`);
    return false;
  }
}

async function uploadDirectory(localDir, dropboxBaseDir) {
  const client = await getUncachableDropboxClient();
  let uploadedCount = 0;
  let failedCount = 0;

  async function processDirectory(currentLocalDir, currentDropboxDir) {
    const items = fs.readdirSync(currentLocalDir, { withFileTypes: true });
    
    for (const item of items) {
      const localPath = path.join(currentLocalDir, item.name);
      const dropboxPath = `${currentDropboxDir}/${item.name}`;
      
      if (item.isDirectory()) {
        await processDirectory(localPath, dropboxPath);
      } else if (item.isFile()) {
        const success = await uploadFile(client, localPath, dropboxPath);
        if (success) uploadedCount++;
        else failedCount++;
      }
    }
  }

  console.log(`Starting upload from ${localDir} to Dropbox:${dropboxBaseDir}`);
  console.log('This may take a few minutes...\n');
  
  await processDirectory(localDir, dropboxBaseDir);
  
  console.log('\n=== Upload Complete ===');
  console.log(`✓ Successfully uploaded: ${uploadedCount} files`);
  if (failedCount > 0) {
    console.log(`✗ Failed: ${failedCount} files`);
  }
}

// Upload all assets to Dropbox
const localFolder = './Dropbox/Replit';
const dropboxFolder = '/Replit';

uploadDirectory(localFolder, dropboxFolder)
  .then(() => {
    console.log('\n✅ All game assets have been uploaded to your Dropbox!');
    console.log('Check your Dropbox folder: /Replit');
  })
  .catch((error) => {
    console.error('Upload failed:', error);
  });
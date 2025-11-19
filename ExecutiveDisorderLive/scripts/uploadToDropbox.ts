import { Dropbox } from 'dropbox';
import * as fs from 'fs';
import * as path from 'path';

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

async function uploadFile(dbx: Dropbox, localPath: string, dropboxPath: string) {
  try {
    const fileContent = fs.readFileSync(localPath);
    const response = await dbx.filesUpload({
      path: dropboxPath,
      contents: fileContent,
      mode: { '.tag': 'overwrite' }
    });
    console.log(`✅ Uploaded: ${dropboxPath}`);
    return response;
  } catch (error) {
    console.error(`❌ Failed to upload ${dropboxPath}:`, error);
    throw error;
  }
}

async function getAllFiles(dir: string, fileList: string[] = []): Promise<string[]> {
  const files = fs.readdirSync(dir);
  
  for (const file of files) {
    const filePath = path.join(dir, file);
    const stat = fs.statSync(filePath);
    
    if (stat.isDirectory()) {
      getAllFiles(filePath, fileList);
    } else {
      fileList.push(filePath);
    }
  }
  
  return fileList;
}

async function uploadAssetsToDropbox() {
  console.log('🚀 Starting Dropbox upload...\n');
  
  const dbx = await getDropboxClient();
  const localBaseDir = '../Dropbox/Replit/ExecutiveDisorder_Assets';
  const dropboxBaseDir = '/Replit/ExecutiveDisorder_Assets';
  
  // Get all files from local directory
  const allFiles = await getAllFiles(localBaseDir);
  
  console.log(`Found ${allFiles.length} files to upload\n`);
  
  let uploadedCount = 0;
  let failedCount = 0;
  
  for (const localPath of allFiles) {
    // Convert local path to Dropbox path
    const relativePath = localPath.replace(localBaseDir, '');
    const dropboxPath = dropboxBaseDir + relativePath;
    
    try {
      await uploadFile(dbx, localPath, dropboxPath);
      uploadedCount++;
    } catch (error) {
      failedCount++;
    }
  }
  
  console.log(`\n📊 Upload Summary:`);
  console.log(`✅ Successfully uploaded: ${uploadedCount} files`);
  console.log(`❌ Failed: ${failedCount} files`);
  console.log(`\n🎉 Dropbox upload complete!`);
}

// Run the upload
uploadAssetsToDropbox().catch(console.error);

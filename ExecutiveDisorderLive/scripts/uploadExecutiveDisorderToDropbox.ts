import { Dropbox } from 'dropbox';
import fs from 'fs';
import path from 'path';

let connectionSettings: any;

async function getAccessToken(): Promise<string> {
  if (connectionSettings && connectionSettings.settings.expires_at && new Date(connectionSettings.settings.expires_at).getTime() > Date.now()) {
    return connectionSettings.settings.access_token;
  }
  
  const hostname = process.env.REPLIT_CONNECTORS_HOSTNAME;
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

async function getDropboxClient(): Promise<Dropbox> {
  const accessToken = await getAccessToken();
  return new Dropbox({ accessToken });
}

function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}

async function uploadDirectoryToDropbox(localDir: string, dropboxBasePath: string) {
  console.log(`☁️  Uploading ${localDir} to Dropbox...`);
  const client = await getDropboxClient();
  let uploadedCount = 0;
  let totalBytes = 0;

  async function uploadRecursive(currentLocalDir: string, currentDropboxPath: string) {
    const entries = fs.readdirSync(currentLocalDir, { withFileTypes: true });
    
    for (const entry of entries) {
      const localPath = path.join(currentLocalDir, entry.name);
      const dropboxPath = `${currentDropboxPath}/${entry.name}`;
      
      if (entry.isDirectory()) {
        await uploadRecursive(localPath, dropboxPath);
      } else if (entry.isFile()) {
        const content = fs.readFileSync(localPath);
        const stats = fs.statSync(localPath);
        
        try {
          await client.filesUpload({
            path: dropboxPath,
            contents: content,
            mode: { '.tag': 'overwrite' }
          });
          
          uploadedCount++;
          totalBytes += stats.size;
          
          if (uploadedCount % 10 === 0) {
            console.log(`   Uploaded ${uploadedCount} files... (${formatBytes(totalBytes)})`);
          }
        } catch (error) {
          console.error(`   ❌ Failed to upload ${dropboxPath}:`, error);
        }
      }
    }
  }
  
  await uploadRecursive(localDir, dropboxBasePath);
  
  return { uploadedCount, totalBytes };
}

async function uploadAllAssets() {
  console.log('☁️  UPLOADING ExecutiveDisorder_Assets TO DROPBOX');
  console.log('==========================================\n');

  const localBase = 'Dropbox/Replit/ExecutiveDisorder_Assets';
  const dropboxBase = '/Replit/ExecutiveDisorder_Assets';

  if (!fs.existsSync(localBase)) {
    console.error(`❌ Directory not found: ${localBase}`);
    process.exit(1);
  }

  const result = await uploadDirectoryToDropbox(localBase, dropboxBase);

  console.log('\n==========================================');
  console.log('📊 UPLOAD SUMMARY');
  console.log('==========================================\n');
  console.log(`✅ Files Uploaded: ${result.uploadedCount}`);
  console.log(`📦 Total Size: ${formatBytes(result.totalBytes)}`);
  console.log(`☁️  Dropbox Location: ${dropboxBase}\n`);
  console.log('✨ Dropbox upload complete!\n');

  return result;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  uploadAllAssets()
    .then(() => process.exit(0))
    .catch((error) => {
      console.error('Fatal error:', error);
      process.exit(1);
    });
}

export { uploadAllAssets };

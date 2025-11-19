import { Dropbox } from 'dropbox';
import fs from 'fs';

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

/**
 * Upload a single file to Dropbox
 * @param localPath Local file path
 * @param dropboxPath Dropbox destination path (e.g., '/Replit/Art/Videos/myv video.mp4')
 * @returns Dropbox path if successful
 */
export async function uploadToDropbox(localPath: string, dropboxPath: string): Promise<string> {
  try {
    const client = await getDropboxClient();
    const content = fs.readFileSync(localPath);
    
    await client.filesUpload({
      path: dropboxPath,
      contents: content,
      mode: { '.tag': 'overwrite' }
    });
    
    return dropboxPath;
  } catch (error) {
    console.error(`Failed to upload ${localPath} to Dropbox:`, error);
    throw error;
  }
}

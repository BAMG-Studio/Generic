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
    throw new Error('X_REPLIT_TOKEN not found');
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

async function uploadCharacters() {
  const accessToken = await getAccessToken();
  const client = new Dropbox({ accessToken });
  
  const dirs = [
    { local: './Dropbox/Replit/characters/main-portraits', dropbox: '/Replit/characters/main-portraits' },
    { local: './Dropbox/Replit/characters/variations', dropbox: '/Replit/characters/variations' }
  ];
  
  let uploaded = 0;
  
  for (const dir of dirs) {
    if (fs.existsSync(dir.local)) {
      const files = fs.readdirSync(dir.local);
      console.log(`Uploading ${files.length} files from ${dir.local}...`);
      
      for (const file of files) {
        if (file.endsWith('.png')) {
          try {
            const content = fs.readFileSync(path.join(dir.local, file));
            await client.filesUpload({
              path: `${dir.dropbox}/${file}`,
              contents: content,
              mode: { '.tag': 'overwrite' }
            });
            uploaded++;
            if (uploaded % 10 === 0) {
              console.log(`Progress: ${uploaded} files uploaded...`);
            }
          } catch (error) {
            console.error(`Failed: ${file}`);
          }
        }
      }
    }
  }
  
  console.log(`✓ Uploaded ${uploaded} character files to Dropbox!`);
}

uploadCharacters().catch(console.error);

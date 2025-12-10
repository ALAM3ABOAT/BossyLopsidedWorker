import { Octokit } from '@octokit/rest'

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
    'https://' + hostname + '/api/v2/connection?include_secrets=true&connector_names=github',
    {
      headers: {
        'Accept': 'application/json',
        'X_REPLIT_TOKEN': xReplitToken
      }
    }
  ).then(res => res.json()).then(data => data.items?.[0]);

  const accessToken = connectionSettings?.settings?.access_token || connectionSettings.settings?.oauth?.credentials?.access_token;

  if (!connectionSettings || !accessToken) {
    throw new Error('GitHub not connected');
  }
  return accessToken;
}

async function addDraftIssueToProject() {
  const accessToken = await getAccessToken();
  
  const response = await fetch('https://api.github.com/graphql', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query: `
        mutation {
          addProjectV2DraftIssue(input: {
            projectId: "PVT_kwHODsOfx84BKRQO"
            title: "رابط الموقع"
            body: "https://4cb59f90-6225-4cf3-9322-3e1da93fa807-00-2ugr5lcgj7wl7.spock.replit.dev/"
          }) {
            projectItem {
              id
            }
          }
        }
      `
    })
  });

  const data = await response.json();
  console.log('Result:', JSON.stringify(data, null, 2));
  
  if (data.errors) {
    console.error('Errors:', data.errors);
  } else {
    console.log('تم إضافة الرابط بنجاح إلى المشروع!');
  }
}

addDraftIssueToProject().catch(console.error);

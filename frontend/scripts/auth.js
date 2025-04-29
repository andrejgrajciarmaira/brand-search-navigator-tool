
#!/usr/bin/env node

const { OAuth2Client } = require('google-auth-library');
const http = require('http');
const url = require('url');
const fs = require('fs');
const path = require('path');
const dotenv = require('dotenv');
const open = require('open');

// Load environment variables from .env file if it exists
dotenv.config();

// Check for required environment variables
const clientId = process.env.GOOGLE_CLIENT_ID;
const clientSecret = process.env.GOOGLE_CLIENT_SECRET;

if (!clientId || !clientSecret) {
  console.error('\x1b[31mError: Missing required environment variables!\x1b[0m');
  console.error('Please create a .env file in the project root with the following variables:');
  console.error('\x1b[33mGOOGLE_CLIENT_ID=your-client-id\nGOOGLE_CLIENT_SECRET=your-client-secret\x1b[0m');
  process.exit(1);
}

// Set up OAuth2 client
const oauth2Client = new OAuth2Client(
  clientId,
  clientSecret,
  'http://localhost:8080/callback'
);

// Generate a URL for authorization
const scopes = [
  'https://www.googleapis.com/auth/adwords'
];

const authorizeUrl = oauth2Client.generateAuthUrl({
  access_type: 'offline',
  scope: scopes,
  prompt: 'consent'
});

// Start a local web server to handle the OAuth callback
const server = http.createServer(async (req, res) => {
  try {
    const reqUrl = url.parse(req.url, true);
    
    if (reqUrl.pathname === '/callback') {
      // Handle OAuth callback
      const code = reqUrl.query.code;
      if (!code) {
        res.writeHead(400);
        res.end('Error: No authorization code was received');
        return;
      }

      // Exchange the authorization code for tokens
      const { tokens } = await oauth2Client.getToken(code);
      
      // Send success response to browser
      res.writeHead(200, { 'Content-Type': 'text/html' });
      res.end(`
        <html>
          <head>
            <title>Authentication Successful</title>
            <style>
              body { font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; line-height: 1.6; }
              .success { color: green; font-size: 1.2em; }
              .code { background: #f4f4f4; padding: 10px; border-radius: 4px; overflow-x: auto; }
            </style>
          </head>
          <body>
            <h2>Google Ads API Authentication Successful!</h2>
            <p class="success">✅ Authentication completed successfully.</p>
            <p>Your refresh token has been saved to your .env file.</p>
            <p>You can now close this window and return to your terminal.</p>
          </body>
        </html>
      `);

      // Update .env file with the refresh token
      let envContent;
      const envPath = path.resolve(process.cwd(), '.env');
      
      try {
        if (fs.existsSync(envPath)) {
          envContent = fs.readFileSync(envPath, 'utf8');
        } else {
          envContent = `GOOGLE_CLIENT_ID=${clientId}\nGOOGLE_CLIENT_SECRET=${clientSecret}\n`;
        }
        
        // Check if GOOGLE_REFRESH_TOKEN already exists in the .env file
        if (envContent.includes('GOOGLE_REFRESH_TOKEN=')) {
          // Replace existing refresh token
          envContent = envContent.replace(
            /GOOGLE_REFRESH_TOKEN=.*/,
            `GOOGLE_REFRESH_TOKEN=${tokens.refresh_token}`
          );
        } else {
          // Add refresh token to .env file
          envContent += `\nGOOGLE_REFRESH_TOKEN=${tokens.refresh_token}`;
        }
        
        fs.writeFileSync(envPath, envContent);
        console.log('\x1b[32m✅ Authentication successful!\x1b[0m');
        console.log('\x1b[32m✅ Refresh token saved to .env file\x1b[0m');
      } catch (err) {
        console.error('\x1b[31mError updating .env file:\x1b[0m', err);
        console.log('\x1b[33mPlease manually add your refresh token to your .env file:\x1b[0m');
        console.log(`GOOGLE_REFRESH_TOKEN=${tokens.refresh_token}`);
      }
      
      // Close the server
      server.close();
      process.exit(0);
    } else {
      // Handle other routes
      res.writeHead(404);
      res.end('Not found');
    }
  } catch (err) {
    console.error('Error during authentication:', err);
    res.writeHead(500);
    res.end('Authentication error occurred');
    server.close();
    process.exit(1);
  }
});

// Start server on a free port
server.listen(8080, () => {
  console.log('\x1b[34mStarting authentication process...\x1b[0m');
  console.log('\x1b[34mA browser window should open automatically.\x1b[0m');
  console.log('\x1b[34mIf not, please open this URL in your browser:\x1b[0m');
  console.log('\x1b[36m%s\x1b[0m', authorizeUrl);
  
  // Open the auth URL in the default browser
  open(authorizeUrl).catch(() => {
    console.log('\x1b[33mCould not open browser automatically. Please open the URL above manually.\x1b[0m');
  });
});

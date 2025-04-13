# Share of Brand Search Tool

A web application that allows you to analyze brand search volumes from Google Ads Keyword Planner. Compare your brand's search performance against competitors and visualize market share trends over time.

## Features

- Input and manage multiple brands and their related keywords
- Separate your own brands from competitor brands
- Select location, language, and network settings
- Choose custom date ranges for analysis
- View data at monthly, quarterly, or yearly granularity
- Visualize results as:
  - Share of search percentage charts
  - Absolute search volume charts
  - Raw data tables
- Export charts and data for reporting

## Prerequisites

Before running this application, you'll need:

1. **Node.js**: Version 14 or higher
2. **Google Ads Account**: With admin access
3. **Google Cloud Platform Account**: For API credentials
4. **Google Ads API Setup**: Developer token and OAuth credentials

## Running the Application Locally

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/share-of-search-tool.git
cd share-of-search-tool
```

### 2. Install dependencies

```bash
npm install
```

### 3. Configure Environment Variables

Create a `.env` file in the root directory based on the provided `.env.example` file:

```
# Google Ads API credentials
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_DEVELOPER_TOKEN=your-developer-token
GOOGLE_REFRESH_TOKEN=your-refresh-token (will be obtained during authentication)
```

### 4. Obtain a Refresh Token

Install the required packages for authentication and run the authentication script:

```bash
npm install google-auth-library dotenv open
node scripts/auth.js
```

Follow the prompts in the browser to authenticate and generate a refresh token.

### 5. Start the development server

```bash
npm run dev
```

Visit `http://localhost:8080` in your browser to use the application.

## Google Ads API Setup Guide

To use this application with real data from Google Ads, you'll need to set up the Google Ads API. Follow these detailed steps:

### Step 1: Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Ads API for your project:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google Ads API"
   - Click "Enable"

### Step 2: Set up OAuth 2.0 Credentials

1. In the Google Cloud Console, go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" and select "OAuth client ID"
3. Select "Web application" as the application type
4. Add a name for your OAuth client
5. Add `http://localhost:8080/callback` as an authorized redirect URI
6. Click "Create" to generate your Client ID and Client Secret

### Step 3: Obtain a Developer Token

1. Log in to your Google Ads account at [ads.google.com](https://ads.google.com)
2. Click the tools icon in the upper right corner
3. Under "Setup," select "API Center"
4. Apply for a developer token by providing the required information

> Note: For testing purposes, you can use a test account which provides immediate access with limited functionality.

### Step 4: Generate a Refresh Token

1. Configure your `.env` file with your client ID and secret
2. Run the authentication script:
   ```bash
   node scripts/auth.js
   ```
3. Follow the prompts to authorize the application
4. The refresh token will be automatically saved to your `.env` file

## Data Integration

This application uses the Google Ads API to fetch keyword search volume data. The integration:

1. Connects to the Google Ads API using your credentials
2. Retrieves historical search volume data for specified keywords
3. Groups the data by brand based on your configuration
4. Calculates share percentages for each time period
5. Generates visualizations based on the aggregated data

## License

[MIT License](LICENSE)

## Contact

For questions or support, please contact [your-email@example.com](mailto:your-email@example.com)

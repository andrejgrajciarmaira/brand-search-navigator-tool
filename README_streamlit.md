
# Share of Brand Search Tool - Streamlit Version

This is a Streamlit version of the Share of Brand Search Tool that allows users to analyze brand search volumes from Google Ads Keyword Planner.

## Deploying to Streamlit Cloud

To deploy this application on Streamlit Cloud:

1. **Fork or upload the code to a GitHub repository**

2. **Create a Streamlit account**
   - Sign up at [streamlit.io](https://streamlit.io)
   - Connect your GitHub account

3. **Create a new app**
   - Click "New app"
   - Select the GitHub repository
   - Set the main file path to `app.py`
   - Click "Deploy"

4. **Set up secrets**
   - In your Streamlit Cloud dashboard, go to your app settings
   - Find the "Secrets" section
   - Add the following secrets:

   ```toml
   GOOGLE_CLIENT_ID = "your-client-id"
   GOOGLE_CLIENT_SECRET = "your-client-secret"
   GOOGLE_DEVELOPER_TOKEN = "your-developer-token"
   REDIRECT_URI = "https://your-app-url.streamlit.app/"
   ```

   Replace "your-app-url" with the URL assigned to your Streamlit app.

## Running Locally

To run the application locally:

1. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

2. Create a `.streamlit/secrets.toml` file in your project directory:
   ```toml
   GOOGLE_CLIENT_ID = "your-client-id"
   GOOGLE_CLIENT_SECRET = "your-client-secret"
   GOOGLE_DEVELOPER_TOKEN = "your-developer-token"
   REDIRECT_URI = "http://localhost:8501/"
   ```

3. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

## Google Ads API Setup

Before using this tool, you'll need:

1. **Create a Google Cloud Project**
   - Go to the [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Enable the Google Ads API

2. **Set up OAuth 2.0 Credentials**
   - In the Google Cloud Console, go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" and select "OAuth client ID"
   - Add your Streamlit app URL as an authorized redirect URI

3. **Obtain a Developer Token**
   - Log in to your Google Ads account
   - Go to "Tools & Settings" > "API Center"
   - Apply for a developer token

For more detailed instructions, see the setup guide in the application sidebar.

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

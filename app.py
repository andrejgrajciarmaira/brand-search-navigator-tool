
import streamlit as st
import pandas as pd
import altair as alt
from google_auth_oauthlib.flow import Flow
import os
import json
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import base64
from io import BytesIO
import uuid

# Set page configuration
st.set_page_config(
    page_title="Share of Brand Search Tool",
    page_icon="📊",
    layout="wide"
)

# Define helper functions for authentication
def create_flow():
    # Create the flow instance
    client_config = {
        "web": {
            "client_id": st.secrets["GOOGLE_CLIENT_ID"],
            "client_secret": st.secrets["GOOGLE_CLIENT_SECRET"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [st.secrets.get("REDIRECT_URI", "https://share-of-search-tool.streamlit.app/")]
        }
    }
    
    flow = Flow.from_client_config(
        client_config,
        scopes=["https://www.googleapis.com/auth/adwords"],
        redirect_uri=client_config["web"]["redirect_uris"][0]
    )
    return flow

def generate_auth_url():
    flow = create_flow()
    auth_url, _ = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    return auth_url

def exchange_code(code):
    flow = create_flow()
    flow.fetch_token(code=code)
    credentials = flow.credentials
    return {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes
    }

# Mock function to simulate Google Ads API data retrieval
def get_search_volumes(brands, settings, credentials):
    # In a real app, this would call the Google Ads API
    # For demonstration, we'll generate mock data
    
    results = []
    
    start_date = datetime.strptime(settings["dateFrom"], "%Y-%m-%d")
    end_date = datetime.strptime(settings["dateTo"], "%Y-%m-%d")
    
    # Generate time periods based on granularity
    periods = []
    current_date = start_date
    
    if settings["granularity"] == "monthly":
        while current_date <= end_date:
            periods.append(current_date.strftime("%Y-%m"))
            # Add one month
            month = current_date.month + 1
            year = current_date.year
            if month > 12:
                month = 1
                year += 1
            current_date = current_date.replace(year=year, month=month)
    elif settings["granularity"] == "quarterly":
        while current_date <= end_date:
            quarter = (current_date.month - 1) // 3 + 1
            periods.append(f"{current_date.year}-Q{quarter}")
            # Add one quarter (3 months)
            month = current_date.month + 3
            year = current_date.year
            if month > 12:
                month = month - 12
                year += 1
            current_date = current_date.replace(year=year, month=month)
    else:  # yearly
        while current_date.year <= end_date.year:
            periods.append(str(current_date.year))
            current_date = current_date.replace(year=current_date.year + 1)
    
    for period in periods:
        base_volume = 1000
        total_volume = 0
        period_results = []
        
        for brand in brands:
            if not brand["name"] or not any(k.strip() for k in brand["keywords"]):
                continue
                
            # Calculate volume based on keywords and a random factor
            keywords_count = len([k for k in brand["keywords"] if k.strip()])
            volume = base_volume * keywords_count
            
            # Add some variation and trend
            if "monthly" in settings["granularity"]:
                month_num = int(period.split("-")[1])
                # Seasonal variations
                volume *= (0.8 + (month_num % 12) / 10)
            
            # Add randomness (±30%)
            import random
            volume *= (0.7 + random.random() * 0.6)
            
            # Round to integer
            volume = round(volume)
            total_volume += volume
            
            period_results.append({
                "brand": brand["name"],
                "period": period,
                "volume": volume,
                "share": 0,  # Will calculate after all volumes
                "color": brand["color"]
            })
        
        # Calculate shares
        for result in period_results:
            result["share"] = round(result["volume"] / total_volume * 100, 1) if total_volume > 0 else 0
            results.append(result)
    
    return results

# App title and introduction
st.title("🔍 Share of Brand Search Tool")
st.markdown("""
This tool helps you analyze brand search volumes from Google Ads and visualize market share trends over time.
Compare your brands against competitors to gain insights into search performance.
""")

# Check for authentication
if "code" in st.query_params:
    with st.spinner("Authenticating with Google..."):
        try:
            auth_code = query_params["code"][0]
            token_data = exchange_code(auth_code)
            st.session_state["authenticated"] = True
            st.session_state["token_data"] = token_data
            st.query_params.clear()
            st.success("Authentication successful!")
        except Exception as e:
            st.error(f"Authentication failed: {str(e)}")
            st.session_state["authenticated"] = False

# Initialize session state variables
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if "brands" not in st.session_state:
    st.session_state["brands"] = [
        {"id": str(uuid.uuid4()), "name": "", "keywords": [""], "isOwnBrand": True, "color": "#1f77b4"},
        {"id": str(uuid.uuid4()), "name": "", "keywords": [""], "isOwnBrand": False, "color": "#ff7f0e"}
    ]

if "settings" not in st.session_state:
    st.session_state["settings"] = {
        "location": "United States",
        "language": "English",
        "network": "google",
        "dateFrom": (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"),  # Last year
        "dateTo": datetime.now().strftime("%Y-%m-%d"),
        "granularity": "monthly"
    }

if "results" not in st.session_state:
    st.session_state["results"] = []

if "show_results" not in st.session_state:
    st.session_state["show_results"] = False

# Authentication section
if not st.session_state["authenticated"]:
    st.header("🔑 Google Authentication")
    st.warning("You need to authenticate with Google to use this tool.")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("""
        ### Why do we need Google Authentication?
        This tool uses the Google Ads API to fetch keyword search volume data. You'll need:
        
        1. A Google account with access to Google Ads
        2. A Google Ads Developer Token (for production use)
        
        We use OAuth to securely access your Google Ads data, and we don't store any of your credentials.
        """)
    
    with col2:
        auth_url = generate_auth_url()
        st.markdown(f"""
        <a href="{auth_url}" target="_self">
            <button style="
                background-color: #4285F4;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-weight: bold;
                display: flex;
                align-items: center;
                justify-content: center;
                width: 100%;
                margin-top: 20px;
            ">
                <svg xmlns="http://www.w3.org/2000/svg" height="24" width="24" style="margin-right: 10px;">
                    <path fill="#ffffff" d="M12.545,10.239v3.821h5.445c-0.712,2.315-2.647,3.972-5.445,3.972c-3.332,0-6.033-2.701-6.033-6.032
                    s2.701-6.032,6.033-6.032c1.498,0,2.866,0.549,3.921,1.453l2.814-2.814C17.503,2.988,15.139,2,12.545,2
                    C7.021,2,2.543,6.477,2.543,12s4.478,10,10.002,10c8.396,0,10.249-7.85,9.426-11.748L12.545,10.239z"/>
                </svg>
                Sign in with Google
            </button>
        </a>
        """, unsafe_allow_html=True)

else:
    # Main application interface (after authentication)
    tabs = st.tabs(["Input Parameters", "Results"] if st.session_state["show_results"] else ["Input Parameters"])
    
    with tabs[0]:
        st.header("Brand Configuration")
        
        # Create two columns
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Your Brands")
            
            # Function to add a new brand
            def add_brand(is_own_brand):
                colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", 
                          "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]
                
                brand_count = len([b for b in st.session_state["brands"] if b["isOwnBrand"] == is_own_brand])
                st.session_state["brands"].append({
                    "id": str(uuid.uuid4()),
                    "name": "",
                    "keywords": [""],
                    "isOwnBrand": is_own_brand,
                    "color": colors[brand_count % len(colors)]
                })
            
            # Display own brands
            own_brands = [b for b in st.session_state["brands"] if b["isOwnBrand"]]
            if not own_brands:
                st.info("Add your own brands to track")
            
            for i, brand in enumerate(own_brands):
                with st.expander(f"Brand {i+1}: {brand['name'] or 'Unnamed'}", expanded=brand["name"] == ""):
                    # Brand name
                    new_name = st.text_input("Brand Name", brand["name"], key=f"own_name_{brand['id']}")
                    if new_name != brand["name"]:
                        brand["name"] = new_name
                    
                    # Brand color
                    new_color = st.color_picker("Brand Color", brand["color"], key=f"own_color_{brand['id']}")
                    if new_color != brand["color"]:
                        brand["color"] = new_color
                    
                    # Keywords
                    st.write("Keywords (one per line):")
                    keywords_text = "\n".join(brand["keywords"])
                    new_keywords = st.text_area("", keywords_text, key=f"own_keywords_{brand['id']}")
                    if new_keywords != keywords_text:
                        brand["keywords"] = [k.strip() for k in new_keywords.split("\n") if k.strip()]
                        if not brand["keywords"]:
                            brand["keywords"] = [""]
                    
                    # Remove brand button
                    if st.button("Remove Brand", key=f"remove_own_{brand['id']}"):
                        st.session_state["brands"] = [b for b in st.session_state["brands"] if b["id"] != brand["id"]]
                        st.rerun()
            
            if st.button("➕ Add Your Brand"):
                add_brand(True)
                st.rerun()
            
            st.subheader("Competitor Brands")
            
            competitor_brands = [b for b in st.session_state["brands"] if not b["isOwnBrand"]]
            if not competitor_brands:
                st.info("Add competitor brands to compare")
            
            for i, brand in enumerate(competitor_brands):
                with st.expander(f"Competitor {i+1}: {brand['name'] or 'Unnamed'}", expanded=brand["name"] == ""):
                    # Brand name
                    new_name = st.text_input("Brand Name", brand["name"], key=f"comp_name_{brand['id']}")
                    if new_name != brand["name"]:
                        brand["name"] = new_name
                    
                    # Brand color
                    new_color = st.color_picker("Brand Color", brand["color"], key=f"comp_color_{brand['id']}")
                    if new_color != brand["color"]:
                        brand["color"] = new_color
                    
                    # Keywords
                    st.write("Keywords (one per line):")
                    keywords_text = "\n".join(brand["keywords"])
                    new_keywords = st.text_area("", keywords_text, key=f"comp_keywords_{brand['id']}")
                    if new_keywords != keywords_text:
                        brand["keywords"] = [k.strip() for k in new_keywords.split("\n") if k.strip()]
                        if not brand["keywords"]:
                            brand["keywords"] = [""]
                    
                    # Remove brand button
                    if st.button("Remove Brand", key=f"remove_comp_{brand['id']}"):
                        st.session_state["brands"] = [b for b in st.session_state["brands"] if b["id"] != brand["id"]]
                        st.rerun()
            
            if st.button("➕ Add Competitor Brand"):
                add_brand(False)
                st.rerun()
        
        with col2:
            st.subheader("Search Parameters")
            
            # Location
            locations = ["United States", "United Kingdom", "Canada", "Australia", "Germany", 
                         "France", "Spain", "Italy", "Japan", "India", "Brazil", "Mexico", "Netherlands"]
            st.session_state["settings"]["location"] = st.selectbox(
                "Location", 
                options=locations,
                index=locations.index(st.session_state["settings"]["location"])
            )
            
            # Language
            languages = ["English", "Spanish", "French", "German", "Italian", "Portuguese", 
                       "Japanese", "Chinese", "Russian", "Arabic", "Hindi", "Dutch"]
            st.session_state["settings"]["language"] = st.selectbox(
                "Language",
                options=languages,
                index=languages.index(st.session_state["settings"]["language"])
            )
            
            # Network
            networks = [
                ("google", "Google Search"),
                ("google_search_partners", "Google Search Partners"),
                ("both", "Both Networks")
            ]
            network_options = [n[1] for n in networks]
            current_network_index = next((i for i, n in enumerate(networks) if n[0] == st.session_state["settings"]["network"]), 0)
            selected_network = st.selectbox(
                "Network",
                options=network_options,
                index=current_network_index
            )
            st.session_state["settings"]["network"] = networks[network_options.index(selected_network)][0]
            
            # Date Range
            col_date1, col_date2 = st.columns(2)
            
            with col_date1:
                start_date = st.date_input(
                    "From Date",
                    value=datetime.strptime(st.session_state["settings"]["dateFrom"], "%Y-%m-%d"),
                    max_value=datetime.now()
                )
                st.session_state["settings"]["dateFrom"] = start_date.strftime("%Y-%m-%d")
            
            with col_date2:
                end_date = st.date_input(
                    "To Date",
                    value=datetime.strptime(st.session_state["settings"]["dateTo"], "%Y-%m-%d"),
                    min_value=start_date,
                    max_value=datetime.now()
                )
                st.session_state["settings"]["dateTo"] = end_date.strftime("%Y-%m-%d")
            
            # Data Granularity
            st.session_state["settings"]["granularity"] = st.radio(
                "Data Granularity",
                options=["monthly", "quarterly", "yearly"],
                index=["monthly", "quarterly", "yearly"].index(st.session_state["settings"]["granularity"]),
                format_func=lambda x: x.title()
            )
            
            # Note about data availability
            st.info("Note: Google Ads API returns data only for available periods (typically max. 4-5 years back), depending on when you select the 'From date'.")
            
            # Generate Analysis Button
            if st.button("📊 Generate Share of Search Analysis", type="primary", use_container_width=True):
                # Validate form
                valid_brands = [b for b in st.session_state["brands"] 
                               if b["name"] and any(k.strip() for k in b["keywords"])]
                
                if not valid_brands:
                    st.error("Please add at least one brand with keywords")
                elif start_date > end_date:
                    st.error("Start date must be before end date")
                else:
                    with st.spinner("Generating analysis..."):
                        # In a real app, this would use the Google Ads API
                        results = get_search_volumes(
                            st.session_state["brands"],
                            st.session_state["settings"],
                            st.session_state.get("token_data")
                        )
                        st.session_state["results"] = results
                        st.session_state["show_results"] = True
                        st.rerun()
    
    # Results tab (only shown when results are available)
    if st.session_state["show_results"] and len(tabs) > 1:
        with tabs[1]:
            st.header("Share of Search Results")
            
            if not st.session_state["results"]:
                st.warning("No results to display. Generate an analysis first.")
            else:
                # Convert results to DataFrame for easier manipulation
                df = pd.DataFrame(st.session_state["results"])
                
                # Get unique brands and periods
                brands = df["brand"].unique().tolist()
                periods = df["period"].unique().tolist()
                
                # Create tabs for different visualizations
                viz_tabs = st.tabs(["Share of Search (%)", "Search Volume", "Data Table"])
                
                with viz_tabs[0]:
                    st.subheader("Share of Search by Brand")
                    
                    # Create a stacked area chart for share percentages
                    fig = px.area(
                        df, 
                        x="period", 
                        y="share", 
                        color="brand",
                        color_discrete_map={brand_name: brand["color"] 
                                            for brand in st.session_state["brands"] 
                                            for brand_name in [brand["name"]] 
                                            if brand_name in brands},
                        title="Share of Search Over Time",
                        labels={"period": "Time Period", "share": "Share (%)", "brand": "Brand"},
                        groupnorm='percent'  # Ensures the values sum to 100%
                    )
                    
                    # Customize layout
                    fig.update_layout(
                        xaxis_title="Time Period",
                        yaxis_title="Share of Search (%)",
                        legend_title="Brands",
                        hovermode="x"
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Add download button for the chart
                    buffer = BytesIO()
                    fig.write_image(buffer, format="png", width=1200, height=600, scale=2)
                    buffer.seek(0)
                    
                    st.download_button(
                        label="Download Chart as PNG",
                        data=buffer,
                        file_name="share_of_search_chart.png",
                        mime="image/png"
                    )
                
                with viz_tabs[1]:
                    st.subheader("Search Volume by Brand")
                    
                    # Create a stacked bar chart for absolute volumes
                    fig = px.bar(
                        df,
                        x="period",
                        y="volume",
                        color="brand",
                        color_discrete_map={brand_name: brand["color"] 
                                            for brand in st.session_state["brands"]
                                            for brand_name in [brand["name"]]
                                            if brand_name in brands},
                        title="Search Volume Over Time",
                        labels={"period": "Time Period", "volume": "Search Volume", "brand": "Brand"},
                        barmode="stack"
                    )
                    
                    # Customize layout
                    fig.update_layout(
                        xaxis_title="Time Period",
                        yaxis_title="Search Volume",
                        legend_title="Brands",
                        hovermode="x"
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Add download button for the chart
                    buffer = BytesIO()
                    fig.write_image(buffer, format="png", width=1200, height=600, scale=2)
                    buffer.seek(0)
                    
                    st.download_button(
                        label="Download Chart as PNG",
                        data=buffer,
                        file_name="search_volume_chart.png",
                        mime="image/png"
                    )
                
                with viz_tabs[2]:
                    st.subheader("Raw Data")
                    
                    # Prepare data for display
                    display_df = df.pivot_table(
                        index="period", 
                        columns="brand", 
                        values=["volume", "share"],
                        aggfunc="sum"
                    ).reset_index()
                    
                    # Format column names
                    display_df.columns = [f"{col[1]} ({col[0]})" if col[1] else "Period" for col in display_df.columns]
                    
                    # Show the data table
                    st.dataframe(display_df, use_container_width=True)
                    
                    # Download as CSV button
                    csv = display_df.to_csv(index=False)
                    st.download_button(
                        label="Download Data as CSV",
                        data=csv,
                        file_name="share_of_search_data.csv",
                        mime="text/csv"
                    )
                
                # Reset button to go back to input
                if st.button("Start New Analysis", type="secondary"):
                    st.session_state["show_results"] = False
                    st.rerun()

# Show the setup guide in the sidebar
with st.sidebar:
    st.title("Setup Guide")
    
    with st.expander("Prerequisites", expanded=False):
        st.markdown("""
        Before using this tool, you'll need:
        
        - A Google Ads account with admin access
        - A Google Cloud Platform account
        - A Google Ads API developer token (for production use)
        """)
    
    with st.expander("Google Cloud Setup", expanded=False):
        st.markdown("""
        1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
        2. Create a new project or select an existing one
        3. Enable the Google Ads API for your project:
           - Navigate to "APIs & Services" > "Library"
           - Search for "Google Ads API"
           - Click "Enable"
        4. Create OAuth credentials:
           - Go to "APIs & Services" > "Credentials"
           - Click "Create Credentials" and select "OAuth client ID"
           - Select "Web application" as the application type
           - Add your Streamlit app URL to the authorized redirect URIs
        """)
    
    with st.expander("Google Ads API Setup", expanded=False):
        st.markdown("""
        1. Log in to your Google Ads account at [ads.google.com](https://ads.google.com)
        2. Click the tools icon in the upper right corner
        3. Under "Setup," select "API Center"
        4. Apply for a developer token by providing the required information

        For testing purposes, you can use a test account which provides immediate access with limited functionality.
        """)
    
    with st.expander("Streamlit Secrets Setup", expanded=False):
        st.markdown("""
        When deploying your app on Streamlit Cloud, add these secrets in the Streamlit dashboard:
        
        ```toml
        # .streamlit/secrets.toml format
        GOOGLE_CLIENT_ID = "your-client-id"
        GOOGLE_CLIENT_SECRET = "your-client-secret"
        GOOGLE_DEVELOPER_TOKEN = "your-developer-token"
        REDIRECT_URI = "https://your-app-url.streamlit.app/"
        ```
        """)
    
    with st.expander("Troubleshooting", expanded=False):
        st.markdown("""
        **Common Issues:**
        
        - **Authentication Failed**: Ensure your client ID, client secret, and redirect URI are correct.
        - **API Quota Exceeded**: Google Ads API has usage quotas. If you exceed them, you'll need to wait or request a quota increase.
        - **No Data Being Retrieved**: Ensure that your Google Ads account has active campaigns and that you're using the correct customer ID.
        
        For additional help:
        - Check the [Google Ads API Documentation](https://developers.google.com/google-ads/api/docs/start)
        - Join the [Google Ads API Forum](https://groups.google.com/g/adwords-api)
        """)

    st.markdown("---")
    st.caption("Share of Brand Search Tool v1.0")

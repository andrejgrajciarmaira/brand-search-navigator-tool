import streamlit as st
import pandas as pd
import altair as alt
import os
import json
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import base64
from io import BytesIO
import uuid
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

# Set page configuration
st.set_page_config(
    page_title="Share of Brand Search Tool",
    page_icon="📊",
    layout="wide"
)

# Initialize Google Ads client with credentials from secrets
@st.cache_resource
def get_google_ads_client():
    """Create and return a Google Ads API client using credentials from Streamlit secrets."""
    try:
        # Load credentials from Streamlit secrets
        credentials = {
            "developer_token": st.secrets["GOOGLE_DEVELOPER_TOKEN"],
            "client_id": st.secrets["GOOGLE_CLIENT_ID"],
            "client_secret": st.secrets["GOOGLE_CLIENT_SECRET"],
            "refresh_token": st.secrets["GOOGLE_REFRESH_TOKEN"],
            "login_customer_id": st.secrets["GOOGLE_LOGIN_CUSTOMER_ID"],
            "use_proto_plus": True
        }
        
        # Create the Google Ads client
        client = GoogleAdsClient.load_from_dict(credentials)
        return client
    except Exception as e:
        st.error(f"Error initializing Google Ads client: {str(e)}")
        return None

# Dictionary of language codes and their criterion IDs
LANGUAGE_MAPPING = {
    "All Languages": "all",
    "Arabic": "1019",
    "Bengali": "1056",
    "Bulgarian": "1020",
    "Catalan": "1038",
    "Chinese (Simplified)": "1017",
    "Chinese (Traditional)": "1018",
    "Croatian": "1039",
    "Czech": "1021",
    "Danish": "1009",
    "Dutch": "1010",
    "English": "1000",
    "Estonian": "1043",
    "Filipino": "1042",
    "Finnish": "1011",
    "French": "1002",
    "German": "1001",
    "Greek": "1022",
    "Gujarati": "1072",
    "Hebrew": "1027",
    "Hindi": "1023",
    "Hungarian": "1024",
    "Icelandic": "1026",
    "Indonesian": "1057",
    "Italian": "1004",
    "Japanese": "1005",
    "Kannada": "1073",
    "Korean": "1012",
    "Latvian": "1028",
    "Lithuanian": "1029",
    "Malay": "1102",
    "Malayalam": "1098",
    "Marathi": "1101",
    "Norwegian": "1013",
    "Persian": "1064",
    "Polish": "1030",
    "Portuguese": "1014",
    "Romanian": "1032",
    "Russian": "1031",
    "Serbian": "1035",
    "Slovak": "1033",
    "Slovenian": "1034",
    "Spanish": "1003",
    "Swedish": "1015",
    "Tamil": "1097",
    "Telugu": "1099",
    "Thai": "1044",
    "Turkish": "1016",
    "Ukrainian": "1036",
    "Urdu": "1076",
    "Vietnamese": "1066"
}

# Dictionary of countries and their geo target IDs
COUNTRY_MAPPING = {
    "All Countries": "all",
    "Afghanistan": "2004",
    "Albania": "2008",
    "Algeria": "2012",
    "American Samoa": "2016",
    "Andorra": "2020",
    "Angola": "2024",
    "Anguilla": "2660",
    "Antarctica": "2010",
    "Antigua and Barbuda": "2028",
    "Argentina": "2032",
    "Armenia": "2051",
    "Aruba": "2533",
    "Australia": "2036",
    "Austria": "2040",
    "Azerbaijan": "2031",
    "Bahamas": "2044",
    "Bahrain": "2048",
    "Bangladesh": "2050",
    "Barbados": "2052",
    "Belarus": "2112",
    "Belgium": "2056",
    "Belize": "2084",
    "Benin": "2204",
    "Bermuda": "2060",
    "Bhutan": "2064",
    "Bolivia": "2068",
    "Bosnia and Herzegovina": "2070",
    "Botswana": "2072",
    "Bouvet Island": "2074",
    "Brazil": "2076",
    "British Indian Ocean Territory": "2086",
    "Brunei": "2096",
    "Bulgaria": "2100",
    "Burkina Faso": "2854",
    "Burundi": "2108",
    "Cambodia": "2116",
    "Cameroon": "2120",
    "Canada": "2124",
    "Cape Verde": "2132",
    "Cayman Islands": "2136",
    "Central African Republic": "2140",
    "Chad": "2148",
    "Chile": "2152",
    "China": "2156",
    "Christmas Island": "2162",
    "Cocos (Keeling) Islands": "2166",
    "Colombia": "2170",
    "Comoros": "2174",
    "Congo": "2178",
    "Cook Islands": "2184",
    "Costa Rica": "2188",
    "Croatia": "2191",
    "Cuba": "2192",
    "Cyprus": "2196",
    "Czech Republic": "2203",
    "Denmark": "2208",
    "Djibouti": "2262",
    "Dominica": "2212",
    "Dominican Republic": "2214",
    "East Timor": "2626",
    "Ecuador": "2218",
    "Egypt": "2818",
    "El Salvador": "2222",
    "Equatorial Guinea": "2226",
    "Eritrea": "2232",
    "Estonia": "2233",
    "Ethiopia": "2231",
    "Falkland Islands": "2238",
    "Faroe Islands": "2234",
    "Fiji": "2242",
    "Finland": "2246",
    "France": "2250",
    "French Guiana": "2254",
    "French Polynesia": "2258",
    "French Southern Territories": "2260",
    "Gabon": "2266",
    "Gambia": "2270",
    "Georgia": "2268",
    "Germany": "2276",
    "Ghana": "2288",
    "Gibraltar": "2292",
    "Greece": "2300",
    "Greenland": "2304",
    "Grenada": "2308",
    "Guadeloupe": "2312",
    "Guam": "2316",
    "Guatemala": "2320",
    "Guinea": "2324",
    "Guinea-Bissau": "2624",
    "Guyana": "2328",
    "Haiti": "2332",
    "Heard Island and McDonald Islands": "2334",
    "Honduras": "2340",
    "Hong Kong": "2344",
    "Hungary": "2348",
    "Iceland": "2352",
    "India": "2356",
    "Indonesia": "2360",
    "Iran": "2364",
    "Iraq": "2368",
    "Ireland": "2372",
    "Israel": "2376",
    "Italy": "2380",
    "Ivory Coast": "2384",
    "Jamaica": "2388",
    "Japan": "2392",
    "Jordan": "2400",
    "Kazakhstan": "2398",
    "Kenya": "2404",
    "Kiribati": "2296",
    "Kuwait": "2414",
    "Kyrgyzstan": "2417",
    "Laos": "2418",
    "Latvia": "2428",
    "Lebanon": "2422",
    "Lesotho": "2426",
    "Liberia": "2430",
    "Libya": "2434",
    "Liechtenstein": "2438",
    "Lithuania": "2440",
    "Luxembourg": "2442",
    "Macau": "2446",
    "Macedonia": "2807",
    "Madagascar": "2450",
    "Malawi": "2454",
    "Malaysia": "2458",
    "Maldives": "2462",
    "Mali": "2466",
    "Malta": "2470",
    "Marshall Islands": "2584",
    "Martinique": "2474",
    "Mauritania": "2478",
    "Mauritius": "2480",
    "Mayotte": "2175",
    "Mexico": "2484",
    "Micronesia": "2583",
    "Moldova": "2498",
    "Monaco": "2492",
    "Mongolia": "2496",
    "Montenegro": "2499",
    "Montserrat": "2500",
    "Morocco": "2504",
    "Mozambique": "2508",
    "Myanmar": "2104",
    "Namibia": "2516",
    "Nauru": "2520",
    "Nepal": "2524",
    "Netherlands": "2528",
    "Netherlands Antilles": "2530",
    "New Caledonia": "2540",
    "New Zealand": "2554",
    "Nicaragua": "2558",
    "Niger": "2562",
    "Nigeria": "2566",
    "Niue": "2570",
    "Norfolk Island": "2574",
    "North Korea": "2408",
    "Northern Mariana Islands": "2580",
    "Norway": "2578",
    "Oman": "2512",
    "Pakistan": "2586",
    "Palau": "2585",
    "Palestine": "2275",
    "Panama": "2591",
    "Papua New Guinea": "2598",
    "Paraguay": "2600",
    "Peru": "2604",
    "Philippines": "2608",
    "Pitcairn": "2612",
    "Poland": "2616",
    "Portugal": "2620",
    "Puerto Rico": "2630",
    "Qatar": "2634",
    "Reunion": "2638",
    "Romania": "2642",
    "Russia": "2643",
    "Rwanda": "2646",
    "Saint Helena": "2654",
    "Saint Kitts and Nevis": "2659",
    "Saint Lucia": "2662",
    "Saint Pierre and Miquelon": "2666",
    "Saint Vincent and the Grenadines": "2670",
    "Samoa": "2882",
    "San Marino": "2674",
    "Sao Tome and Principe": "2678",
    "Saudi Arabia": "2682",
    "Senegal": "2686",
    "Serbia": "2688",
    "Seychelles": "2690",
    "Sierra Leone": "2694",
    "Singapore": "2702",
    "Slovakia": "2703",
    "Slovenia": "2705",
    "Solomon Islands": "2090",
    "Somalia": "2706",
    "South Africa": "2710",
    "South Georgia and the South Sandwich Islands": "2239",
    "South Korea": "2410",
    "Spain": "2724",
    "Sri Lanka": "2144",
    "Sudan": "2736",
    "Suriname": "2740",
    "Svalbard and Jan Mayen": "2744",
    "Swaziland": "2748",
    "Sweden": "2752",
    "Switzerland": "2756",
    "Syria": "2760",
    "Taiwan": "2158",
    "Tajikistan": "2762",
    "Tanzania": "2834",
    "Thailand": "2764",
    "Togo": "2768",
    "Tokelau": "2772",
    "Tonga": "2776",
    "Trinidad and Tobago": "2780",
    "Tunisia": "2788",
    "Turkey": "2792",
    "Turkmenistan": "2795",
    "Turks and Caicos Islands": "2796",
    "Tuvalu": "2798",
    "Uganda": "2800",
    "Ukraine": "2804",
    "United Arab Emirates": "2784",
    "United Kingdom": "2826",
    "United States": "2840",
    "United States Minor Outlying Islands": "2581",
    "Uruguay": "2858",
    "Uzbekistan": "2860",
    "Vanuatu": "2548",
    "Vatican": "2336",
    "Venezuela": "2862",
    "Vietnam": "2704",
    "Virgin Islands, British": "2092",
    "Virgin Islands, U.S.": "2850",
    "Wallis and Futuna": "2876",
    "Western Sahara": "2732",
    "Yemen": "2887",
    "Zambia": "2894",
    "Zimbabwe": "2716"
}

# Function to get search volumes from Google Ads API using GenerateKeywordHistoricalMetrics
def get_search_volumes(brands, settings, client):
    """Retrieve search volume data from Google Ads API for specified brands and keywords using historical metrics."""
    if not client:
        st.error("Google Ads client not initialized. Please check your credentials.")
        return []
    
    results = []
    
    # Parse date range from settings
    start_date = datetime.strptime(settings["dateFrom"], "%Y-%m-%d")
    end_date = datetime.strptime(settings["dateTo"], "%Y-%m-%d")
    
    # Generate time periods based on granularity
    periods = []
    current_date = start_date
    
    if settings["granularity"] == "monthly":
        while current_date <= end_date:
            # Store the display label with the correct month name
            display_label = current_date.strftime("%Y-%m")
            
            # For API matching, we need to adjust for the month offset
            # Google Ads API reports data for the previous month
            # Create a copy of current_date for API querying
            api_date = current_date - timedelta(days=28)  # Subtract approximately one month
            api_month = api_date.month
            api_year = api_date.year
            
            periods.append((api_year, api_month, display_label))
            
            # Add one month
            month = current_date.month + 1
            year = current_date.year
            if month > 12:
                month = 1
                year += 1
            current_date = current_date.replace(year=year, month=month, day=1)
            
    elif settings["granularity"] == "quarterly":
        while current_date <= end_date:
            quarter = ((current_date.month - 1) // 3) + 1
            display_label = f"{current_date.year}-Q{quarter}"
            
            # For quarterly data, we still need to adjust for the month offset
            # but we're working with quarters
            # Create a copy of current_date for API querying
            api_date = current_date - timedelta(days=28)  # Subtract approximately one month
            api_quarter = ((api_date.month - 1) // 3) + 1
            api_year = api_date.year
            
            periods.append((api_year, api_quarter, display_label))
            
            # Add one quarter (3 months)
            month = current_date.month + 3
            year = current_date.year
            if month > 12:
                month = month - 12
                year += 1
            current_date = current_date.replace(year=year, month=month, day=1)
            
    else:  # yearly
        while current_date.year <= end_date.year:
            display_label = str(current_date.year)
            
            # For yearly data, we still need to adjust for the month offset
            # Create a copy of current_date for API querying
            api_date = current_date - timedelta(days=28)  # Subtract approximately one month
            api_year = api_date.year
            
            periods.append((api_year, None, display_label))
            current_date = current_date.replace(year=current_date.year + 1, month=1, day=1)
    
    # Get customer ID from secrets
    customer_id = st.secrets["GOOGLE_CUSTOMER_ID"]
    
    # Get language and location IDs
    language_id = LANGUAGE_MAPPING.get(settings["language"])
    location_id = COUNTRY_MAPPING.get(settings["location"])
    
    # Create Google Ads service
    googleads_service = client.get_service("GoogleAdsService")
    
    # Create keyword plan idea service
    keyword_plan_idea_service = client.get_service("KeywordPlanIdeaService")
    
    # Process each period
    for period_year, period_month_or_quarter, period_label in periods:
        period_results = {}
        
        # Process each brand
        for brand in brands:
            # Skip brands without keywords
            if not brand.get("keywords"):
                continue
                
            brand_name = brand["name"]
            brand_keywords = brand["keywords"].split(",")
            brand_keywords = [kw.strip() for kw in brand_keywords if kw.strip()]
            
            if not brand_keywords:
                continue
                
            brand_volume = 0
            
            try:
                # Process each keyword for this brand
                for keyword in brand_keywords:
                    # Create request for historical metrics
                    request = client.get_type("GenerateKeywordHistoricalMetricsRequest")
                    request.customer_id = customer_id
                    request.keywords.append(keyword)
                    
                    # Add geo target constants if not "All Countries"
                    if settings["location"] != "All Countries":
                        request.geo_target_constants.append(googleads_service.geo_target_constant_path(location_id))
                    
                    # Set language if not "All Languages"
                    if settings["language"] != "All Languages":
                        request.language = googleads_service.language_constant_path(language_id)
                    
                    # Set network
                    if settings["network"] == "GOOGLE_SEARCH":
                        request.keyword_plan_network = client.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH
                    else:  # GOOGLE_SEARCH_AND_PARTNERS
                        request.keyword_plan_network = client.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH_AND_PARTNERS
                    
                    # Execute the request
                    response = keyword_plan_idea_service.generate_keyword_historical_metrics(request=request)
                    
                    # Process each result
                    for result in response.results:
                        keyword_metrics = result.keyword_metrics
                        
                        # For monthly granularity, find the specific month's data
                        if settings["granularity"] == "monthly" and period_month_or_quarter is not None:
                            for monthly_search_volume in keyword_metrics.monthly_search_volumes:
                                if (monthly_search_volume.year == period_year and 
                                    monthly_search_volume.month.value == period_month_or_quarter):
                                    brand_volume += monthly_search_volume.monthly_searches
                                    break
                        
                        # For quarterly granularity
                        elif settings["granularity"] == "quarterly" and period_month_or_quarter is not None:
                            quarter_start_month = (period_month_or_quarter - 1) * 3 + 1
                            quarter_end_month = quarter_start_month + 2
                            
                            for monthly_search_volume in keyword_metrics.monthly_search_volumes:
                                if (monthly_search_volume.year == period_year and 
                                    quarter_start_month <= monthly_search_volume.month.value <= quarter_end_month):
                                    brand_volume += monthly_search_volume.monthly_searches
                        
                        # For yearly granularity
                        elif settings["granularity"] == "yearly":
                            for monthly_search_volume in keyword_metrics.monthly_search_volumes:
                                if monthly_search_volume.year == period_year:
                                    brand_volume += monthly_search_volume.monthly_searches
            
            except GoogleAdsException as ex:
                st.error(f"Google Ads API error: {ex}")
                for error in ex.failure.errors:
                    st.error(f"Error details: {error.message}")
                return []
            
            # Store the brand volume for this period
            period_results[brand_name] = brand_volume
        
        # Calculate total volume for this period
        total_volume = sum(period_results.values())
        
        # Calculate market share for each brand
        for brand_name, brand_volume in period_results.items():
            market_share = (brand_volume / total_volume * 100) if total_volume > 0 else 0
            results.append({
                "period": period_label,
                "brand": brand_name,
                "search_volume": brand_volume,
                "market_share": market_share
            })
    
    return results

# Function to generate a download link for a dataframe
def get_csv_download_link(df, filename="data.csv"):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'data:file/csv;base64,{b64}'
    return href

# Function to convert Plotly figure to HTML for download
def plotly_fig_to_html(fig):
    """Convert a Plotly figure to HTML string for download."""
    return fig.to_html(include_plotlyjs='cdn', full_html=True)

# Main app layout
def main():
    # Add custom CSS
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        margin-bottom: 1rem;
    }
    .section-header {
        font-size: 1.5rem;
        color: #333;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    .info-text {
        font-size: 1rem;
        color: #555;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # App header
    st.markdown('<h1 class="main-header">Brand Search Navigator</h1>', unsafe_allow_html=True)
    st.markdown('<p class="info-text">Analyze brand search volumes and market share trends over time.</p>', unsafe_allow_html=True)
    
    # Initialize session state for brands if not exists
    if 'brands' not in st.session_state:
        st.session_state.brands = [{"name": "", "keywords": ""}]
    
    if 'current_fig' not in st.session_state:
        st.session_state.current_fig = None
    
    # Create tabs
    tab1, tab2 = st.tabs(["Brand Analysis", "About"])
    
    with tab1:
        # Create columns for the form
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown('<h2 class="section-header">Brand Configuration</h2>', unsafe_allow_html=True)
            
            # Brand inputs
            for i, brand in enumerate(st.session_state.brands):
                cols = st.columns([3, 7, 1])
                with cols[0]:
                    brand_name = st.text_input(f"Brand {i+1} Name", brand["name"], key=f"brand_name_{i}")
                with cols[1]:
                    brand_keywords = st.text_input(f"Brand {i+1} Keywords (comma-separated)", brand["keywords"], key=f"brand_keywords_{i}")
                with cols[2]:
                    if i > 0 and st.button("Remove", key=f"remove_{i}"):
                        st.session_state.brands.pop(i)
                        st.rerun()
                
                # Update session state
                st.session_state.brands[i]["name"] = brand_name
                st.session_state.brands[i]["keywords"] = brand_keywords
            
            # Add brand button
            if st.button("Add Brand"):
                st.session_state.brands.append({"name": "", "keywords": ""})
                st.rerun()
        
        with col2:
            st.markdown('<h2 class="section-header">Settings</h2>', unsafe_allow_html=True)
            
            # Date range
            date_from = st.date_input("From Date", datetime.now() - timedelta(days=365))
            date_to = st.date_input("To Date", datetime.now())
            
            # Granularity
            granularity = st.selectbox("Time Granularity", ["monthly", "quarterly", "yearly"])
            
            # Language
            language = st.selectbox("Language", list(LANGUAGE_MAPPING.keys()))
            
            # Location
            location = st.selectbox("Location", list(COUNTRY_MAPPING.keys()))
            
            # Network
            networks = [
                ("GOOGLE_SEARCH", "Google Search"),
                ("GOOGLE_SEARCH_AND_PARTNERS", "Google Search + Search Partners")
            ]
            network = st.selectbox("Network", [n[0] for n in networks], format_func=lambda x: dict(networks)[x])
        
        # Collect settings
        settings = {
            "dateFrom": date_from.strftime("%Y-%m-%d"),
            "dateTo": date_to.strftime("%Y-%m-%d"),
            "granularity": granularity,
            "language": language,
            "location": location,
            "network": network
        }
        
        # Run analysis button
        if st.button("Run Analysis"):
            # Validate inputs
            valid_brands = [b for b in st.session_state.brands if b["name"] and b["keywords"]]
            
            if not valid_brands:
                st.error("Please add at least one brand with name and keywords.")
            else:
                # Initialize Google Ads client
                client = get_google_ads_client()
                
                # Get search volumes
                with st.spinner("Fetching data from Google Ads API..."):
                    results = get_search_volumes(valid_brands, settings, client)
                
                if results:
                    # Convert to dataframe
                    df = pd.DataFrame(results)
                    
                    # Store in session state
                    st.session_state.results_df = df
                    
                    # Display results
                    st.success("Analysis complete!")
                    
                    # Create tabs for different visualizations
                    viz_tab1, viz_tab2, viz_tab3 = st.tabs(["Share of Search", "Search Volume", "Data Table"])
                    
                    with viz_tab1:
                        # Create market share chart
                        fig = px.line(df, x="period", y="market_share", color="brand", 
                                     title="Brand Market Share Over Time",
                                     labels={"period": "Time Period", "market_share": "Market Share (%)", "brand": "Brand"},
                                     markers=True)
                        fig.update_layout(yaxis_ticksuffix="%")
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Store current figure in session state
                        st.session_state.current_fig = fig
                        st.session_state.current_view = "share"
                    
                    with viz_tab2:
                        # Create search volume chart
                        fig = px.line(df, x="period", y="search_volume", color="brand", 
                                     title="Brand Search Volume Over Time",
                                     labels={"period": "Time Period", "search_volume": "Search Volume", "brand": "Brand"},
                                     markers=True)
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Store current figure in session state
                        st.session_state.current_fig = fig
                        st.session_state.current_view = "volume"
                    
                    with viz_tab3:
                        # Display data table
                        st.dataframe(df)
                        st.session_state.current_view = "table"
                    
                    # Export options
                    st.markdown("### Export Options")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # CSV download
                        csv_link = get_csv_download_link(df)
                        st.markdown(f'<a href="{csv_link}" download="brand_search_data.csv">Download CSV</a>', unsafe_allow_html=True)
                    
                    with col2:
                        # Chart download (HTML)
                        if st.session_state.current_fig and st.session_state.current_view != "table":
                            html_str = plotly_fig_to_html(st.session_state.current_fig)
                            b64 = base64.b64encode(html_str.encode()).decode()
                            href = f'data:text/html;base64,{b64}'
                            st.markdown(f'<a href="{href}" download="brand_search_chart.html">Download Interactive Chart (HTML)</a>', unsafe_allow_html=True)
                        else:
                            st.info("Chart export is available when viewing Share of Search or Search Volume visualizations.")
                else:
                    st.error("No data returned. Please check your inputs and try again.")
    
    with tab2:
        st.markdown('<h2 class="section-header">About Brand Search Navigator</h2>', unsafe_allow_html=True)
        st.markdown("""
        This tool helps you analyze brand search volumes and market share trends over time using data from Google Ads Keyword Planner.
        
        ### How to use:
        1. Add brands and their associated keywords
        2. Configure settings (date range, granularity, language, location)
        3. Click "Run Analysis" to fetch data from Google Ads API
        4. View results in different visualizations
        5. Export data as needed
        
        ### Data Source:
        The tool uses the Google Ads API to fetch historical search volume data for the specified keywords.
        
        ### Privacy:
        All data is processed securely and not shared with third parties.
        """)

if __name__ == "__main__":
    main()

import streamlit as st
import pandas as pd
import altair as alt
import calendar
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

# Function to get search volumes from Google Ads API using GenerateKeywordIdeas
def get_search_volumes(brands, settings, client):
    """Retrieve search volume data from Google Ads API for specified brands and keywords using Keyword Ideas API."""
    if not client:
        st.error("Google Ads client not initialized. Please check your credentials.")
        return []
    
    results = []
    
    # Parse date range from settings
    start_date = datetime.strptime(settings["dateFrom"], "%Y-%m")
    end_date = datetime.strptime(settings["dateTo"], "%Y-%m")
    
    # Generate time periods based on granularity
    periods = []
    current_date = start_date
    
    if settings["granularity"] == "monthly":
        while current_date <= end_date:
            periods.append((current_date.year, current_date.month, current_date.strftime("%Y-%m")))
            # Add one month
            month = current_date.month + 1
            year = current_date.year
            if month > 12:
                month = 1
                year += 1
            current_date = current_date.replace(year=year, month=month, day=1)
    elif settings["granularity"] == "quarterly":
        while current_date <= end_date:
            quarter = (current_date.month - 1) // 3 + 1
            # Include incomplete quarters
            periods.append((current_date.year, quarter, f"{current_date.year}-Q{quarter}"))
            # Add one quarter (3 months)
            month = current_date.month + 3
            year = current_date.year
            if month > 12:
                month = month - 12
                year += 1
            current_date = current_date.replace(year=year, month=month, day=1)
    else:  # yearly
        while current_date.year <= end_date.year:
            # Include incomplete years
            periods.append((current_date.year, None, str(current_date.year)))
            current_date = current_date.replace(year=current_date.year + 1, month=1, day=1)
    
    # Get location ID
    location_id = COUNTRY_MAPPING.get(settings["location"], "2840")  # Default to US if not found
    
    # Get customer ID from secrets
    customer_id = st.secrets["GOOGLE_CUSTOMER_ID"]
    
    # Process each brand and its keywords
    for brand in brands:
        if not brand["name"] or not any(k.strip() for k in brand["keywords"]):
            continue
        
        brand_keywords = [k.strip() for k in brand["keywords"] if k.strip()]
        
        try:
            # Create keyword plan idea service
            keyword_plan_idea_service = client.get_service("KeywordPlanIdeaService")
            googleads_service = client.get_service("GoogleAdsService")
            
            # Create request for keyword ideas
            request = client.get_type("GenerateKeywordIdeasRequest")
            request.customer_id = customer_id
            
            # Set up keyword seed
            request.keyword_seed.keywords.extend(brand_keywords)
            
            # Add geo target constants if not "All Countries"
            if settings["location"] != "All Countries":
                request.geo_target_constants.append(googleads_service.geo_target_constant_path(location_id))
            
            # Set network based on settings
            if settings["network"] == "GOOGLE_SEARCH":
                request.keyword_plan_network = client.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH
            else:  # GOOGLE_SEARCH_AND_PARTNERS
                request.keyword_plan_network = client.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH_AND_PARTNERS

            historical_metrics_options = request.historical_metrics_options
            year_month_range = historical_metrics_options.year_month_range

            historical_metrics_options = request.historical_metrics_options
            year_month_range = historical_metrics_options.year_month_range

            year_month_range.start.year = start_date.year
            month_enum_name = calendar.month_name[start_date.month].upper()
            year_month_range.start.month = client.enums.MonthOfYearEnum[month_enum_name]

            # End date +1 logic
            end_month = end_date.month + 1
            end_year = end_date.year
            if end_month > 12:
                end_month = 1
                end_year += 1
            end_month_enum_name = calendar.month_name[end_month].upper()
            year_month_range.end.year = end_year
            year_month_range.end.month = client.enums.MonthOfYearEnum[end_month_enum_name]
            
            # Execute the request
            response = keyword_plan_idea_service.generate_keyword_ideas(request=request)
            
            # Process the response for each period
            for period_year, period_month_or_quarter, period_label in periods:
                brand_volume = 0
                
                # Process each result
                for result in response:
                    if result.text.lower() in [k.lower() for k in brand_keywords]:
                        keyword_metrics = result.keyword_idea_metrics
                        
                        if settings["granularity"] == "monthly" and period_month_or_quarter is not None:
                            for monthly_search_volume in keyword_metrics.monthly_search_volumes:
                                # ✨ Fix: Align using 1-based period_month_or_quarter
                                if (monthly_search_volume.year == period_year and 
                                    monthly_search_volume.month.value - 1 == period_month_or_quarter):
                                    brand_volume += monthly_search_volume.monthly_searches
                        
                        elif settings["granularity"] == "quarterly" and period_month_or_quarter is not None:
                            quarter_start_month = (period_month_or_quarter - 1) * 3 + 1
                            quarter_end_month = min(quarter_start_month + 2, end_date.month) if period_year == end_date.year else quarter_start_month + 2
                            for monthly_search_volume in keyword_metrics.monthly_search_volumes:
                                # ✨ Fix: Compare directly with value (1-based)
                                if (monthly_search_volume.year == period_year and 
                                    quarter_start_month <= monthly_search_volume.month.value - 1 <= quarter_end_month):
                                    brand_volume += monthly_search_volume.monthly_searches
                        
                        elif settings["granularity"] == "yearly":
                            for monthly_search_volume in keyword_metrics.monthly_search_volumes:
                                if monthly_search_volume.year == period_year:
                                    # For the end year, only include months up to the selected end month
                                    if period_year == end_date.year and monthly_search_volume.month.value - 1 > end_date.month:
                                        continue
                                    brand_volume += monthly_search_volume.monthly_searches
                
                if brand_volume > 0:
                    results.append({
                        "brand": brand["name"],
                        "period": period_label,
                        "volume": brand_volume,
                        "share": 0,
                        "color": brand["color"]
                    })
        
        except GoogleAdsException as ex:
            st.error(f"Google Ads API error for brand {brand['name']}: {ex}")
            for error in ex.failure.errors:
                st.error(f"Error details: {error.message}")
            continue
        
        except Exception as e:
            st.error(f"Error retrieving search volume for {brand['name']}: {str(e)}")
            continue
    
    # Calculate total volume and share percentages for each period
    period_totals = {}
    for result in results:
        period = result["period"]
        if period not in period_totals:
            period_totals[period] = 0
        period_totals[period] += result["volume"]
    
    for result in results:
        period = result["period"]
        if period_totals[period] > 0:
            result["share"] = round((result["volume"] / period_totals[period]) * 100, 1)
    
    return results

# App title and introduction
st.title("📊 Share of Brand Search Tool")
st.markdown("""
This tool helps you analyze brand search volumes from Google Ads and visualize market share trends over time.
Compare your brands against competitors to gain insights into search performance.
""")

# Initialize Google Ads client
google_ads_client = get_google_ads_client()

# Initialize session state variables
if "brands" not in st.session_state:
    st.session_state["brands"] = [
        {"id": str(uuid.uuid4()), "name": "", "keywords": [""], "isOwnBrand": True, "color": "#1f77b4"},
        {"id": str(uuid.uuid4()), "name": "", "keywords": [""], "isOwnBrand": False, "color": "#ff7f0e"}
    ]

# Calculate default date range: 1 year back with end month being current month - 1
current_date = datetime.now()
end_date = datetime(current_date.year, current_date.month, 1) - timedelta(days=1)  # Last day of previous month
start_date = datetime(end_date.year - 1, end_date.month, 1)  # One year before end date

if "settings" not in st.session_state:
    st.session_state["settings"] = {
        "location": "Czech Republic",
        "network": "GOOGLE_SEARCH",
        "dateFrom": start_date.strftime("%Y-%m"),  # Last year
        "dateTo": end_date.strftime("%Y-%m"),  # Current month - 1
        "granularity": "monthly"
    }

if "results" not in st.session_state:
    st.session_state["results"] = []

if "show_results" not in st.session_state:
    st.session_state["show_results"] = False

# Main application interface
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
        locations = list(COUNTRY_MAPPING.keys())
        st.session_state["settings"]["location"] = st.selectbox(
            "Location", 
            options=locations,
            index=locations.index(st.session_state["settings"]["location"]) if st.session_state["settings"]["location"] in locations else locations.index("United States")
        )
        
        # Network - Updated to match the API's available options
        networks = [
            ("GOOGLE_SEARCH", "Google Search"),
            ("GOOGLE_SEARCH_AND_PARTNERS", "Google Search + Search Partners")
        ]
        network_options = [n[1] for n in networks]
        current_network_index = next((i for i, n in enumerate(networks) if n[0] == st.session_state["settings"]["network"]), 0)
        selected_network = st.selectbox(
            "Network",
            options=network_options,
            index=current_network_index
        )
        st.session_state["settings"]["network"] = networks[network_options.index(selected_network)][0]
        
        # Date Range using month/year selectors
        col_date1, col_date2 = st.columns(2)
        
        # Get current date for validation
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        # Calculate previous month (for max date validation)
        prev_month = current_month - 1
        prev_year = current_year
        if prev_month == 0:
            prev_month = 12
            prev_year -= 1
        
        with col_date1:
            st.markdown("**From Month**")
            
            # Parse current from date
            from_date = datetime.strptime(st.session_state["settings"]["dateFrom"], "%Y-%m")
            from_year = from_date.year
            from_month = from_date.month
            
            # Year selector (limit to reasonable range: 10 years back from current year)
            min_year = current_year - 10
            years = list(range(min_year, current_year + 1))
            selected_from_year = st.selectbox(
                "Year",
                options=years,
                index=years.index(from_year) if from_year in years else years.index(current_year - 1),
                key="from_year"
            )
            
            # Month selector
            months = [
                (1, "January"), (2, "February"), (3, "March"), (4, "April"),
                (5, "May"), (6, "June"), (7, "July"), (8, "August"),
                (9, "September"), (10, "October"), (11, "November"), (12, "December")
            ]
            month_options = [m[1] for m in months]
            selected_from_month = st.selectbox(
                "Month",
                options=month_options,
                index=from_month - 1,  # 0-based index
                key="from_month"
            )
            selected_from_month_num = months[month_options.index(selected_from_month)][0]
            
            # Update session state with selected date
            st.session_state["settings"]["dateFrom"] = f"{selected_from_year}-{selected_from_month_num:02d}"
        
        with col_date2:
            st.markdown("**To Month**")
            
            # Parse current to date
            to_date = datetime.strptime(st.session_state["settings"]["dateTo"], "%Y-%m")
            to_year = to_date.year
            to_month = to_date.month
            
            # Year selector (limit to reasonable range and ensure it's not before from_year)
            to_years = [y for y in years if y >= selected_from_year]
            selected_to_year = st.selectbox(
                "Year",
                options=to_years,
                index=to_years.index(to_year) if to_year in to_years else min(to_years.index(selected_from_year), len(to_years) - 1),
                key="to_year"
            )
            
            # Month selector (with validation)
            # If same year as from_date, only show months >= from_month
            # If same year as current year, only show months <= prev_month
            available_months = months.copy()
            if selected_to_year == selected_from_year:
                available_months = [m for m in months if m[0] >= selected_from_month_num]
            if selected_to_year == current_year:
                available_months = [m for m in available_months if m[0] <= prev_month]
            
            # If no months available (edge case), default to from_month
            if not available_months:
                available_months = [months[selected_from_month_num - 1]]
            
            available_month_options = [m[1] for m in available_months]
            
            # Find closest match to current to_month
            default_month_index = 0
            for i, m in enumerate(available_months):
                if m[0] == to_month:
                    default_month_index = i
                    break
                elif m[0] > to_month and i > 0:
                    default_month_index = i - 1
                    break
                elif i == len(available_months) - 1:
                    default_month_index = i
            
            selected_to_month = st.selectbox(
                "Month",
                options=available_month_options,
                index=min(default_month_index, len(available_month_options) - 1),
                key="to_month"
            )
            selected_to_month_num = available_months[available_month_options.index(selected_to_month)][0]
            
            # Update session state with selected date
            st.session_state["settings"]["dateTo"] = f"{selected_to_year}-{selected_to_month_num:02d}"
            
            # Add a note about date limitations
            st.caption("Note: Only past months are available for selection")
        
        # Data Granularity
        st.session_state["settings"]["granularity"] = st.radio(
            "Data Granularity",
            options=["monthly", "quarterly", "yearly"],
            index=["monthly", "quarterly", "yearly"].index(st.session_state["settings"]["granularity"]),
            horizontal=True
        )
        
        # Generate Results Button
        st.markdown("### Generate Results")
        
        valid_brands = [b for b in st.session_state["brands"] 
                       if b["name"] and any(k.strip() for k in b["keywords"])]
        
        if len(valid_brands) < 1:
            st.warning("Please add at least one brand with a name and keywords.")
        else:
            if st.button("🔍 Generate Search Volume Data", type="primary"):
                with st.spinner("Fetching search volume data from Google Ads..."):
                    # Get search volumes using the Google Ads client
                    results = get_search_volumes(valid_brands, st.session_state["settings"], google_ads_client)
                    
                    if results:
                        st.session_state["results"] = results
                        st.session_state["show_results"] = True
                        st.rerun()
                    else:
                        st.error("No data found for the selected parameters.")

# Results tab (only shown after generating results)
if st.session_state["show_results"] and len(tabs) > 1:
    with tabs[1]:
        st.header("Share of Search Results")
        
        # Convert results to DataFrame
        df = pd.DataFrame(st.session_state["results"])
        
        # Create visualization options
        viz_type = st.radio(
            "Visualization Type",
            options=["Share of Search (%)", "Search Volume", "Data Table"],
            horizontal=True
        )
        
        if viz_type == "Share of Search (%)":
            # Create a stacked area chart for share percentages
            fig = px.area(
                df, 
                x="period", 
                y="share", 
                color="brand",
                color_discrete_map={brand["name"]: brand["color"] for brand in st.session_state["brands"] if brand["name"]},
                title="Share of Search Over Time (%)",
                labels={"period": "Time Period", "share": "Share (%)", "brand": "Brand"},
                groupnorm="percent"
            )
            
            fig.update_layout(
                xaxis_title="Time Period",
                yaxis_title="Share of Search (%)",
                legend_title="Brands",
                height=600
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        elif viz_type == "Search Volume":
            # Create a line chart for absolute search volumes
            fig = px.line(
                df, 
                x="period", 
                y="volume", 
                color="brand",
                color_discrete_map={brand["name"]: brand["color"] for brand in st.session_state["brands"] if brand["name"]},
                title="Search Volume Over Time",
                labels={"period": "Time Period", "volume": "Search Volume", "brand": "Brand"},
                markers=True
            )
            
            fig.update_layout(
                xaxis_title="Time Period",
                yaxis_title="Search Volume",
                legend_title="Brands",
                height=600
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        else:  # Data Table
            # Group by period and calculate totals
            periods = sorted(df["period"].unique())
            
            # Create a pivot table
            pivot_df = df.pivot(index="period", columns="brand", values=["volume", "share"]).reset_index()
            
            # Flatten the column names
            pivot_df.columns = [f"{col[0]}_{col[1]}" if col[1] else col[0] for col in pivot_df.columns]
            
            # Sort by period
            pivot_df = pivot_df.sort_values("period")
            
            # Display the table
            st.dataframe(pivot_df, use_container_width=True)
        
        # Export options
        st.subheader("Export Options")
        
        # Export as CSV
        csv = df.to_csv(index=False)
        st.download_button(
            label="📄 Download CSV",
            data=csv,
            file_name=f"share_of_search_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888;">
    Share of Brand Search Tool | Developed by Proficio during 1st AI hackathon with ❤️ | © 2025
</div>
""", unsafe_allow_html=True)

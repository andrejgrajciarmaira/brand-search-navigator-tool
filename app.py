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

# Function to get location ID from location name
def get_location_id(client, location_name):
    """Get the location criterion ID for a given location name."""
    location_mapping = {
        "United States": "2840",
        "United Kingdom": "2826",
        "Canada": "2124",
        "Australia": "2036",
        "Germany": "2276",
        "France": "2250",
        "Spain": "2724",
        "Italy": "2380",
        "Japan": "2392",
        "India": "2356",
        "Brazil": "2076",
        "Mexico": "2484",
        "Netherlands": "2528"
    }
    
    return location_mapping.get(location_name, "2840")  # Default to US if not found

# Function to get language ID from language name
def get_language_id(client, language_name):
    """Get the language criterion ID for a given language name."""
    language_mapping = {
        "English": "1000",
        "Spanish": "1003",
        "French": "1002",
        "German": "1001",
        "Italian": "1004",
        "Portuguese": "1014",
        "Japanese": "1005",
        "Chinese": "1017",  # Simplified Chinese
        "Russian": "1031",
        "Arabic": "1019",
        "Hindi": "1023",
        "Dutch": "1010"
    }
    
    return language_mapping.get(language_name, "1000")  # Default to English if not found

# Function to get search volumes from Google Ads API
def get_search_volumes(brands, settings, client):
    """Retrieve search volume data from Google Ads API for specified brands and keywords."""
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
    
    # Get location and language IDs
    location_id = get_location_id(client, settings["location"])
    language_id = get_language_id(client, settings["language"])
    
    # Get customer ID from secrets
    customer_id = st.secrets["GOOGLE_CUSTOMER_ID"]
    
    # Process each time period
    for period in periods:
        period_results = []
        total_volume = 0
        
        # Process each brand and its keywords
        for brand in brands:
            if not brand["name"] or not any(k.strip() for k in brand["keywords"]):
                continue
            
            brand_volume = 0
            
            # Get search volume for each keyword
            for keyword in [k.strip() for k in brand["keywords"] if k.strip()]:
                try:
                    # Create keyword plan ideas request
                    keyword_plan_idea_service = client.get_service("KeywordPlanIdeaService")
                    
                    # Set up the request
                    request = client.get_type("GenerateKeywordIdeasRequest")
                    request.customer_id = customer_id
                    
                    # Add location and language criteria
                    request.geo_target_constants.append(location_id)
                    request.language = language_id
                    
                    # Set keyword text
                    request.keywords.append(keyword)
                    
                    # Set network based on settings
                    if settings["network"] == "google":
                        request.keyword_plan_network = client.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH
                    elif settings["network"] == "google_search_partners":
                        request.keyword_plan_network = client.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH_PARTNERS
                    else:  # both
                        request.keyword_plan_network = client.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH_AND_PARTNERS
                    
                    # Set date range for historical metrics
                    if settings["granularity"] == "monthly":
                        year, month = period.split("-")
                        request.historical_metrics_options.year_month_range.start.year = int(year)
                        request.historical_metrics_options.year_month_range.start.month = int(month)
                        request.historical_metrics_options.year_month_range.end.year = int(year)
                        request.historical_metrics_options.year_month_range.end.month = int(month)
                    elif settings["granularity"] == "quarterly":
                        year, quarter = period.split("-Q")
                        start_month = (int(quarter) - 1) * 3 + 1
                        end_month = start_month + 2
                        request.historical_metrics_options.year_month_range.start.year = int(year)
                        request.historical_metrics_options.year_month_range.start.month = start_month
                        request.historical_metrics_options.year_month_range.end.year = int(year)
                        request.historical_metrics_options.year_month_range.end.month = end_month
                    else:  # yearly
                        year = int(period)
                        request.historical_metrics_options.year_month_range.start.year = year
                        request.historical_metrics_options.year_month_range.start.month = 1
                        request.historical_metrics_options.year_month_range.end.year = year
                        request.historical_metrics_options.year_month_range.end.month = 12
                    
                    # Execute the request
                    response = keyword_plan_idea_service.generate_keyword_ideas(request=request)
                    
                    # Process the response
                    for result in response.results:
                        if result.keyword_idea_metrics and result.keyword_idea_metrics.avg_monthly_searches:
                            keyword_volume = result.keyword_idea_metrics.avg_monthly_searches
                            brand_volume += keyword_volume
                
                except GoogleAdsException as ex:
                    st.error(f"Google Ads API error: {ex}")
                    for error in ex.failure.errors:
                        st.error(f"Error details: {error.message}")
                    continue
                
                except Exception as e:
                    st.error(f"Error retrieving search volume for {keyword}: {str(e)}")
                    continue
            
            # Add brand data to period results
            if brand_volume > 0:
                period_results.append({
                    "brand": brand["name"],
                    "period": period,
                    "volume": brand_volume,
                    "share": 0,  # Will calculate after all volumes are collected
                    "color": brand["color"]
                })
                total_volume += brand_volume
        
        # Calculate share percentages
        for result in period_results:
            if total_volume > 0:
                result["share"] = round((result["volume"] / total_volume) * 100, 1)
            else:
                result["share"] = 0
            results.append(result)
    
    return results

# App title and introduction
st.title("🔍 Share of Brand Search Tool")
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
        
        col_exp1, col_exp2 = st.columns(2)
        
        with col_exp1:
            # Export as CSV
            csv = df.to_csv(index=False)
            st.download_button(
                label="📄 Download CSV",
                data=csv,
                file_name=f"share_of_search_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
        with col_exp2:
            # Export as Excel
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
                df.to_excel(writer, sheet_name="Data", index=False)
                workbook = writer.book
                worksheet = writer.sheets["Data"]
                
                # Add a chart sheet
                chart_sheet = workbook.add_worksheet("Chart")
                
                # Create a chart
                chart = workbook.add_chart({"type": "line"})
                
                # Configure the chart
                for i, brand in enumerate(df["brand"].unique()):
                    brand_data = df[df["brand"] == brand]
                    col_idx = df.columns.get_loc("volume") + 1
                    row_idx = 1
                    chart.add_series({
                        "name": brand,
                        "categories": ["Data", row_idx, 1, row_idx + len(brand_data) - 1, 1],
                        "values": ["Data", row_idx, col_idx, row_idx + len(brand_data) - 1, col_idx],
                    })
                
                chart.set_title({"name": "Search Volume Over Time"})
                chart.set_x_axis({"name": "Time Period"})
                chart.set_y_axis({"name": "Search Volume"})
                
                # Insert the chart into the chart sheet
                chart_sheet.insert_chart("B2", chart, {"x_scale": 2, "y_scale": 2})
            
            buffer.seek(0)
            st.download_button(
                label="📊 Download Excel",
                data=buffer,
                file_name=f"share_of_search_data_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.ms-excel"
            )

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888;">
    Share of Brand Search Tool | Developed with ❤️ | © 2023
</div>
""", unsafe_allow_html=True)

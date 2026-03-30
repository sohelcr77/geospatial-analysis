# ===============================
# Import Libraries
# ===============================
import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import geodatasets
import requests
import io

# ===============================
# Page Config
# ===============================
st.set_page_config(page_title="Resource Rents Dashboard", layout="wide")
st.title("🌍 Global Natural Resource Rents Dashboard")

# ===============================
# Load World Map (with fallback)
# ===============================
@st.cache_data
def load_world():
    try:
        world = gpd.read_file(geodatasets.get_path('naturalearth_lowres'))
    except:
        url = "https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json"
        response = requests.get(url)
        world = gpd.read_file(io.StringIO(response.text))

    # Ensure ISO code column
    if 'id' in world.columns:
        world = world.rename(columns={'id': 'iso_a3'})

    return world

# ===============================
# Load Resource Data
# ===============================
@st.cache_data
def load_resources():
    data = pd.read_csv('API_NY.GDP.TOTL.RT.ZS_DS2_en_csv_v2_362.csv', skiprows=4)
    return data

world = load_world()
resources = load_resources()

# ===============================
# Sidebar Controls
# ===============================
year = st.sidebar.selectbox("📅 Select Year", ['2018', '2019', '2020'])

# ===============================
# Data Cleaning
# ===============================
df = resources[['Country Name', 'Country Code', year]]
df.columns = ['country', 'iso_a3', 'resource_rents']
df['resource_rents'] = pd.to_numeric(df['resource_rents'], errors='coerce')

# Merge
gdf = world.merge(df, on='iso_a3', how='left')

# ===============================
# Metrics
# ===============================
st.subheader("📊 Key Metrics")
col1, col2, col3 = st.columns(3)

col1.metric("Average", f"{df['resource_rents'].mean():.2f}%")
col2.metric("Maximum", f"{df['resource_rents'].max():.2f}%")
col3.metric("Minimum", f"{df['resource_rents'].min():.2f}%")

# ===============================
# Plotly Map
# ===============================
st.subheader("🌍 Choropleth Map")

fig = px.choropleth(
    df,
    locations="iso_a3",
    color="resource_rents",
    hover_name="country",
    color_continuous_scale="Viridis"
)

st.plotly_chart(fig, use_container_width=True)

# ===============================
# Top 10 Countries
# ===============================
st.subheader("🏆 Top 10 Resource-Rich Countries")

top10 = df.sort_values(by='resource_rents', ascending=False).head(10)
st.dataframe(top10, use_container_width=True)

# ===============================
# Distribution
# ===============================
st.subheader("📈 Distribution")

hist_fig = px.histogram(df, x="resource_rents", nbins=30)
st.plotly_chart(hist_fig, use_container_width=True)

# ===============================
# Footer
# ===============================
st.markdown("---")
st.markdown("**Data Source:** World Bank Open Data (NY.GDP.TOTL.RT.ZS)")

import streamlit as st
import requests
import numpy as np

# Constants
G = 6.674e-11  # Gravitational constant (m³/kg/s²)
AU_TO_METERS = 1.496e+11  # Convert AU to meters

# API endpoints
solar_system_api = "https://api.le-systeme-solaire.net/rest/bodies/"

# Dictionary of known celestial bodies with their API identifiers
horizons_bodies = {
    "Mercury": "mercure",
    "Venus": "venus",
    "Earth": "terre",
    "Mars": "mars",
    "Jupiter": "jupiter",
    "Saturn": "saturne",
    "Uranus": "uranus",
    "Neptune": "neptune",
    "Pluto": "pluton",
    "Moon": "lune",
    "Europa": "europa",
    "Titan": "titan"
}

# Celestial Symbols
celestial_symbols = {
    "Mercury": "☿",
    "Venus": "♀",
    "Earth": "⊕",
    "Mars": "♂",
    "Jupiter": "♃",
    "Saturn": "♄",
    "Uranus": "♅",
    "Neptune": "♆",
    "Pluto": "♇",
    "Moon": "☽",
    "Europa": "🜁",
    "Titan": "🜂"
}

# NASA JPL Image Links for Solar System Objects
nasa_images = {
    "Mercury": "https://solarsystem.nasa.gov/system/feature_items/images/18_mercury_new.png",
    "Venus": "https://solarsystem.nasa.gov/system/feature_items/images/27_venus_jg.png",
    "Earth": "https://solarsystem.nasa.gov/system/feature_items/images/17_earth.png",
    "Mars": "https://solarsystem.nasa.gov/system/feature_items/images/19_mars.png",
    "Jupiter": "https://solarsystem.nasa.gov/system/feature_items/images/16_jupiter_new.png",
    "Saturn": "https://solarsystem.nasa.gov/system/feature_items/images/28_saturn.png",
    "Uranus": "https://solarsystem.nasa.gov/system/feature_items/images/29_uranus.png",
    "Neptune": "https://solarsystem.nasa.gov/system/feature_items/images/30_neptune.png",
    "Pluto": "https://solarsystem.nasa.gov/system/feature_items/images/31_pluto.png",
    "Moon": "https://solarsystem.nasa.gov/system/feature_items/images/16_moon.png",
    "Europa": "https://solarsystem.nasa.gov/system/feature_items/images/14_europa_1600.jpg",
    "Titan": "https://solarsystem.nasa.gov/system/feature_items/images/20_titan_1600.jpg"
}

# Function to get planetary data
def get_planetary_data(body_name):
    """Fetch planetary data from Le Systeme Solaire API and ensure correct unit conversions."""
    response = requests.get(f"{solar_system_api}{body_name}")

    if response.status_code != 200:
        return {}

    data = response.json()
    
    # Extract relevant fields, ensuring correct unit conversions
    extracted_data = {
        "Mass (kg)": data.get("mass", {}).get("massValue", None) * 10**data.get("mass", {}).get("massExponent", 0) if data.get("mass") else None,
        "Sidereal Orbital Period (s)": data.get("sideralOrbit", None) * 86400 if data.get("sideralOrbit") else None,
        "Mean Radius (m)": data.get("meanRadius", None) * 1000 if data.get("meanRadius") else None,
        "Mean Solar Day (s)": data.get("sideralRotation", None) * 86400 if data.get("sideralRotation") else None,
        "Distance from Sun (m)": data.get("semimajorAxis", None) * 1000 if data.get("semimajorAxis") else None,
    }

    return extracted_data

# Format values for LaTeX
def format_value(name, value, unit=""):
    """Formats numerical values using LaTeX scientific notation in 10^x format with proper units."""
    if value is None:
        return rf"{name} = \text{{Unknown}}"
    
    exponent = int(np.floor(np.log10(abs(value)))) if value != 0 else 0
    base = value / (10**exponent)
    
    return rf"{name} = {base:.3f} \times 10^{{{exponent}}} \text{{ {unit} }}"

# Streamlit UI
st.title("Celestial Mechanics Simulator")

# Selection of Solar System bodies
selected_body = st.selectbox("Select a Celestial Body", list(horizons_bodies.keys()))

if st.button("Fetch Data"):
    body_id = horizons_bodies[selected_body]
    planetary_data = get_planetary_data(body_id)

    st.subheader("Extracted Data:")
    formatted_latex = [
        format_value(r"\text{Mass}", planetary_data.get("Mass (kg)"), "kg"),
        format_value(r"\text{Sidereal Orbital Period}", planetary_data.get("Sidereal Orbital Period (s)"), "s"),
        format_value(r"\text{Mean Radius}", planetary_data.get("Mean Radius (m)"), "m"),
        format_value(r"\text{Mean Solar Day}", planetary_data.get("Mean Solar Day (s)"), "s"),
        format_value(r"\text{Distance from Sun}", planetary_data.get("Distance from Sun (m)"), "m"),
    ]

    for latex_string in formatted_latex:
        st.latex(latex_string)

    # Display the celestial symbol if available
    symbol = celestial_symbols.get(selected_body, "N/A")
    st.markdown(f"### **Celestial Symbol: {symbol}**")

    # Display the NASA JPL image of the celestial body
    image_url = nasa_images.get(selected_body, "")
    if image_url:
        st.image(image_url, caption=f"Image of {selected_body}", use_container_width=True)

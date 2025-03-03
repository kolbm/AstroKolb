import streamlit as st
import requests
import numpy as np

# Constants
G = 6.674e-11  # Gravitational constant (m³/kg/s²)
AU_TO_METERS = 1.496e+11  # Convert AU to meters

# API endpoint for solar system objects
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

# Wikipedia GIFs for Solar System Objects
wikipedia_gifs = {
    "Mercury": "https://upload.wikimedia.org/wikipedia/commons/d/d0/Mercury.gif",
    "Venus": "https://upload.wikimedia.org/wikipedia/commons/0/0e/Venus_Rotation_Movie.gif",
    "Earth": "https://upload.wikimedia.org/wikipedia/commons/3/32/Earth_rotation.gif",
    "Mars": "https://upload.wikimedia.org/wikipedia/commons/3/34/Spinning_Mars.gif",
    "Jupiter": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Jupiter_rotation_over_3_hours_with_11_inch_telescope.gif/220px-Jupiter_rotation_over_3_hours_with_11_inch_telescope.gif",
    "Saturn": "https://upload.wikimedia.org/wikipedia/commons/f/fe/Saturnoppositions-animated.gif",
    "Uranus": "https://upload.wikimedia.org/wikipedia/commons/2/20/Uranus_orientation_1985-2030.gif",
    "Neptune": "https://upload.wikimedia.org/wikipedia/commons/6/6d/Neptune.gif",
    "Pluto": "https://upload.wikimedia.org/wikipedia/commons/f/f9/Pluto_rotation_movie.gif",
    "Moon": "https://upload.wikimedia.org/wikipedia/commons/c/c0/Lunar_libration_with_phase2.gif",
    "Europa": "https://upload.wikimedia.org/wikipedia/commons/2/2d/Europa-rotationmovie.gif",
    "Titan": "https://upload.wikimedia.org/wikipedia/commons/e/e2/PIA02146.gif"
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

    # Display the Wikipedia GIF for the celestial body
    image_url = wikipedia_gifs.get(selected_body, "")
    if image_url:
        st.image(image_url, caption=f"Rotating Image of {selected_body}", use_container_width=True)

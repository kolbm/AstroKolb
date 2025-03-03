import streamlit as st
import requests
import numpy as np

# Constants
G = 6.674e-11  # Gravitational constant (m³/kg/s²)
AU_TO_METERS = 1.496e+11  # Convert AU to meters

# Dictionary of known celestial bodies with their API identifiers
solar_system_api = "https://api.le-systeme-solaire.net/rest/bodies/"
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

def get_exoplanet_data():
    """Fetch exoplanet data from NASA Exoplanet Archive API."""
    API_URL = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"
    params = {
        "query": "SELECT pl_name, hostname, pl_orbper, pl_orbsmax, pl_rade, pl_bmassj, pl_constellation FROM pscomppars",
        "format": "json"
    }

    response = requests.get(API_URL, params=params)
    if response.status_code != 200:
        return None

    return response.json()

def format_value(name, value, unit=""):
    """Formats numerical values using LaTeX scientific notation in 10^x format with proper units."""
    if value is None:
        return rf"{name} = \text{{Unknown}}"
    
    exponent = int(np.floor(np.log10(abs(value)))) if value != 0 else 0
    base = value / (10**exponent)
    
    return rf"{name} = {base:.3f} \times 10^{{{exponent}}} \text{{ {unit} }}"

# Streamlit UI
st.title("Celestial Mechanics Simulator")

# Selection between Solar System bodies or Exoplanets
mode = st.radio("Choose Data Source", ["Solar System Objects", "Exoplanets"])

if mode == "Solar System Objects":
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

elif mode == "Exoplanets":
    exoplanets = get_exoplanet_data()

    if exoplanets:
        exoplanet_names = [planet["pl_name"] for planet in exoplanets]
        selected_exoplanet = st.selectbox("Select an Exoplanet", exoplanet_names)

        if st.button("Fetch Exoplanet Data"):
            planet_data = next((p for p in exoplanets if p["pl_name"] == selected_exoplanet), None)

            if planet_data:
                extracted_data = {
                    "Mass (kg)": float(planet_data.get("pl_bmassj", 1.0)) * 1.898e27,  # Convert Jupiter masses to kg
                    "Semi-Major Axis (m)": float(planet_data.get("pl_orbsmax", 1.0)) * AU_TO_METERS,  # Convert AU to meters
                    "Orbital Period (s)": float(planet_data.get("pl_orbper", 1.0)) * 86400,  # Convert days to seconds
                    "Constellation": planet_data.get("pl_constellation", "Unknown"),  # Constellation the exoplanet is in
                }

                st.subheader("Extracted Data:")
                formatted_latex = [
                    format_value(r"\text{Mass}", extracted_data.get("Mass (kg)"), "kg"),
                    format_value(r"\text{Semi-Major Axis}", extracted_data.get("Semi-Major Axis (m)"), "m"),
                    format_value(r"\text{Orbital Period}", extracted_data.get("Orbital Period (s)"), "s"),
                ]

                for latex_string in formatted_latex:
                    st.latex(latex_string)

                # Display the constellation instead of a symbol
                st.markdown(f"### **Constellation: {extracted_data['Constellation']}**")

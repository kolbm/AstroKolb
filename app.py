import streamlit as st
import requests
import numpy as np
import plotly.graph_objects as go

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

def get_planetary_data(body_name):
    """Fetch planetary data from Le Systeme Solaire API."""
    response = requests.get(f"{solar_system_api}{body_name}")

    if response.status_code != 200:
        return {}

    data = response.json()
    
    # Extract relevant fields, using defaults if missing
    extracted_data = {
        "Mass (kg)": data.get("mass", {}).get("massValue", None) * 10**data.get("mass", {}).get("massExponent", 0) if data.get("mass") else None,
        "Orbital Speed (m/s)": data.get("avgVelocity", None) * 1000 if data.get("avgVelocity") else None,
        "Sidereal Orbital Period (s)": data.get("sideralOrbit", None) * 86400 if data.get("sideralOrbit") else None,
        "Escape Velocity (m/s)": data.get("escape", None) * 1000 if data.get("escape") else None,
        "Mean Radius (m)": data.get("meanRadius", None) * 1000 if data.get("meanRadius") else None,
        "Mean Solar Day (s)": data.get("sideralRotation", None) * 86400 if data.get("sideralRotation") else None,
        "Distance from Sun (m)": data.get("semimajorAxis", None) * 1000 if data.get("semimajorAxis") else None,
    }

    return extracted_data

def get_exoplanet_data():
    """Fetch exoplanet data from NASA Exoplanet Archive API."""
    API_URL = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"
    params = {
        "query": "SELECT pl_name, hostname, pl_orbper, pl_orbsmax, pl_rade, pl_bmassj FROM pscomppars",
        "format": "json"
    }

    response = requests.get(API_URL, params=params)
    if response.status_code != 200:
        return None

    return response.json()

def format_value(value):
    """Formats numerical values in scientific notation using LaTeX."""
    if value is None:
        return r"\text{Unknown}"
    return rf"$ {value:.3e} $"

# Streamlit UI
st.title("Celestial Mechanics Simulator")

# Selection between Solar System bodies or Exoplanets
mode = st.radio("Choose Data Source", ["Solar System Objects", "Exoplanets"])

if mode == "Solar System Objects":
    selected_body = st.selectbox("Select a Celestial Body", list(horizons_bodies.keys()))

    if st.button("Fetch Data"):
        body_id = horizons_bodies[selected_body]
        planetary_data = get_planetary_data(body_id)

        # Ensure no repeated "Unknown" values
        cleaned_data = {key: format_value(planetary_data.get(key)) for key in planetary_data}

        st.subheader("Extracted Data:")
        for key, value in cleaned_data.items():
            st.latex(rf"{key.replace(' ', '_')} = {value}")

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
                    "Eccentricity": float(planet_data.get("pl_orbeccen", 0.0)),  # Default to circular orbit
                }

                # Ensure no repeated "Unknown" values
                cleaned_data = {key: format_value(extracted_data.get(key)) for key in extracted_data}

                st.subheader("Extracted Data:")
                for key, value in cleaned_data.items():
                    st.latex(rf"{key.replace(' ', '_')} = {value}")

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
        st.error(f"Failed to retrieve planetary data. HTTP Status: {response.status_code}")
        return None

    data = response.json()
    
    # Extract the relevant fields
    extracted_data = {
        "Mass (kg)": data.get("mass", {}).get("massValue", "Unknown") * 10**data.get("mass", {}).get("massExponent", 0),
        "Orbital Speed (m/s)": data.get("avgVelocity", "Unknown") * 1000,  # Convert from km/s
        "Sidereal Orbital Period (s)": data.get("sideralOrbit", "Unknown") * 86400,  # Convert from days
        "Escape Velocity (m/s)": data.get("escape", "Unknown") * 1000,  # Convert from km/s
        "Mean Radius (m)": data.get("meanRadius", "Unknown") * 1000,  # Convert from km
        "Mean Solar Day (s)": data.get("sideralRotation", "Unknown") * 86400,  # Convert from days
        "Distance from Sun (m)": data.get("semimajorAxis", "Unknown") * 1000,  # Convert from km
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
        st.error(f"Failed to retrieve exoplanet data. HTTP Status: {response.status_code}")
        return None

    return response.json()

def plot_3d_orbit(semi_major_axis, eccentricity):
    """Plot a 3D orbit using Plotly."""
    if semi_major_axis == "Unknown":
        st.error("Cannot plot orbit: missing or invalid semi-major axis.")
        return None

    theta = np.linspace(0, 2*np.pi, 200)
    a = semi_major_axis
    b = a * np.sqrt(1 - eccentricity**2)  # Semi-minor axis

    x = a * np.cos(theta) - eccentricity * a  # Adjust for center shift
    y = b * np.sin(theta)
    z = np.zeros_like(x)

    fig = go.Figure()
    fig.add_trace(go.Scatter3d(x=x, y=y, z=z, mode='lines', name="Orbit Path"))
    fig.add_trace(go.Scatter3d(x=[-eccentricity * a], y=[0], z=[0], mode='markers', marker=dict(size=6, color='red'), name="Central Body"))
    fig.add_trace(go.Scatter3d(x=[(1-eccentricity) * a], y=[0], z=[0], mode='markers', marker=dict(size=4, color='blue'), name="Second Focus"))

    fig.update_layout(scene=dict(xaxis_title='X Position (m)', yaxis_title='Y Position (m)', zaxis_title='Z Position'))
    return fig

# Streamlit UI
st.title("Celestial Mechanics Simulator")

# Selection between Solar System bodies or Exoplanets
mode = st.radio("Choose Data Source", ["Solar System Objects", "Exoplanets"])

if mode == "Solar System Objects":
    selected_body = st.selectbox("Select a Celestial Body", list(horizons_bodies.keys()))

    if st.button("Fetch Data"):
        body_id = horizons_bodies[selected_body]
        extracted_data = get_planetary_data(body_id)

        if extracted_data:
            st.subheader("Extracted Data:")
            for key, value in extracted_data.items():
                st.write(f"**{key}:** {value}")

elif mode == "Exoplanets":
    exoplanets = get_exoplanet_data()

    if exoplanets:
        exoplanet_names = [planet["pl_name"] for planet in exoplanets]
        selected_exoplanet = st.selectbox("Select an Exoplanet", exoplanet_names)

        if st.button("Fetch Exoplanet Data"):
            planet_data = next((p for p in exoplanets if p["pl_name"] == selected_exoplanet), None)

            if planet_data:
                extracted_data = {
                    "Mass (kg)": float(planet_data.get("pl_bmassj", "1.0")) * 1.898e27,  # Convert Jupiter masses to kg
                    "Semi-Major Axis (m)": float(planet_data.get("pl_orbsmax", "1.0")) * AU_TO_METERS,  # Convert AU to meters
                    "Orbital Period (s)": float(planet_data.get("pl_orbper", "1.0")) * 86400,  # Convert days to seconds
                    "Eccentricity": float(planet_data.get("pl_orbeccen", "0.0")),  # Default to circular orbit
                }

                st.subheader("Extracted Data:")
                for key, value in extracted_data.items():
                    st.write(f"**{key}:** {value}")

                # 3D Visualization
                st.subheader("3D Orbital Visualization")
                st.plotly_chart(plot_3d_orbit(extracted_data["Semi-Major Axis (m)"], extracted_data["Eccentricity"]))

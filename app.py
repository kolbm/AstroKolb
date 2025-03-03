import streamlit as st
import requests
import numpy as np
import plotly.graph_objects as go

# Constants
G = 6.674e-11  # Gravitational constant (m³/kg/s²)
AU_TO_METERS = 1.496e+11  # 1 AU to meters

# Dictionary of known celestial bodies with NASA Horizons API IDs
horizons_bodies = {
    "Earth": "399",
    "Moon": "301",
    "Mars": "499",
    "Jupiter": "599",
    "Europa": "502",
    "Titan": "606",
    "Pluto": "999"
}

def get_horizons_data(body_id):
    """Fetch orbital data from NASA Horizons API and extract key values."""
    API_URL = "https://ssd.jpl.nasa.gov/api/horizons.api"
    params = {"format": "json", "COMMAND": body_id, "OBJ_DATA": "YES"}

    response = requests.get(API_URL, params=params)
    if response.status_code != 200:
        st.error(f"Failed to retrieve data from NASA Horizons. HTTP Status: {response.status_code}")
        return None

    data = response.json()
    if "result" not in data:
        st.error("Invalid API response: 'result' key missing.")
        st.json(data)  # Debugging output
        return None

    result_text = data["result"]

    def extract_value(label, unit_conversion=1):
        """Extract numerical values from the text response."""
        try:
            line = next(line for line in result_text.split("\n") if label in line)
            value = float(line.split("=")[1].split()[0]) * unit_conversion
            return value
        except (StopIteration, ValueError, IndexError):
            return "Unknown"

    extracted_data = {
        "Mass (kg)": extract_value("Mass x10^24", 1e24),
        "Orbital Speed (m/s)": extract_value("Orbital speed, km/s", 1000),
        "Sidereal Orbital Period (s)": extract_value("Sidereal orb period", 86400),
        "Escape Velocity (m/s)": extract_value("Escape velocity", 1000),
        "Mean Radius (m)": extract_value("Vol. Mean Radius (km)", 1000),
        "Mean Solar Day (s)": extract_value("Mean solar day", 1),
        "Distance from Sun (m)": extract_value("Hill's sphere radius", AU_TO_METERS),
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

def calculate_orbital_parameters(mass, semi_major_axis, eccentricity):
    """Calculate orbital properties based on UCM and UG."""
    if mass == "Unknown" or semi_major_axis == "Unknown":
        return "Unknown", "Unknown", "Unknown", "Unknown"

    GM = G * mass
    r = semi_major_axis * (1 - eccentricity)

    if r == 0:
        return "Unknown", "Unknown", "Unknown", "Unknown"

    orbital_velocity = np.sqrt(GM / r)
    centripetal_acceleration = orbital_velocity**2 / r
    escape_velocity = np.sqrt(2 * GM / r)
    orbital_period = 2 * np.pi * np.sqrt(semi_major_axis**3 / GM)

    return orbital_velocity, centripetal_acceleration, escape_velocity, orbital_period

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
        extracted_data = get_horizons_data(body_id)

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

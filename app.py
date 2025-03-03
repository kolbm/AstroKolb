import streamlit as st
import requests
import numpy as np
import plotly.graph_objects as go

# Constants
G = 6.674e-11  # Gravitational constant (m³/kg/s²)

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
    """Fetch orbital data from NASA Horizons API."""
    API_URL = "https://ssd.jpl.nasa.gov/api/horizons.api"
    params = {
        "format": "json",
        "COMMAND": body_id,
        "OBJ_DATA": "YES"
    }
    
    response = requests.get(API_URL, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to retrieve data from NASA Horizons. HTTP Status: {response.status_code}")
        return None

def get_exoplanet_data():
    """Fetch exoplanet data from NASA Exoplanet Archive API."""
    API_URL = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"
    params = {
        "query": "SELECT pl_name, hostname, pl_orbper, pl_orbsmax, pl_rade, pl_bmassj FROM pscomppars",
        "format": "json"
    }

    response = requests.get(API_URL, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to retrieve exoplanet data. HTTP Status: {response.status_code}")
        return None

def calculate_orbital_parameters(mass, semi_major_axis, eccentricity):
    """Calculate orbital properties based on UCM and UG."""
    if mass is None or semi_major_axis is None:
        return None, None, None, None  # Prevent NaN errors
    
    GM = G * mass
    r = semi_major_axis * (1 - eccentricity)
    
    if r == 0:
        return None, None, None, None

    orbital_velocity = np.sqrt(GM / r)
    centripetal_acceleration = orbital_velocity**2 / r
    escape_velocity = np.sqrt(2 * GM / r)
    orbital_period = 2 * np.pi * np.sqrt(semi_major_axis**3 / GM)

    return orbital_velocity, centripetal_acceleration, escape_velocity, orbital_period

def plot_3d_orbit(semi_major_axis, eccentricity):
    """Plot a 3D orbit using Plotly."""
    if semi_major_axis is None or semi_major_axis == 0:
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
        data = get_horizons_data(body_id)

        if data:
            st.json(data)  # Debugging: Display raw API response

            try:
                mass = None
                if "GM" in data["result"]:
                    try:
                        gm_value = float(data["result"]["GM"].split()[0])  # Extract GM
                        mass = gm_value / G  # Convert GM to mass
                    except ValueError:
                        st.error("Could not convert GM to mass.")
                
                semi_major_axis = float(data["result"].get("a", "1.0")) * 1.496e+11  # Convert AU to meters
                eccentricity = float(data["result"].get("e", "0.0"))  # Default to circular orbit

                if mass is None:
                    st.error("Mass data not found.")
                if semi_major_axis is None:
                    st.error("Semi-major axis data not found.")

                orbital_velocity, centripetal_acceleration, escape_velocity, orbital_period = calculate_orbital_parameters(mass, semi_major_axis, eccentricity)

                st.write(f"**Mass**: {mass:.2e} kg" if mass else "Mass unavailable")
                st.write(f"**Semi-Major Axis**: {semi_major_axis:.2e} m")
                st.write(f"**Eccentricity**: {eccentricity:.3f}")
                st.write(f"**Orbital Velocity**: {orbital_velocity:.2f} m/s" if orbital_velocity else "Unavailable")
                st.write(f"**Centripetal Acceleration**: {centripetal_acceleration:.2f} m/s²" if centripetal_acceleration else "Unavailable")
                st.write(f"**Escape Velocity**: {escape_velocity:.2f} m/s" if escape_velocity else "Unavailable")
                st.write(f"**Orbital Period**: {orbital_period:.2f} s" if orbital_period else "Unavailable")

                # 3D Visualization
                st.subheader("3D Orbital Visualization")
                st.plotly_chart(plot_3d_orbit(semi_major_axis, eccentricity))

            except KeyError:
                st.error("Missing orbital data for the selected body.")

elif mode == "Exoplanets":
    exoplanets = get_exoplanet_data()

    if exoplanets:
        exoplanet_names = [planet["pl_name"] for planet in exoplanets]
        selected_exoplanet = st.selectbox("Select an Exoplanet", exoplanet_names)

        if st.button("Fetch Exoplanet Data"):
            planet_data = next((p for p in exoplanets if p["pl_name"] == selected_exoplanet), None)

            if planet_data:
                semi_major_axis = float(planet_data.get("pl_orbsmax", "1.0")) * 1.496e+11  # Convert AU to meters
                mass = float(planet_data.get("pl_bmassj", "1.0")) * 1.898e27  # Convert Jupiter masses to kg
                eccentricity = float(planet_data.get("pl_orbeccen", "0.0"))  # Default to circular orbit

                orbital_velocity, centripetal_acceleration, escape_velocity, orbital_period = calculate_orbital_parameters(mass, semi_major_axis, eccentricity)

                st.write(f"**Mass**: {mass:.2e} kg")
                st.write(f"**Semi-Major Axis**: {semi_major_axis:.2e} m")
                st.write(f"**Eccentricity**: {eccentricity:.3f}")
                st.write(f"**Orbital Velocity**: {orbital_velocity:.2f} m/s")
                st.write(f"**Centripetal Acceleration**: {centripetal_acceleration:.2f} m/s²")
                st.write(f"**Escape Velocity**: {escape_velocity:.2f} m/s")
                st.write(f"**Orbital Period**: {orbital_period:.2f} s")

                # 3D Visualization
                st.subheader("3D Orbital Visualization")
                st.plotly_chart(plot_3d_orbit(semi_major_axis, eccentricity))

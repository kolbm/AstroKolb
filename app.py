import streamlit as st
import requests
import numpy as np
import plotly.graph_objects as go

G = 6.674e-11  # Gravitational constant (m³/kg/s²)

bodies = {
    "Earth": "Earth",
    "Moon": "Moon",
    "Mars": "Mars",
    "Jupiter": "Jupiter",
    "Europa": "Europa",
    "Titan": "Titan",
    "Pluto": "Pluto",
    "Ceres": "Ceres",
    "Eris": "Eris"
}

def get_celestial_data(body_name):
    """Fetch orbital data from JPL Small-Body API."""
    API_URL = "https://ssd-api.jpl.nasa.gov/sbdb.api"
    params = {"sstr": body_name, "full": "true"}

    response = requests.get(API_URL, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to retrieve data. HTTP Status: {response.status_code}")
        return None

def calculate_orbital_parameters(mass, semi_major_axis, eccentricity):
    """Calculate orbital properties based on UCM and UG."""
    GM = G * mass
    r = semi_major_axis * (1 - eccentricity)
    orbital_velocity = np.sqrt(GM / r)
    centripetal_acceleration = orbital_velocity**2 / r
    escape_velocity = np.sqrt(2 * GM / r)
    orbital_period = 2 * np.pi * np.sqrt(semi_major_axis**3 / GM)

    return orbital_velocity, centripetal_acceleration, escape_velocity, orbital_period

st.title("Celestial Mechanics Simulator")

selected_body = st.selectbox("Select a Celestial Body", list(bodies.keys()))

if st.button("Fetch Data"):
    data = get_celestial_data(bodies[selected_body])

    if data:
        try:
            orbit_params = data.get("orbit", {})

            mass = float(data["phys_pars"]["GM"]) / G  # Convert GM to mass
            semi_major_axis = float(orbit_params["a"]) * 1.496e+11  # AU to meters
            eccentricity = float(orbit_params["e"])

            orbital_velocity, centripetal_acceleration, escape_velocity, orbital_period = calculate_orbital_parameters(mass, semi_major_axis, eccentricity)

            st.write(f"**Mass**: {mass:.2e} kg")
            st.write(f"**Semi-Major Axis**: {semi_major_axis:.2e} m")
            st.write(f"**Eccentricity**: {eccentricity:.3f}")
            st.write(f"**Orbital Velocity**: {orbital_velocity:.2f} m/s")
            st.write(f"**Centripetal Acceleration**: {centripetal_acceleration:.2f} m/s²")
            st.write(f"**Escape Velocity**: {escape_velocity:.2f} m/s")
            st.write(f"**Orbital Period**: {orbital_period:.2f} s")

        except KeyError:
            st.error("Missing orbital data for the selected body.")

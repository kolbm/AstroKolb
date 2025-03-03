import streamlit as st
import requests
import numpy as np
import plotly.graph_objects as go

# Constants
G = 6.674e-11  # Gravitational constant (m³/kg/s²)
API_URL = "https://ssd-api.jpl.nasa.gov/horizons.api"

# Dictionary of celestial bodies with Horizons API IDs
bodies = {
    "Earth (399)": "399",
    "Moon (301)": "301",
    "Mars (499)": "499",
    "Jupiter (599)": "599",
    "Europa (502)": "502",
    "Titan (606)": "606",
    "Pluto (999)": "999",
    "Ceres (2000001)": "2000001",
    "Eris (136199)": "136199"
}

def get_celestial_data(body_id):
    """Fetch orbital data from NASA Horizons API."""
    params = {"format": "json", "COMMAND": body_id, "OBJ_DATA": "YES"}
    response = requests.get(API_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to retrieve data.")
        return None

def calculate_orbital_parameters(mass, semi_major_axis, eccentricity):
    """Calculate orbital properties based on UCM and UG."""
    GM = G * mass  # Gravitational parameter
    r = semi_major_axis * (1 - eccentricity)  # Approximate minimum radius
    orbital_velocity = np.sqrt(GM / r)
    centripetal_acceleration = orbital_velocity**2 / r
    escape_velocity = np.sqrt(2 * GM / r)
    orbital_period = 2 * np.pi * np.sqrt(semi_major_axis**3 / GM)

    return orbital_velocity, centripetal_acceleration, escape_velocity, orbital_period

def plot_3d_orbit(semi_major_axis, eccentricity):
    """Plot a 3D orbit using Plotly."""
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

# Selection between pre-defined bodies or custom input
mode = st.radio("Choose Data Source", ["Select a Celestial Body", "Enter Custom Values"])

if mode == "Select a Celestial Body":
    selected_body = st.selectbox("Select a Celestial Body", list(bodies.keys()))
    if st.button("Fetch Data"):
        body_id = bodies[selected_body]
        data = get_celestial_data(body_id)

        if data:
            try:
                mass = float(data["result"]["mass"].split()[0])  # Extract mass
                semi_major_axis = float(data["result"]["a"].split()[0]) * 1.496e+11  # Convert AU to meters
                eccentricity = float(data["result"]["e"].split()[0])  # Extract eccentricity

                # Compute orbital parameters
                orbital_velocity, centripetal_acceleration, escape_velocity, orbital_period = calculate_orbital_parameters(mass, semi_major_axis, eccentricity)

                # Display results
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

            except KeyError:
                st.error("Unable to parse the data. The selected body may not have all necessary parameters.")

elif mode == "Enter Custom Values":
    st.subheader("Enter Custom Orbital Parameters")

    mass = st.number_input("Mass of Central Object (kg)", value=5.972e24, format="%.2e")
    semi_major_axis = st.number_input("Semi-Major Axis (m)", value=1.496e11, format="%.2e")
    eccentricity = st.number_input("Eccentricity (0 for circular, <1 for elliptical)", value=0.0167, min_value=0.0, max_value=0.999)

    if st.button("Calculate Orbit"):
        orbital_velocity, centripetal_acceleration, escape_velocity, orbital_period = calculate_orbital_parameters(mass, semi_major_axis, eccentricity)

        # Display results
        st.write(f"**Orbital Velocity**: {orbital_velocity:.2f} m/s")
        st.write(f"**Centripetal Acceleration**: {centripetal_acceleration:.2f} m/s²")
        st.write(f"**Escape Velocity**: {escape_velocity:.2f} m/s")
        st.write(f"**Orbital Period**: {orbital_period:.2f} s")

        # 3D Visualization
        st.subheader("3D Orbital Visualization")
        st.plotly_chart(plot_3d_orbit(semi_major_axis, eccentricity))

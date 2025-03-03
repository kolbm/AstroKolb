import streamlit as st
import requests
import numpy as np
import random

# Constants
G = 6.674e-11  # Gravitational constant (m³/kg/s²)

# API endpoint for solar system objects
solar_system_api = "https://api.le-systeme-solaire.net/rest/bodies/"

# Dictionary of known celestial bodies
horizons_bodies = {
    "Mercury": "mercure", "Venus": "venus", "Earth": "terre", "Mars": "mars",
    "Jupiter": "jupiter", "Saturn": "saturne", "Uranus": "uranus", "Neptune": "neptune",
    "Pluto": "pluton", "Ceres": "ceres", "Eris": "eris", "Haumea": "haumea", "Makemake": "makemake",
    "Moon": "lune", "Europa": "europa", "Ganymede": "ganymede", "Callisto": "callisto",
    "Io": "io", "Triton": "triton", "Enceladus": "enceladus", "Titan": "titan",
    "Vesta": "vesta", "Pallas": "pallas", "Hygiea": "hygiea"
}

# Parent body (for moons)
moon_orbits = {
    "Moon": "Earth", "Europa": "Jupiter", "Ganymede": "Jupiter", "Callisto": "Jupiter",
    "Io": "Jupiter", "Triton": "Neptune", "Enceladus": "Saturn", "Titan": "Saturn"
}

# Function to get planetary data
def get_planetary_data(body_name):
    try:
        response = requests.get(f"{solar_system_api}{body_name}", timeout=5)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {e}")
        return {}, None  # Return empty data to prevent crashes

    data = response.json()
    
    # Extract mass
    mass = None
    if "mass" in data and data["mass"]:
        mass = data["mass"].get("massValue", None)
        if mass is not None:
            mass *= 10 ** data["mass"].get("massExponent", 0)

    # Extract radius
    radius = data.get("meanRadius", None)
    if radius is not None:
        radius *= 1000  # Convert km to m

    # Compute surface gravity & escape velocity
    surface_gravity = None
    escape_velocity = None
    if mass is not None and radius is not None:
        surface_gravity = G * mass / radius**2
        escape_velocity = np.sqrt(2 * G * mass / radius)

    # Extract data
    extracted_data = {
        "Mass": (mass, "kg"),
        "Sidereal Orbital Period": (data.get("sideralOrbit", None) * 86400 if data.get("sideralOrbit") else None, "s"),
        "Mean Radius": (radius, "m"),
        "Mean Solar Day": (data.get("sideralRotation", None) * 86400 if data.get("sideralRotation") else None, "s"),
        "Distance from Sun": (data.get("semimajorAxis", None) * 1000 if data.get("semimajorAxis") else None, "m"),
        "Surface Gravity": (surface_gravity, "m/s^2"),
        "Escape Velocity": (escape_velocity, "m/s"),
    }
    
    # If the object is a moon, return its orbit information
    orbits_text = moon_orbits.get(body_name, None)

    return extracted_data, orbits_text

# Streamlit UI
st.title("Celestial Mechanics Simulator")

selected_body = st.selectbox("Select a Celestial Body", list(horizons_bodies.keys()))

if st.button("Fetch Data"):
    st.write("Fetching data...")  # Prevents white screen delay
    planetary_data, orbits = get_planetary_data(selected_body)

    # Display centered and bold category title
    st.markdown(f"<h2 style='text-align: center;'><b>{selected_body}</b></h2>", unsafe_allow_html=True)

    # Display planetary data with copy buttons
    for key, (value, unit) in planetary_data.items():
        col1, col2 = st.columns([3, 1])
        
        # Format the value for display
        formatted_value = "Unknown" if value is None else f"{value:.3e}" if abs(value) >= 1e3 or abs(value) < 1e-3 else f"{value:.3f}"
        
        # Show value and unit
        col1.markdown(f"**{key}:** {formatted_value} {unit}")
        
        # Show copy button (only if value exists)
        if value is not None:
            col2.button("📋 Copy", key=f"copy_{key}", on_click=lambda val=formatted_value: st.session_state.update({"clipboard": val}))

    # Display what the moon orbits (only if applicable)
    if orbits:
        st.markdown(f"**Orbits:** {orbits}")

    # Display celestial image (if available)
    celestial_images = {
        "Mercury": "https://upload.wikimedia.org/wikipedia/commons/d/d0/Mercury.gif",
        "Venus": "https://upload.wikimedia.org/wikipedia/commons/0/0e/Venus_Rotation_Movie.gif",
        "Earth": "https://upload.wikimedia.org/wikipedia/commons/3/32/Earth_rotation.gif",
        "Mars": "https://upload.wikimedia.org/wikipedia/commons/3/34/Spinning_Mars.gif",
        "Jupiter": "https://upload.wikimedia.org/wikipedia/commons/6/6d/Neptune.gif",
        "Saturn": "https://upload.wikimedia.org/wikipedia/commons/f/fe/Saturnoppositions-animated.gif",
        "Pluto": "https://upload.wikimedia.org/wikipedia/commons/f/f9/Pluto_rotation_movie.gif"
    }

    if selected_body in celestial_images:
        st.image(celestial_images[selected_body], caption=f"Image of {selected_body}", use_container_width=True)

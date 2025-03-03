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
    # Planets
    "Mercury": "mercure",
    "Venus": "venus",
    "Earth": "terre",
    "Mars": "mars",
    "Jupiter": "jupiter",
    "Saturn": "saturne",
    "Uranus": "uranus",
    "Neptune": "neptune",
    "Pluto": "pluton",

    # Dwarf Planets
    "Ceres": "ceres",
    "Eris": "eris",
    "Haumea": "haumea",
    "Makemake": "makemake",

    # Moons
    "Moon": "lune",
    "Europa": "europa",
    "Ganymede": "ganymede",
    "Callisto": "callisto",
    "Io": "io",
    "Triton": "triton",
    "Enceladus": "enceladus",
    "Titan": "titan",

    # Asteroids
    "Vesta": "vesta",
    "Pallas": "pallas",
    "Hygiea": "hygiea"
}

# Categories for celestial objects
object_categories = {
    "Mercury": "Planet",
    "Venus": "Planet",
    "Earth": "Planet",
    "Mars": "Planet",
    "Jupiter": "Planet",
    "Saturn": "Planet",
    "Uranus": "Planet",
    "Neptune": "Planet",
    "Pluto": "Dwarf Planet",
    "Ceres": "Dwarf Planet",
    "Eris": "Dwarf Planet",
    "Haumea": "Dwarf Planet",
    "Makemake": "Dwarf Planet",
    "Moon": "Planetary Satellite (Moon)",
    "Europa": "Planetary Satellite (Moon)",
    "Ganymede": "Planetary Satellite (Moon)",
    "Callisto": "Planetary Satellite (Moon)",
    "Io": "Planetary Satellite (Moon)",
    "Triton": "Planetary Satellite (Moon)",
    "Enceladus": "Planetary Satellite (Moon)",
    "Titan": "Planetary Satellite (Moon)",
    "Vesta": "Asteroid",
    "Pallas": "Asteroid",
    "Hygiea": "Asteroid"
}

# Celestial Symbols (for planets and major bodies)
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
    "Moon": "https://upload.wikimedia.org/wikipedia/commons/c/c0/Lunar_libration_with_phase2.gif"
}

# Function to get planetary data
def get_planetary_data(body_name):
    response = requests.get(f"{solar_system_api}{body_name}")
    if response.status_code != 200:
        return {}

    data = response.json()
    
    mass = data.get("mass", {}).get("massValue", None) * 10**data.get("mass", {}).get("massExponent", 0) if data.get("mass") else None
    radius = data.get("meanRadius", None) * 1000 if data.get("meanRadius") else None

    surface_gravity = (G * mass / radius**2) if (mass and radius) else None
    escape_velocity = np.sqrt(2 * G * mass / radius) if (mass and radius) else None

    extracted_data = {
        "Mass (kg)": mass,
        "Sidereal Orbital Period (s)": data.get("sideralOrbit", None) * 86400 if data.get("sideralOrbit") else None,
        "Mean Radius (m)": radius,
        "Mean Solar Day (s)": data.get("sideralRotation", None) * 86400 if data.get("sideralRotation") else None,
        "Distance from Sun (m)": data.get("semimajorAxis", None) * 1000 if data.get("semimajorAxis") else None,
        "Surface Gravity (m/s^2)": surface_gravity,
        "Escape Velocity (m/s)": escape_velocity
    }
    return extracted_data

# Streamlit UI
st.title("Celestial Mechanics Simulator")

selected_body = st.selectbox("Select a Celestial Body", list(horizons_bodies.keys()))

if st.button("Fetch Data"):
    category = object_categories[selected_body]
    body_id = horizons_bodies[selected_body]
    planetary_data = get_planetary_data(body_id)

    st.subheader(f"Category: **{category}**")
    
    for key, value in planetary_data.items():
        if value is not None:
            st.latex(f"{key} = {value:.3e}")
        else:
            st.latex(f"{key} = \\text{{Unknown}}")

    symbol = celestial_symbols.get(selected_body, "N/A")
    st.markdown(f"<div style='text-align: center; font-size: 140px;'>{symbol}</div>", unsafe_allow_html=True)

    image_url = wikipedia_gifs.get(selected_body, "")
    if image_url:
        st.image(image_url, caption=f"Rotating Image of {selected_body}", use_container_width=True)

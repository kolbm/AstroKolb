import streamlit as st
import requests
import numpy as np
import random

# Constants
G = 6.674e-11  # Gravitational constant (m³/kg/s²)

# API endpoint for solar system objects
solar_system_api = "https://api.le-systeme-solaire.net/rest/bodies/"

# Dictionary of known celestial bodies with their API identifiers
horizons_bodies = {
    "Mercury": "mercure", "Venus": "venus", "Earth": "terre", "Mars": "mars",
    "Jupiter": "jupiter", "Saturn": "saturne", "Uranus": "uranus", "Neptune": "neptune",
    "Pluto": "pluton", "Ceres": "ceres", "Eris": "eris", "Haumea": "haumea", "Makemake": "makemake",
    "Moon": "lune", "Europa": "europa", "Ganymede": "ganymede", "Callisto": "callisto",
    "Io": "io", "Triton": "triton", "Enceladus": "enceladus", "Titan": "titan",
    "Vesta": "vesta", "Pallas": "pallas", "Hygiea": "hygiea"
}

# Dictionary of celestial object images
celestial_images = {
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
    "Titan": "https://upload.wikimedia.org/wikipedia/commons/e/e2/PIA02146.gif",
    "Ceres": "https://upload.wikimedia.org/wikipedia/commons/7/73/PIA19179-Ceres-DawnSpacecraft-Animation16-20150204.gif",
    "Eris": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Artist%27s_impression_dwarf_planet_Eris.jpg/2560px-Artist%27s_impression_dwarf_planet_Eris.jpg",
    "Haumea": "https://upload.wikimedia.org/wikipedia/commons/9/9c/Haumea_Rotation.gif",
    "Makemake": "https://upload.wikimedia.org/wikipedia/commons/7/79/Makemake_Animation.gif",
    "Ganymede": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR7spUKvknajRiSUvNvyVSJ98HxDLzMIJqSjw&s",
    "Callisto": "https://upload.wikimedia.org/wikipedia/commons/e/e4/Callisto-rotationmovie.gif",
    "Io": "https://upload.wikimedia.org/wikipedia/commons/1/14/Io-rotationmovie.gif",
    "Triton": "https://upload.wikimedia.org/wikipedia/commons/f/f3/Triton_Rotation_Movie.gif",
    "Enceladus": "https://cdn.mos.cms.futurecdn.net/C4hmAcPxXXHY8AZ7EpHZDJ-320-80.gif",
    "Vesta": "https://upload.wikimedia.org/wikipedia/commons/f/ff/Vesta_Rotation.gif?20110803005326",
    "Pallas": "https://upload.wikimedia.org/wikipedia/commons/d/d4/Potw1749a_Pallas_crop.png",
    "Hygiea": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/88/SPHERE_image_of_Hygiea.jpg/290px-SPHERE_image_of_Hygiea.jpg"
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
        "Mass": (mass, "kg"),
        "Surface Gravity": (surface_gravity, r"\text{m/s}^2"),
        "Escape Velocity": (escape_velocity, "m/s"),
    }

    return extracted_data

# Format values for LaTeX
def format_value(name, value, unit):
    """Formats numerical values using LaTeX scientific notation, with standard notation for -2 ≤ exponent ≤ 2."""
    if value is None:
        return rf"\textbf{{{name}}}: \text{{Unknown}}"

    exponent = int(np.floor(np.log10(abs(value)))) if value != 0 else 0
    base = value / (10**exponent)

    # If exponent is between -2 and 2, display in standard notation
    if -2 <= exponent <= 2:
        return rf"\textbf{{{name}}}: {value:.3f} \quad {unit}"
    
    return rf"\textbf{{{name}}}: {base:.3f} \times 10^{{{exponent}}} \quad {unit}"

# Streamlit UI
st.title("Celestial Mechanics Simulator")

selected_body = st.selectbox("Select a Celestial Body", list(horizons_bodies.keys()))

if st.button("Fetch Data"):
    planetary_data = get_planetary_data(selected_body)

    # Display centered and bold category title
    st.markdown(f"<h2 style='text-align: center;'><b>{selected_body}</b></h2>", unsafe_allow_html=True)

    for key, (value, unit) in planetary_data.items():
        st.latex(format_value(key, value, unit))

    # Display celestial image
    if selected_body in celestial_images:
        st.image(celestial_images[selected_body], caption=f"Image of {selected_body}", use_column_width=True)


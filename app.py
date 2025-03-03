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

# Celestial Symbols
celestial_symbols = {
    "Mercury": "☿", "Venus": "♀", "Earth": "⊕", "Mars": "♂",
    "Jupiter": "♃", "Saturn": "♄", "Uranus": "♅", "Neptune": "♆",
    "Pluto": "♇", "Moon": "☽", "Europa": "🜁", "Titan": "🜂"
}

# Parent body (for moons)
moon_orbits = {
    "Moon": "Earth", "Europa": "Jupiter", "Ganymede": "Jupiter", "Callisto": "Jupiter",
    "Io": "Jupiter", "Triton": "Neptune", "Enceladus": "Saturn", "Titan": "Saturn"
}

# Function to get planetary data
def get_planetary_data(body_name):
    response = requests.get(f"{solar_system_api}{body_name}")
    if response.status_code != 200:
        return {}

    data = response.json()
    
    mass = None
    if "mass" in data and data["mass"]:
        mass = data["mass"].get("massValue", None)
        if mass is not None:
            mass *= 10 ** data["mass"].get("massExponent", 0)

    radius = data.get("meanRadius", None)
    if radius is not None:
        radius *= 1000  # Convert km to m

    surface_gravity = None
    escape_velocity = None
    if mass is not None and radius is not None:
        surface_gravity = G * mass / radius**2
        escape_velocity = np.sqrt(2 * G * mass / radius)

    extracted_data = {
        "Mass": (mass, "kg"),
        "Sidereal Orbital Period": (data.get("sideralOrbit", None) * 86400 if data.get("sideralOrbit") else None, "s"),
        "Mean Radius": (radius, "m"),
        "Mean Solar Day": (data.get("sideralRotation", None) * 86400 if data.get("sideralRotation") else None, "s"),
        "Distance from Sun": (data.get("semimajorAxis", None) * 1000 if data.get("semimajorAxis") else None, "m"),
        "Surface Gravity": (surface_gravity, r"\text{m/s}^2"),
        "Escape Velocity": (escape_velocity, "m/s"),
    }
    
    # If the object is a moon, add information about its parent planet
    if body_name in moon_orbits:
        extracted_data["Orbits"] = (moon_orbits[body_name], "")

    return extracted_data

# Format values for LaTeX
def format_value(name, value, unit):
    """Formats numerical values using LaTeX scientific notation, with standard notation for -2 ≤ exponent ≤ 2."""
    if value is None:
        return rf"\textbf{{{name}}}: \text{{Unknown}}"

    try:
        exponent = int(np.floor(np.log10(abs(value)))) if value != 0 else 0
        base = value / (10**exponent)

        # If exponent is between -2 and 2, display in standard notation
        if -2 <= exponent <= 2:
            return rf"\textbf{{{name}}}: {value:.3f} \quad {unit}"
        
        return rf"\textbf{{{name}}}: {base:.3f} \times 10^{{{exponent}}} \quad {unit}"
    except:
        return rf"\textbf{{{name}}}: \text{{Unknown}}"

# Streamlit UI
st.title("Celestial Mechanics Simulator")

selected_body = st.selectbox("Select a Celestial Body", list(horizons_bodies.keys()))

if st.button("Fetch Data"):
    planetary_data = get_planetary_data(selected_body)

    # Display centered and bold category title
    st.markdown(f"<h2 style='text-align: center;'><b>{selected_body}</b></h2>", unsafe_allow_html=True)

    # Display celestial symbol
    symbol = celestial_symbols.get(selected_body, random.choice(["🦄", "🐦‍🔥", "🦖", "🐲"]))
    st.markdown(f"<div style='text-align: center; font-size: 140px;'>{symbol}</div>", unsafe_allow_html=True)

    # Display planetary data
    for key, (value, unit) in planetary_data.items():
        st.latex(format_value(key, value, unit))

    # Display what the moon orbits
    if selected_body in moon_orbits:
        st.latex(rf"\textbf{{Orbits}}: \text{{{moon_orbits[selected_body]}}}")

    # Display celestial image
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

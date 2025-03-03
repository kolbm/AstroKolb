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

# Categories for celestial objects
object_categories = {
    "Mercury": "Planet", "Venus": "Planet", "Earth": "Planet", "Mars": "Planet",
    "Jupiter": "Planet", "Saturn": "Planet", "Uranus": "Planet", "Neptune": "Planet",
    "Pluto": "Dwarf Planet", "Ceres": "Dwarf Planet", "Eris": "Dwarf Planet",
    "Haumea": "Dwarf Planet", "Makemake": "Dwarf Planet", "Moon": "Moon",
    "Europa": "Moon", "Ganymede": "Moon", "Callisto": "Moon",
    "Io": "Moon", "Triton": "Moon", "Enceladus": "Moon",
    "Titan": "Moon", "Vesta": "Asteroid", "Pallas": "Asteroid",
    "Hygiea": "Asteroid"
}

# Parent body (for moons)
moon_orbits = {
    "Moon": "Earth", "Europa": "Jupiter", "Ganymede": "Jupiter", "Callisto": "Jupiter",
    "Io": "Jupiter", "Triton": "Neptune", "Enceladus": "Saturn", "Titan": "Saturn"
}

# Celestial Symbols
celestial_symbols = {
    "Mercury": "☿", "Venus": "♀", "Earth": "⊕", "Mars": "♂",
    "Jupiter": "♃", "Saturn": "♄", "Uranus": "♅", "Neptune": "♆",
    "Pluto": "♇", "Moon": "☽", "Europa": "🜁", "Titan": "🜂"
}

# Random symbols for celestial bodies with no official symbol
random_symbols = ["🦄", "🐦‍🔥", "🦖", "🐲"]

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
        "Sidereal Orbital Period": (data.get("sideralOrbit", None) * 86400 if data.get("sideralOrbit") else None, "s"),
        "Mean Radius": (radius, "m"),
        "Mean Solar Day": (data.get("sideralRotation", None) * 86400 if data.get("sideralRotation") else None, "s"),
        "Distance from Sun": (data.get("semimajorAxis", None) * 1000 if data.get("semimajorAxis") else None, "m"),
        "Surface Gravity": (surface_gravity, "m/s^2"),
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

    exponent = int(np.floor(np.log10(abs(value)))) if value != 0 else 0
    base = value / (10**exponent)

    # If exponent is between -2 and 2, display in standard notation
    if -2 <= exponent <= 2:
        return rf"\textbf{{{name}}}: {value:.3f} \quad \text{{{unit}}}"
    
    return rf"\textbf{{{name}}}: {base:.3f} \times 10^{{{exponent}}} \quad \text{{{unit}}}"

# Streamlit UI
st.title("Celestial Mechanics Simulator")

selected_body = st.selectbox("Select a Celestial Body", list(horizons_bodies.keys()))

if st.button("Fetch Data"):
    category = object_categories[selected_body]
    body_id = horizons_bodies[selected_body]
    planetary_data = get_planetary_data(body_id)

    # Display centered and bold category title
    st.markdown(f"<h2 style='text-align: center;'><b>Category: {category}</b></h2>", unsafe_allow_html=True)

    for key, (value, unit) in planetary_data.items():
        st.latex(format_value(key, value, unit))

    # Display what the moon orbits
    if selected_body in moon_orbits:
        st.latex(rf"\textbf{{Orbits}}: \text{{{moon_orbits[selected_body]}}}")

    # Display celestial symbol, or a random one if missing
    symbol = celestial_symbols.get(selected_body, random.choice(random_symbols))
    st.markdown(f"<div style='text-align: center; font-size: 140px;'>{symbol}</div>", unsafe_allow_html=True)

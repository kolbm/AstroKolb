import streamlit as st
import requests
import numpy as np
import pyperclip  # Python library to handle clipboard copying

# Constants
G = 6.674e-11  # Gravitational constant (m³/kg/s²)

# API endpoint for solar system objects
solar_system_api = "https://api.le-systeme-solaire.net/rest/bodies/"

# Dictionary of known celestial bodies, symbols, and images
horizons_bodies = {
    "Mercury": ("mercure", "☿", "https://upload.wikimedia.org/wikipedia/commons/d/d0/Mercury.gif"),
    "Venus": ("venus", "♀", "https://upload.wikimedia.org/wikipedia/commons/0/0e/Venus_Rotation_Movie.gif"),
    "Earth": ("terre", "⊕", "https://upload.wikimedia.org/wikipedia/commons/3/32/Earth_rotation.gif"),
    "Mars": ("mars", "♂", "https://upload.wikimedia.org/wikipedia/commons/3/34/Spinning_Mars.gif"),
    "Jupiter": ("jupiter", "♃", "https://upload.wikimedia.org/wikipedia/commons/6/6d/Neptune.gif"),
    "Saturn": ("saturne", "♄", "https://upload.wikimedia.org/wikipedia/commons/f/fe/Saturnoppositions-animated.gif"),
    "Neptune": ("neptune", "♆", "https://upload.wikimedia.org/wikipedia/commons/6/6d/Neptune.gif"),
    "Pluto": ("pluton", "♇", "https://upload.wikimedia.org/wikipedia/commons/f/f9/Pluto_rotation_movie.gif"),
    "Moon": ("lune", "☽", "https://upload.wikimedia.org/wikipedia/commons/c/c0/Lunar_libration_with_phase2.gif"),
    "Europa": ("europa", "🜁", "https://upload.wikimedia.org/wikipedia/commons/2/2d/Europa-rotationmovie.gif"),
    "Titan": ("titan", "🪐", "https://upload.wikimedia.org/wikipedia/commons/e/e2/PIA02146.gif"),
}

# Function to get planetary data
def get_planetary_data(body_name):
    try:
        response = requests.get(f"{solar_system_api}{body_name}", timeout=5)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {e}")
        return {}

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
        "Surface Gravity": (surface_gravity, "m/s²"),
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

# Convert value to long form for copying
def format_long_form(value):
    """Converts a value to long form (no scientific notation, full decimal expansion)."""
    if value is None:
        return ""
    return f"{value:.10f}".rstrip("0").rstrip(".")  # Removes unnecessary trailing zeros

# Streamlit UI
st.title("Celestial Mechanics Simulator")

selected_body = st.selectbox("Select a Celestial Body", list(horizons_bodies.keys()))

if st.button("Fetch Data"):
    st.write("Fetching data...")  
    planetary_data = get_planetary_data(selected_body)

    # Display centered and bold category title with planetary symbol
    symbol, image_url = horizons_bodies[selected_body][1], horizons_bodies[selected_body][2]
    st.markdown(f"<h2 style='text-align: center;'><b>{selected_body}</b> {symbol}</h2>", unsafe_allow_html=True)

    # Display image
    st.image(image_url, caption=f"Image of {selected_body}", use_container_width=True)

    # Display planetary data with copy buttons
    for key, (value, unit) in planetary_data.items():
        col1, col2 = st.columns([3, 1])

        # Convert value for LaTeX formatting
        formatted_value = format_value(key, value, unit)
        col1.latex(formatted_value)

        # Convert value for copying (long form)
        if value is not None:
            long_form_value = format_long_form(value)

            # Button copies value to clipboard
            if col2.button(f"📋 Copy {key}", key=f"copy_{key}"):
                pyperclip.copy(long_form_value)
                st.success(f"Copied: {long_form_value}")

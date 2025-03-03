import streamlit as st
import requests
import numpy as np

# Constants
G = 6.674e-11  # Gravitational constant (m³/kg/s²)

# API endpoint for solar system objects
solar_system_api = "https://api.le-systeme-solaire.net/rest/bodies/"

# Dictionary of known celestial bodies and their symbols
horizons_bodies = {
    "Mercury": ("mercure", "☿"), "Venus": ("venus", "♀"), "Earth": ("terre", "⊕"), "Mars": ("mars", "♂"),
    "Jupiter": ("jupiter", "♃"), "Saturn": ("saturne", "♄"), "Uranus": ("uranus", "♅"), "Neptune": ("neptune", "♆"),
    "Pluto": ("pluton", "♇"), "Ceres": ("ceres", "⚳"), "Eris": ("eris", "❄"), "Haumea": ("haumea", "💫"),
    "Makemake": ("makemake", "🌍"), "Moon": ("lune", "☽"), "Europa": ("europa", "🜁"), 
    "Ganymede": ("ganymede", "🜂"), "Callisto": ("callisto", "🜃"), "Io": ("io", "🔥"),
    "Triton": ("triton", "🌊"), "Enceladus": ("enceladus", "🧊"), "Titan": ("titan", "🪐"),
    "Vesta": ("vesta", "🌑"), "Pallas": ("pallas", "🌓"), "Hygiea": ("hygiea", "🌕")
}

# Function to get planetary data
def get_planetary_data(body_name):
    try:
        response = requests.get(f"{solar_system_api}{body_name}", timeout=5)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {e}")
        return {}, None  

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
    symbol = horizons_bodies[selected_body][1]
    st.markdown(f"<h2 style='text-align: center;'><b>{selected_body}</b> {symbol}</h2>", unsafe_allow_html=True)

    # JavaScript to enable clipboard copying
    st.markdown("""
        <script>
        function copyToClipboard(value) {
            navigator.clipboard.writeText(value);
            alert("Copied: " + value);
        }
        </script>
    """, unsafe_allow_html=True)

    # Display planetary data with copy buttons
    for key, (value, unit) in planetary_data.items():
        col1, col2 = st.columns([3, 1])

        # Convert value for LaTeX formatting
        formatted_value = format_value(key, value, unit)
        col1.latex(formatted_value)

        # Convert value for copying (long form)
        if value is not None:
            long_form_value = format_long_form(value)

            # Button triggers JavaScript function to copy value
            button_html = f"""
            <button onclick="copyToClipboard('{long_form_value}')">📋 Copy</button>
            """
            col2.markdown(button_html, unsafe_allow_html=True)

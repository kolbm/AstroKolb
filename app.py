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

# Celestial images for all known objects
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

# Streamlit UI
st.title("Celestial Mechanics Simulator")

selected_body = st.selectbox("Select a Celestial Body", list(horizons_bodies.keys()))

if st.button("Fetch Data"):
    planetary_data, orbits = get_planetary_data(selected_body)

    # Display centered and bold category title
    st.markdown(f"<h2 style='text-align: center;'><b>{selected_body}</b></h2>", unsafe_allow_html=True)

    # Display celestial symbol
    symbol = celestial_symbols.get(selected_body, random.choice(["🦄", "🐦‍🔥", "🦖", "🐲"]))
    st.markdown(f"<div style='text-align: center; font-size: 140px;'>{symbol}</div>", unsafe_allow_html=True)

    # Display planetary data
    for key, (value, unit) in planetary_data.items():
        st.latex(format_value(key, value, unit))

    # Display what the moon orbits (only if applicable)
    if orbits:
        st.latex(rf"\textbf{{Orbits}}: \text{{{orbits}}}")

    # Display celestial image
    if selected_body in celestial_images:
        st.image(celestial_images[selected_body], caption=f"Image of {selected_body}", use_container_width=True)

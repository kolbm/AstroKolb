def get_planetary_data(body_name):
    response = requests.get(f"{solar_system_api}{body_name}")
    if response.status_code != 200:
        return {}, None  # Ensure we always return TWO values

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
    
    # If the object is a moon, return its orbit information
    orbits_text = moon_orbits.get(body_name, None)

    return extracted_data, orbits_text  # Ensure TWO values are returned

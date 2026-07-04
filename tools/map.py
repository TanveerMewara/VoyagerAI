import folium

locations = {
    "tokyo": (35.6762, 139.6503),
    "japan": (35.6762, 139.6503),
    "paris": (48.8566, 2.3522),
    "dubai": (25.2048, 55.2708),
    "goa": (15.2993, 74.1240),
    "london": (51.5072, -0.1276),
}


def create_map(destination):
    destination = destination.strip().lower()

    lat, lon = locations.get(destination, (20.5937, 78.9629))

    m = folium.Map(
        location=[lat, lon],
        zoom_start=10
    )

    folium.Marker(
        [lat, lon],
        popup=destination.title()
    ).add_to(m)

    return m
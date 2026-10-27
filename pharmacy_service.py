
import requests

OVERPASS_URL = "https://overpass-api.de/api/interpreter"


def find_pharmacies(latitude, longitude, radius_km=5):
    radius_m = int(radius_km * 1000)

    query = f"""
    [out:json][timeout:25];
    (
      node["amenity"="pharmacy"]
      (around:{radius_m},{latitude},{longitude});

      way["amenity"="pharmacy"]
      (around:{radius_m},{latitude},{longitude});

      relation["amenity"="pharmacy"]
      (around:{radius_m},{latitude},{longitude});

      node["shop"="chemist"]
      (around:{radius_m},{latitude},{longitude});

      way["shop"="chemist"]
      (around:{radius_m},{latitude},{longitude});
    );
    out center tags;
    """

    response = requests.post(
        OVERPASS_URL,
        data={"data": query},
        timeout=35
    )

    response.raise_for_status()

    pharmacies = []

    for item in response.json().get("elements", []):
        tags = item.get("tags", {})
        center = item.get("center", {})

        lat = item.get("lat", center.get("lat"))
        lon = item.get("lon", center.get("lon"))

        if lat is None or lon is None:
            continue

        address_parts = [
            tags.get("addr:housenumber"),
            tags.get("addr:street"),
            tags.get("addr:suburb"),
            tags.get("addr:city")
        ]

        pharmacies.append({
            "name": tags.get("name", "Unnamed pharmacy"),
            "lat": float(lat),
            "lon": float(lon),
            "phone": (
                tags.get("phone")
                or tags.get("contact:phone")
            ),
            "opening_hours": tags.get("opening_hours"),
            "wheelchair": tags.get("wheelchair"),
            "address": ", ".join(
                part for part in address_parts if part
            )
        })

    return pharmacies


import math


def distance_km(lat1, lon1, lat2, lon2):
    earth_radius = 6371.0

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)

    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1)
        * math.cos(phi2)
        * math.sin(dlambda / 2) ** 2
    )

    return 2 * earth_radius * math.asin(
        math.sqrt(a)
    )


def rank_pharmacies(
    pharmacies, user_lat, user_lon, preferences
):
    ranked = []

    for pharmacy in pharmacies:
        item = dict(pharmacy)

        distance = distance_km(
            user_lat,
            user_lon,
            item["lat"],
            item["lon"]
        )

        item["distance_km"] = distance

        # Maximum distance contribution: 60 points
        score = max(
            0.0,
            60.0 * (1.0 - distance / 10.0)
        )

        # Accessibility contribution
        if preferences.get("wheelchair"):
            if item.get("wheelchair") == "yes":
                score += 25
            elif item.get("wheelchair") == "limited":
                score += 10

        # Useful contact and opening information
        if item.get("phone"):
            score += 8

        if item.get("opening_hours"):
            score += 7

        item["score"] = round(min(score, 100), 1)

        ranked.append(item)

    if preferences.get("wheelchair"):
        ranked.sort(
            key=lambda p: (
                p.get("wheelchair") != "yes",
                -p["score"],
                p["distance_km"]
            )
        )
    else:
        ranked.sort(
            key=lambda p: (
                -p["score"],
                p["distance_km"]
            )
        )

    return ranked

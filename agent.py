
from nlp_engine import understand_request
from pharmacy_service import find_pharmacies
from recommender import rank_pharmacies


class CareFinderAgent:

    def __init__(self, default_radius_km=5):
        self.default_radius_km = default_radius_km

    def run(
        self,
        user_request,
        latitude,
        longitude,
        radius_km=None
    ):
        actions = []
        safety_notes = []

        if not user_request.strip():
            return {
                "interpreted_request": {},
                "actions": ["Request was empty."],
                "results": [],
                "safety_notes": [
                    "Please describe your requirements."
                ]
            }

        # 1. Understand the request
        preferences = understand_request(user_request)

        actions.append(
            "Parsed natural-language preferences."
        )

        # 2. Determine search radius
        if radius_km is None:
            radius_km = self.default_radius_km

        if preferences.get("max_km") is not None:
            radius_km = min(
                radius_km,
                preferences["max_km"]
            )

        radius_km = max(
            1.0,
            min(float(radius_km), 20.0)
        )

        actions.append(
            f"Search radius selected: {radius_km} km."
        )

        # 3. Search pharmacy listings
        pharmacies = find_pharmacies(
            latitude,
            longitude,
            radius_km
        )

        actions.append(
            f"Retrieved {len(pharmacies)} listings."
        )

        # 4. Rank the results
        results = rank_pharmacies(
            pharmacies,
            latitude,
            longitude,
            preferences
        )

        actions.append(
            "Ranked pharmacies by suitability."
        )

        # 5. Provide safety guidance
        if preferences.get("medicine"):
            safety_notes.append(
                "Live stock is unavailable. Call to confirm "
                "medicine availability and prescription requirements."
            )

        if preferences.get("open_now"):
            safety_notes.append(
                "Opening-hours data may be incomplete. "
                "Call before travelling."
            )

        if preferences.get("wheelchair"):
            safety_notes.append(
                "Confirm wheelchair access with the pharmacy."
            )

        safety_notes.append(
            "Do not substitute prescribed medicines without "
            "consulting a pharmacist or clinician."
        )

        return {
            "interpreted_request": preferences,
            "actions": actions,
            "results": results,
            "safety_notes": safety_notes
        }


def main():
    print("CareFinder Pharmacy Agent")

    try:
        latitude = float(
            input("Latitude [12.9716]: ") or 12.9716
        )

        longitude = float(
            input("Longitude [77.5946]: ") or 77.5946
        )

        radius = float(
            input("Radius in km [5]: ") or 5
        )

        request = input(
            "What pharmacy do you need? "
        ).strip()

        agent = CareFinderAgent(radius)

        response = agent.run(
            request,
            latitude,
            longitude,
            radius
        )

        print("\nINTERPRETED REQUEST")

        for key, value in response[
            "interpreted_request"
        ].items():
            print(f"{key}: {value}")

        print("\nAGENT ACTIONS")

        for action in response["actions"]:
            print("-", action)

        print("\nRECOMMENDED PHARMACIES")

        for i, pharmacy in enumerate(
            response["results"][:10], start=1
        ):
            print(
                f"\n{i}. {pharmacy['name']}"
            )

            print(
                f"Distance: "
                f"{pharmacy['distance_km']:.2f} km"
            )

            print(
                f"Score: {pharmacy['score']}/100"
            )

            print(
                "Wheelchair access:",
                pharmacy.get("wheelchair") or "Unknown"
            )

            print(
                "Opening hours:",
                pharmacy.get("opening_hours") or "Not listed"
            )

            if pharmacy.get("address"):
                print("Address:", pharmacy["address"])

            if pharmacy.get("phone"):
                print("Phone:", pharmacy["phone"])

            print(
                "Directions:",
                "https://www.google.com/maps/dir/?api=1"
                f"&destination={pharmacy['lat']},"
                f"{pharmacy['lon']}"
            )

        if not response["results"]:
            print("No pharmacies found.")

        print("\nSAFETY NOTES")

        for note in response["safety_notes"]:
            print("-", note)

    except ValueError:
        print("Enter valid numeric coordinates and radius.")

    except Exception as error:
        print("Search failed:", error)


if __name__ == "__main__":
    main()

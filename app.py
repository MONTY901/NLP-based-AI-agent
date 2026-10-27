
import streamlit as st

from nlp_engine import understand_request
from pharmacy_service import find_pharmacies
from recommender import rank_pharmacies


st.set_page_config(
    page_title="CareFinder",
    page_icon="💊",
    layout="wide"
)

st.title("CareFinder")
st.subheader(
    "A pharmacy finder designed for older adults"
)

st.write(
    "Describe your needs in everyday language "
    "to find suitable nearby pharmacies."
)

st.warning(
    "Pharmacy listings may be incomplete. "
    "Call before travelling. Live medicine stock "
    "is not available in this prototype."
)

with st.sidebar:
    st.header("Your search location")

    latitude = st.number_input(
        "Latitude",
        value=12.9716,
        format="%.6f"
    )

    longitude = st.number_input(
        "Longitude",
        value=77.5946,
        format="%.6f"
    )

    radius_km = st.slider(
        "Search radius (km)",
        1, 20, 5
    )

request = st.text_area(
    "What do you need?",
    placeholder=(
        "Find a pharmacy with wheelchair access "
        "within 3 km."
    ),
    height=100
)

if st.button(
    "Find suitable pharmacies",
    type="primary",
    use_container_width=True
):
    if not request.strip():
        st.error("Please enter your requirements.")
    else:
        preferences = understand_request(request)

        search_radius = radius_km

        if preferences["max_km"] is not None:
            search_radius = min(
                search_radius,
                preferences["max_km"]
            )

        st.subheader("Your preferences")
        st.write(preferences)

        try:
            with st.spinner(
                "Searching pharmacy listings..."
            ):
                pharmacies = find_pharmacies(
                    latitude,
                    longitude,
                    search_radius
                )

            results = rank_pharmacies(
                pharmacies,
                latitude,
                longitude,
                preferences
            )

            st.subheader("Recommended pharmacies")

            if not results:
                st.info(
                    "No listings found. Try a wider radius."
                )

            if preferences.get("medicine"):
                st.info(
                    "Call to confirm medicine stock "
                    "and prescription requirements."
                )

            for pharmacy in results:
                with st.container(border=True):
                    st.subheader(pharmacy["name"])

                    st.write(
                        f"Distance: "
                        f"{pharmacy['distance_km']:.2f} km"
                    )

                    st.write(
                        f"Suitability score: "
                        f"{pharmacy['score']}/100"
                    )

                    st.write(
                        "Wheelchair access: "
                        f"{pharmacy.get('wheelchair') or 'Unknown'}"
                    )

                    st.write(
                        "Opening hours: "
                        f"{pharmacy.get('opening_hours') or 'Not listed'}"
                    )

                    if pharmacy.get("address"):
                        st.write(
                            "Address: " + pharmacy["address"]
                        )

                    if pharmacy.get("phone"):
                        st.write(
                            "Phone: " + pharmacy["phone"]
                        )

                    maps_url = (
                        "https://www.google.com/maps/dir/?api=1"
                        f"&destination={pharmacy['lat']},"
                        f"{pharmacy['lon']}"
                    )

                    st.link_button(
                        "Get directions",
                        maps_url
                    )

        except Exception as error:
            st.error(
                "Unable to search pharmacy listings. "
                "Check your internet connection."
            )
            st.caption(str(error))

st.divider()

st.subheader("Safety and accessibility")

st.markdown(
    "- Confirm opening hours and wheelchair access by phone.\n"
    "- Medicine inventory is not verified by this application.\n"
    "- Consult a pharmacist or clinician about medicines."
)

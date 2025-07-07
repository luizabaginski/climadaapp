import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from climada.hazard.centroids import Centroids
from climada.hazard import Hazard

st.set_page_config(page_title="CLIMADA Centroid Input App2", page_icon="🌍")

st.title("🌍 CLIMADA Centroid Input App2")

# User inputs
lat_input = st.text_input("Enter latitudes (comma-separated)", "50,55,70")
lon_input = st.text_input("Enter longitudes (comma-separated)", "10,20,30")
intensity_input = st.text_area(
    "Enter intensity matrix (rows = events, columns = centroids)",
    "1,2,3\n2,1,0\n0,2,1"
)

run_clicked = st.button("Run CLIMADA")

if run_clicked:
    try:
        # Parse latitude and longitude
        lat_array = np.array([float(val.strip()) for val in lat_input.split(',')])
        lon_array = np.array([float(val.strip()) for val in lon_input.split(',')])

        # Parse intensity matrix
        intensity_matrix = np.array([
            [float(x.strip()) for x in row.split(',')] for row in intensity_input.strip().split('\n')
        ])

        # Check shape compatibility
        if intensity_matrix.shape[1] != len(lat_array):
            raise ValueError("Number of centroids must match number of columns in intensity matrix.")

        # Create centroids and hazard
        centroids = Centroids(lat=lat_array, lon=lon_array)
        hazard = Hazard()
        hazard.intensity = intensity_matrix
        hazard.centroids = centroids
        hazard.frequency = np.ones(intensity_matrix.shape[0])
        hazard.event_id = np.arange(intensity_matrix.shape[0])

        st.success("Centroids and hazard created successfully!")

        # Show parsed data
        st.write("Latitude array:")
        st.dataframe(lat_array)

        st.write("Longitude array:")
        st.dataframe(lon_array)

        st.write("Hazard intensity matrix:")
        st.dataframe(intensity_matrix)

        # Select event or mean to visualize
        st.subheader("Select event to visualize:")
        options = [f"Event {i}" for i in range(intensity_matrix.shape[0])] + ["Mean"]
        selected = st.selectbox("Select event to visualize:", options)

        try:
            fig, ax = plt.subplots()

            if selected == "Mean":
                mean_values = hazard.intensity.mean(axis=0)
                sc = ax.scatter(lon_array, lat_array, c=mean_values, cmap='viridis', s=100)
                ax.set_title("Mean Hazard Intensity")
                ax.set_xlabel("Longitude")
                ax.set_ylabel("Latitude")
                plt.colorbar(sc, ax=ax, label="Intensity")
            else:
                idx = int(selected.split()[-1])
                event_values = hazard.intensity[idx]
                sc = ax.scatter(lon_array, lat_array, c=event_values, cmap='plasma', s=100)
                ax.set_title(f"Hazard Intensity for Event {idx}")
                ax.set_xlabel("Longitude")
                ax.set_ylabel("Latitude")
                plt.colorbar(sc, ax=ax, label="Intensity")

            st.pyplot(fig)

        except Exception as plot_error:
            st.error(f"Something went wrong while plotting: {plot_error}")

    except Exception as e:
        st.error(f"Error parsing inputs: {e}")

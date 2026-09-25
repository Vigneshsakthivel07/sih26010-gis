import sys
import os

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

sys.path.insert(0, PROJECT_ROOT)

import streamlit as st
import tempfile

from src.validation.api import validate_land_parcel

st.set_page_config(
    page_title="Land Parcel Validation",
    page_icon="🗺️",
    layout="wide"
)


st.title("🗺️ Land Parcel Validation System")

st.write(
    "Validate historical FMB geometry against modern survey data "
    "using spatial consistency checks."
)

st.divider()

st.header("📂 Input Data")

fmb_file = st.file_uploader(
    "Upload Digitized FMB CSV",
    type=["csv"]
)

survey_file = st.file_uploader(
    "Upload Modern Survey CSV",
    type=["csv"]
)

st.header("⚙️ Validation Settings")

tolerance = st.number_input(
    "Maximum allowed deviation (metres)",
    min_value=0.1,
    value=1.0,
    step=0.1
)

minimum_overlap = st.number_input(
    "Minimum required overlap (%)",
    min_value=0.0,
    max_value=100.0,
    value=90.0,
    step=1.0
)

st.divider()


if st.button("🔍 Validate Parcel", type="primary"):

    if fmb_file is None:
        st.warning("Please upload the FMB CSV.")

    elif survey_file is None:
        st.warning("Please upload the modern survey CSV.")

    else:

        # Save uploaded FMB temporarily
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".csv"
        ) as f:
            f.write(fmb_file.getbuffer())
            fmb_path = f.name

        # Save uploaded survey temporarily
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".csv"
        ) as f:
            f.write(survey_file.getbuffer())
            survey_path = f.name

        try:

            with st.spinner("Running GIS validation..."):

                result = validate_land_parcel(
                    fmb_file=fmb_path,
                    survey_file=survey_path,
                    control_ids=["P1", "P3", "P7"],
                    tolerance=tolerance,
                    minimum_overlap=minimum_overlap,
                    digitized_fmb=True
                )

            st.divider()

            # Final status
            if result["status"] == "VERIFIED":
                st.success("🟢 VERIFIED")
            else:
                st.error("🔴 MISMATCH")

            st.subheader("📊 Validation Results")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Maximum Deviation",
                    f"{result['maximum_deviation']:.3f} m"
                )

            with col2:
                st.metric(
                    "Polygon Overlap",
                    f"{result['overlap_percentage']:.2f}%"
                )

            with col3:
                st.metric(
                    "Points Outside",
                    result["points_outside"]
                )

        except Exception as e:
            st.error(f"Validation failed: {e}")

        finally:
            os.unlink(fmb_path)
            os.unlink(survey_path)

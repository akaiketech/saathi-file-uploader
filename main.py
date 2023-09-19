import streamlit as st
import requests
from io import BytesIO
import os
from loguru import logger
import sentry_sdk
from sentry_sdk.integrations.loguru import LoguruIntegration
from sentry_sdk.integrations.loguru import LoggingLevels

UPLOADER_SENTRY_DSN = os.environ.get("UPLOADER_SENTRY_DSN")
UPLOAD_API_URL = os.environ.get("UPLOAD_API_URL")

# Initialize Sentry
sentry_sdk.init(
    dsn=UPLOADER_SENTRY_DSN,
    integrations=[LoguruIntegration(level=LoggingLevels.INFO.value,        
                                    event_level=LoggingLevels.INFO.value)],
    traces_sample_rate=1.0,
    release="saathi-file-uploader@1.0"
)

# Set the title and description of the app
st.set_page_config(
    page_title="SAATHI - File Uploader",
    page_icon=":file_folder:",
    layout="wide"
)

# Define the Loguru logger configuration
logger.add("app.log", rotation="10 MB", retention="7 days", level="INFO")

st.markdown(
    """
    <style>
    .stFrame {
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stButton button {
        background-color: #008CBA;
        color: white;
        border: none;
        padding: 12px 24px;
        margin: 0 auto;
        display: block;
        border-radius: 10px;
    }
    .stRadio > div {
        margin-bottom: 10px;
    }
    .stMultiselect {
        margin-top: 10px;
    }
    .stHeader {
        font-size: 24px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def main():
    st.title("SAATHI - File Uploader")
    st.write("This app allows you to upload files and associate them with various scheme details.")

    # Create columns for better layout
    col1, col2 = st.columns(2)

    with col1:
        st.header("Fill the Scheme Details")

        scheme_gender = st.radio("Select Gender", ["General", "Female"])
        scheme_category = st.multiselect("Select Category", ["Schedule Caste (SC)", "Schedule Tribe (ST) ", "General", "Other Backward Classes (OBC)"])
        scheme_source = st.radio("Select Scheme Source", ["State", "Central", "Bank"])
        scheme_type = st.multiselect("Select Scheme Type", ["Loan", "Insurance", "Education", "Savings", "Welfare", "Pension"])
        scheme_description = st.text_area("Scheme Description", "")

    with col2:
        st.header("File Upload")
        uploaded_file = st.file_uploader("Choose a file", type=["docx", "pdf"])

        # Upload button with custom styling
        if st.button("Upload", key="upload_button"):
            # Check if a file has been uploaded
            if uploaded_file is not None:
                file_content = BytesIO(uploaded_file.read())
                files = {"file": (uploaded_file.name, file_content)}

                params = {
                    "scheme_gender": scheme_gender,
                    "scheme_source": scheme_source, 
                    "scheme_description": scheme_description,
                }
                
                data = {
                    "scheme_type": scheme_type,
                    "scheme_category": scheme_category
                }
                
                try:
                    # Send the request to the API
                    res = requests.post(UPLOAD_API_URL, params=params, data=data, files=files)
                    res.raise_for_status()

                    # Log successful upload
                    logger.info(f"File uploaded successfully: {uploaded_file.name} with fields {data}{params}")

                    st.success(f"File uploaded successfully: {uploaded_file.name}")
                    st.markdown("### Summary")
                    st.json(data)
                    st.json(params)

                except Exception as e:
                    # Log error and send it to Sentry
                    logger.error(f"Upload failed: {str(e)}")
                    sentry_sdk.capture_exception(e)
                    st.error("Upload failed. Please try again later.")


if __name__ == "__main__":
    main()

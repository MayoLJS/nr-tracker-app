import pandas as pd
import requests
import streamlit as st
from io import BytesIO

# Streamlit App
st.title("IHS NR Tracker App")
st.write("Search and explore NR data providing a site ID.")

# Replace this with your shared link
shared_link = "https://1drv.ms/x/c/e9d2c9c9c1997df7/ETjIp_jnagZOiSoc6nOXDoMBipfwxe5muyD-TW009pwEeA?download=1"

# Cache the download and data processing function (for Button 1)
@st.cache_data
def download_and_process_file(shared_link):
    response = requests.get(shared_link)
    if response.status_code == 200:
        try:
            # Save the file temporarily in memory
            excel_file = BytesIO(response.content)
            
            # Load specific sheets
            ihs_nr_data = pd.read_excel(excel_file, sheet_name="ihs nr data", engine="openpyxl")
            ihs_matrix = pd.read_excel(excel_file, sheet_name="ihsmatrix", engine="openpyxl")
            
            # Merge tables on 'ihs_id'
            merged_data = pd.merge(ihs_nr_data, ihs_matrix, on="ihs_id", how="inner")
            return merged_data
        except Exception as e:
            st.error(f"An error occurred while processing the data: {e}")
            return None
    else:
        st.error("Failed to download the file. Please check the shared link.")
        return None

# Non-cached version to force a fresh download (for Button 2)
def download_and_process_file_no_cache(shared_link):
    response = requests.get(shared_link)
    if response.status_code == 200:
        try:
            # Save the file temporarily in memory
            excel_file = BytesIO(response.content)
            
            # Load specific sheets
            ihs_nr_data = pd.read_excel(excel_file, sheet_name="ihs nr data", engine="openpyxl")
            ihs_matrix = pd.read_excel(excel_file, sheet_name="ihsmatrix", engine="openpyxl")
            
            # Merge tables on 'ihs_id'
            merged_data = pd.merge(ihs_nr_data, ihs_matrix, on="ihs_id", how="inner")
            return merged_data
        except Exception as e:
            st.error(f"An error occurred while processing the data: {e}")
            return None
    else:
        st.error("Failed to download the file. Please check the shared link.")
        return None

# Create a search box at the beginning
site_id = st.text_input("Enter a valid site ID to search (case-insensitive):")

# Initialize merged_data to None if not already in session state
if "merged_data" not in st.session_state:
    st.session_state.merged_data = None

# Button 1 - Load and Process Data (Using Cached Data)
if st.button("Load and Process Data"):
    if shared_link:
        # Only process and cache data if not in session state
        if st.session_state.merged_data is None:
            st.session_state.merged_data = download_and_process_file(shared_link)

        if st.session_state.merged_data is not None:
            st.success("Data successfully merged!")
            
            # Select relevant columns
            df = st.session_state.merged_data[['request_date', 'ihs_id', 'alt_id', 'fault', 'approval', 'total', 
                                              'job_status', 'Regional Manager', 'Cluster']]
            
            if site_id:
                # Filter by `ihs_id`
                filtered_df_ihs = df[df['ihs_id'].str.contains(site_id, na=False, case=False)]
                
                if not filtered_df_ihs.empty:
                    st.write("### Results from `ihs_id`")
                    st.dataframe(filtered_df_ihs)
                else:
                    # Filter by `alt_id`
                    filtered_df_alt = df[df['alt_id'].str.contains(site_id, na=False, case=False)]
                    
                    if not filtered_df_alt.empty:
                        st.write("### Results from `alt_id`")
                        st.dataframe(filtered_df_alt)
                    else:
                        st.warning("No results found for the provided site ID.")
    else:
        st.warning("No shared link provided. Update the script with the link.")

# Button 2 - Load and Process Data (Refreshed) (Bypasses Cache)
if st.button("Load and Process Data (Refreshed)"):
    if shared_link:
        # Force reload and bypass cache (use the non-cached version)
        st.session_state.merged_data = None  # Reset the session state
        st.session_state.merged_data = download_and_process_file_no_cache(shared_link)

        if st.session_state.merged_data is not None:
            st.success("Data successfully refreshed and merged!")
            
            # Select relevant columns
            df = st.session_state.merged_data[['request_date', 'ihs_id', 'alt_id', 'fault', 'approval', 'total', 
                                              'job_status', 'Regional Manager', 'Cluster']]
            
            if site_id:
                # Filter by `ihs_id`
                filtered_df_ihs = df[df['ihs_id'].str.contains(site_id, na=False, case=False)]
                
                if not filtered_df_ihs.empty:
                    st.write("### Results from `ihs_id`")
                    st.dataframe(filtered_df_ihs)
                else:
                    # Filter by `alt_id`
                    filtered_df_alt = df[df['alt_id'].str.contains(site_id, na=False, case=False)]
                    
                    if not filtered_df_alt.empty:
                        st.write("### Results from `alt_id`")
                        st.dataframe(filtered_df_alt)
                    else:
                        st.warning("No results found for the provided site ID.")
    else:
        st.warning("No shared link provided. Update the script with the link.")
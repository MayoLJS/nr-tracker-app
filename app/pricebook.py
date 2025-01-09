import pandas as pd
import requests
import streamlit as st

# Set up Streamlit interface
st.title("🔍 IHS Pricebook Search")  # Streamlit: Add title with an icon
st.write("Search the IHS Pricebook by entering a fault name below.")  # Description text

# Shared link for the Excel file
shared_link = "https://1drv.ms/x/c/e9d2c9c9c1997df7/ETjIp_jnagZOiSoc6nOXDoMBipfwxe5muyD-TW009pwEeA?download=1"

# Cache function to load and preprocess the data
@st.cache_data(max_entries=5)  # Cache data for efficiency
def load_data(shared_link: str):  # Function to load data from the shared link
    response = requests.get(shared_link)  # Download the file
    if response.status_code == 200:  # Verify successful download
        with open("temp.xlsx", "wb") as file:  # Save the file temporarily
            file.write(response.content)

        # Load the Excel file into a DataFrame
        df = pd.read_excel(
            "temp.xlsx",
            sheet_name="ihspricebook",
            engine="openpyxl"
        )
        # Select relevant columns
        df = df[['fault', 'Approval', 'Severity', 'Essense']]
        return df
    else:
        st.write("❌ Failed to download the file. Check your shared link.")
        return None

# Load the dataset
df = load_data(shared_link)

# Automatically display the full dataframe if data is available
if df is not None:  # Check if data is successfully loaded
    st.write("### Full Pricebook Data")
    st.dataframe(df, hide_index=True)  # Display the full dataset without the index

    # **User Input Section**
    fault_input = st.text_input("Enter fault name to filter:", "").strip()  # Text input for fault filtering

    # Filter the dataframe based on user input
    if fault_input:
        filtered_df = df[df['fault'].str.contains(fault_input, na=False, case=False)]  # Filter DataFrame

        if not filtered_df.empty:  # Check if any matches are found
            st.write("### Filtered Results")
            st.dataframe(filtered_df, hide_index=True)  # Display filtered DataFrame
        else:
            st.write("🔍 No matching results found. Try a different fault name.")
else:
    st.write("⚠️ No data available. Check the shared link or try reloading.")

import pandas as pd
import requests
import streamlit as st

# Set up Streamlit interface
st.title('IHS Pricebook Search')
st.write('Enter a fault to search for in the pricebook.')

# Replace this with your shared link
shared_link = "https://1drv.ms/x/c/e9d2c9c9c1997df7/ETjIp_jnagZOiSoc6nOXDoMBipfwxe5muyD-TW009pwEeA?download=1"

# Cache the function to download and load the Excel file
@st.cache_data
def load_data(shared_link):
    # Download the file
    response = requests.get(shared_link)
    if response.status_code == 200:  # Ensure the file is downloaded successfully
        with open("temp.xlsx", "wb") as file:
            file.write(response.content)

        # Load the data from the Excel sheet
        df = pd.read_excel("temp.xlsx", sheet_name="ihspricebook", engine="openpyxl")

        # Select only the relevant columns
        df = df[['fault', 'Approval', 'Severity', 'Essense']]
        return df
    else:
        st.write("Failed to download the file. Check your shared link.")
        return None

# Load the data with caching
df = load_data(shared_link)

# Input box for user to enter the fault
item = st.text_input("Enter item name:", "").strip()

# Add a search button
if st.button("Search"):
    if df is not None:  # Check if data is successfully loaded
        if item:
            # Filter based on the user's input
            filtered_df = df[df['fault'].str.contains(item, na=False, case=False)]

            if not filtered_df.empty:
                # Display the filtered table in Streamlit using st.dataframe
                st.dataframe(filtered_df)
            else:
                st.write("No matching results found.")
        else:
            st.write("Please enter a fault to search.")
    else:
        st.write("No data available.")

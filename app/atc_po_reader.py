import streamlit as st
import pandas as pd
from tabula.io import read_pdf
import warnings

# Suppress warnings
warnings.filterwarnings("ignore", category=pd.errors.SettingWithCopyWarning)

# Streamlit app title and description
st.title("📊 PDF Table Extractor")
st.subheader("Upload a PDF to extract tabular data from it, and download it as a CSV file.")
st.markdown("This app allows you to upload a PDF containing tables and automatically extract them for further use.")

# File upload section with a more prominent upload button
uploaded_file = st.file_uploader("Choose a PDF file to upload", type=["pdf"], label_visibility="collapsed")

# Function to process a single page
def process_page(page_data):
    try:
        if 'Description' in page_data.columns:
            page_data['Description'] = page_data['Description'].str.replace(r'\bReplacement\b', '', regex=True)
            page_data = page_data[['Description', 'QTY', 'Unit Price']]
            page_data.rename(columns={'Description': 'Job', 'Unit Price': 'UOM Unit Price'}, inplace=True)

            # Extract Site ID and clean the Job column
            page_data['Site ID'] = page_data['Job'].str.extract(r'@(\S{6})', expand=False).fillna('')
            page_data['Job'] = page_data['Job'].str.replace(r'@.*', '', regex=True).str.strip()

            # Filter out rows with 'Total' or missing data
            page_data = page_data[~page_data['Job'].str.contains('Total', na=False)]
            page_data.dropna(subset=['Job'], inplace=True)

            return page_data[['Site ID', 'Job', 'QTY', 'UOM Unit Price']]
        else:
            return pd.DataFrame(columns=['Site ID', 'Job', 'QTY', 'UOM Unit Price'])
    except Exception:
        return pd.DataFrame(columns=['Site ID', 'Job', 'QTY', 'UOM Unit Price'])

# Function to process the PDF and extract tables
def process_pdf(file_path):
    try:
        # Extract tables from the PDF
        tables = read_pdf(file_path, pages='all', multiple_tables=True)

        if not tables or len(tables) < 2:
            st.error("No valid tables were found in the PDF.")
            return None

        # Process Page 1 (second table in the list)
        page1 = tables[1]

        # Clean and format Page 1
        page1.iloc[:, 0] = page1.iloc[:, 0].astype(str)
        page1.columns = page1.iloc[1]
        page1 = page1.iloc[2:].reset_index(drop=True)
        page1 = page1[page1.iloc[:, 0].str.match('^\d')]

        # Further processing for Page 1
        table1 = page1.copy()
        table1['UOM Unit Price'] = table1['UOM Unit Price'].str.replace('Each', '', regex=False)
        table1['UOM Unit Price'] = table1['UOM Unit Price'].str.replace(',', '', regex=False).astype(float)

        table1['not needed'] = table1.iloc[:, 0].str.extract(r'^(\S+)')
        table1['Job'] = table1.iloc[:, 0].str.split(n=1).str[1].str.strip()
        table1['Job'] = table1['Job'].str.replace(r'\bReplacement\b', '', regex=True)
        table1['Site ID'] = table1.iloc[:, 0].str.extract(r'@(\S{6})', expand=False).fillna('')
        table1['Job'] = table1['Job'].str.replace(r'@.*', '', regex=True)

        # Extract relevant columns for Page 1
        PO_table1 = table1[['Site ID', 'Job', 'QTY', 'UOM Unit Price']]

        # Process additional tables (if any)
        po_tables = [PO_table1]  # Start with Page 1 data
        for i in range(2, len(tables)):
            additional_table = process_page(tables[i])
            po_tables.append(additional_table)

        # Concatenate all the processed tables
        PO_Table = pd.concat(po_tables, ignore_index=True)
        PO_Table['Job'] = PO_Table['Job'].str.strip()

        # Remove rows with "Total" and drop any residual invalid rows
        PO_Table = PO_Table[~PO_Table['Job'].str.contains('Total', na=False)]
        PO_Table.dropna(subset=['Job'], inplace=True)

        return PO_Table

    except Exception as e:
        st.error(f"An error occurred while processing the PDF: {str(e)}")
        return None

# Main app logic
if uploaded_file is not None:
    # Save the uploaded file temporarily
    with open("temp.pdf", "wb") as f:
        f.write(uploaded_file.read())

    # Process the PDF and extract the tables
    PO_table = process_pdf("temp.pdf")

    if PO_table is not None and not PO_table.empty:
        # Display the extracted table with custom styling
        st.success("📊 Table extracted successfully!")
        
        # Highlight numeric columns only
        numeric_columns = PO_table.select_dtypes(include=['number'])
        if not numeric_columns.empty:
            st.dataframe(PO_table.style.highlight_max(axis=0, color='lightblue'))
        else:
            st.dataframe(PO_table)  # Display without styling if no numeric columns exist

        # Provide an option to download the table as a CSV file
        csv = PO_table.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Download CSV",
            data=csv,
            file_name="PO_Table.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.warning("❌ No valid data to display or save.")

import streamlit as st
import pandas as pd
import requests
from io import BytesIO
import plotly.express as px
import plotly.graph_objects as go
from hashlib import sha256


# Cache Data Load Function
@st.cache_data(max_entries=5)  # Keeps the cache to 5 entries
def load_data(shared_link: str):
    response = requests.get(shared_link)
    if response.status_code == 200:
        try:
            excel_file = BytesIO(response.content)

            # Load specific sheets
            atc_nr_data = pd.read_excel(excel_file, sheet_name="atc nr data", engine="openpyxl")
            atc_matrix = pd.read_excel(excel_file, sheet_name="atcmatrix", engine="openpyxl")

            # Merge tables on 'ihs_id'
            merged_data = pd.merge(atc_nr_data, atc_matrix, on="atc_id", how="inner")

            # Ensure 'revenue_month' is datetime and handle invalid dates
            # List of columns to convert to datetime
            date_cols = ['month', 'invoice', 'sav_date']
            # Apply pd.to_datetime() to each column in the list
            merged_data[date_cols] = merged_data[date_cols].apply(pd.to_datetime, errors='coerce')


            # Specify the list of desired columns
            columns_to_select = [
                    'jobcode', 'category', 'description', 'job', 'atc_id', 'region', 
                    'state', 'cluster', 'regional_supervisor', 'year', 'sav_date',
                    'month', 'qty', 'unit', 'revenue', 'qty_used', 'unit_used', 'expense', 
                    'rs_proposed', 'job_status', 'sav_doc', 'po', 'invoice', 
                    'status', 'comment'
]

            
            # Filter the dataframe to keep only the specified columns
            filtered_data = merged_data[columns_to_select]

            return filtered_data
        except Exception as e:
            st.error(f"An error occurred while processing the data: {e}")
            return None
    else:
        st.error("Failed to download the file. Please check the shared link.")
        return None


# Shared link to download the file
shared_link = "https://1drv.ms/x/c/e9d2c9c9c1997df7/ETjIp_jnagZOiSoc6nOXDoMBipfwxe5muyD-TW009pwEeA?download=1"

# Call the function to load the data
df = load_data(shared_link)



#####################################################
########## UI
#####################################################

st.title('💼 Non Routine - ATC')

# Reload Data Button
if st.button('Reload new data'):
    st.cache_data.clear()
atc_id, job_filter, job_status_filter, jobcode_filter, region_filter = st.columns(5, gap='medium')

# Alt ID Search box (using text_input for dynamic filtering)
with atc_id:
    search_text = st.text_input('Search alt_id', '').strip()
    filtered_df = df[df['atc_id'].str.contains(search_text, case=False, na=False)] if search_text else df
# Requirement Filter
with job_filter:
    job_options = filtered_df['job'].unique()
    selected_job = st.selectbox('Select job', [''] + list(job_options))
# Job Status Filter
with job_status_filter:
    status_options = filtered_df['job_status'].unique()
    selected_status = st.selectbox('Select Job Status', [''] + list(status_options))
# Reference Filter
with jobcode_filter:
    jc_options = filtered_df['jobcode'].unique()
    selected_jc = st.selectbox('Select jobcode', [''] + list(jc_options))
# Region Filter
with region_filter:
    region_options = filtered_df['region'].unique()
    selected_region = st.selectbox('Select Region', [''] + list(region_options))

# Apply Filters to DataFrame
if selected_job:
    filtered_df = filtered_df[filtered_df['job'] == selected_job]
if selected_status:
    filtered_df = filtered_df[filtered_df['job_status'] == selected_status]
if selected_jc:
    filtered_df = filtered_df[filtered_df['jobcode'] == selected_ref]
if selected_region:
    filtered_df = filtered_df[filtered_df['region'] == selected_region]


st.markdown('<h1 style="font-size: 30px;">NR</h1>', unsafe_allow_html=True)
# Display Dataframe
with st.expander('**Expand**', icon='⚙️'):
    if filtered_df is not None:
        st.dataframe(filtered_df, hide_index=True)
    else:
        st.write("No data to display.")
        
        

st.markdown('<h1 style="font-size: 30px;">Pending Documents</h1>', unsafe_allow_html=True)

# Filter data based on the conditions: job_status = 'Closed' and sav_doc is blank
pending_df = filtered_df[(filtered_df['job_status'] == 'Closed') & (filtered_df['sav_doc'].isna())]

# Create the layout using columns for filters, and download button on one line
col1, col2, col3 = st.columns([2, 1, 1])

# Filter and display controls in columns
with col1:
    # PO Filter (single selection)
    po_filter = st.selectbox('Select PO Filter', ['All', 'PO available', 'No PO'], key='po_filter_ui')

with col2:
    # Regional Supervisors Filter (multi-selection)
    regional_manager_filter = st.multiselect('Select Regional Supervisors', filtered_df['rs_proposed'].unique(), key='regional_supervisors_ui')

# Filter data based on the selected PO options
if po_filter == 'PO available':
    pending_df_po = pending_df[pending_df['po'].notna()]
elif po_filter == 'No PO':
    pending_df_po = pending_df[pending_df['po'].isna()]
else:
    pending_df_po = pending_df  # "All" option, show all data

# Apply multi-filter for regional supervisors
if regional_manager_filter:
    pending_df_po = pending_df_po[pending_df_po['rs_proposed'].isin(regional_manager_filter)]

# Aggregate the revenue by regional supervisor based on the filters
aggregated_data = pending_df_po.groupby('rs_proposed')['revenue'].sum().reset_index(name='Accrued')

# Display the aggregated revenue metric
total_revenue = aggregated_data['Accrued'].sum()
st.metric(label="Accrued (₦)", value=f"{total_revenue:,.2f}")

# Create a bar chart using Plotly with amount displayed on each bar
fig = px.bar(aggregated_data, x='rs_proposed', y='Accrued', 
             title='Pending Documentation',
             labels={'Accrued': 'Accrued Revenue'},
             text='Accrued')  # Adding text on each bar

# Format the total revenue in a cleaner way (without Naira symbol)
fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')

# Increase the figure size, change color to maroon, and bold the bar figures
fig.update_layout(
    title_font_size=18,
    xaxis_title_font_size=14,
    yaxis_title_font_size=14,
    font=dict(size=14, family='Arial, sans-serif'),
    bargap=0.15,  # Adjust gap between bars
    plot_bgcolor='white',  # Background color of the plot
    bargroupgap=0.1,  # Adjust the gap between bars in the same group
    coloraxis_showscale=False,  # Hide the color scale
)

# Change the color to maroon for the bars
fig.update_traces(marker_color='maroon')

# Show the bar chart
st.plotly_chart(fig)

# Add Download CSV button for filtered data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# Convert filtered data to CSV
csv = convert_df_to_csv(pending_df_po)

# Display download button
st.download_button(label="Download Filtered Data as CSV", data=csv, file_name='filtered_data.csv', mime='text/csv')







# Title for the Receivables Tracker section
st.markdown('<h1 style="font-size: 30px;">Receivables Tracker</h1>', unsafe_allow_html=True)

# Create a new branch dataframe for the Receivables Tracker
received_df = filtered_df.copy()

# Create the layout for the date filter and metric
col1, col2 = st.columns([2, 1])

with col1:
    # Date Filter: Between Date 1 and Date 2
    date_filter = st.date_input(
        "Select Date Range (sav_date)",
        [],
        key='date_filter_ui'
    )

# Filter the dataframe based on the selected date range
if date_filter and len(date_filter) == 2:
    start_date, end_date = date_filter
    received_df = received_df[
        (received_df['sav_date'] >= pd.Timestamp(start_date)) & 
        (received_df['sav_date'] <= pd.Timestamp(end_date))
    ]

# Aggregate the revenue by regional supervisor
aggregated_received_data = received_df.groupby('rs_proposed')['revenue'].sum().reset_index(name='Total Revenue')

# Display the aggregated revenue metric
total_received_revenue = aggregated_received_data['Total Revenue'].sum()
st.metric(label="Accrued (₦)", value=f"{total_received_revenue:,.2f}")

# Create a bar chart using Plotly with amount displayed on each bar
fig_received = px.bar(
    aggregated_received_data,
    x='rs_proposed',
    y='Total Revenue',
    title='Received Within Filtered Period',
    labels={'Total Revenue': 'Accrued'},
    text='Total Revenue',
    color_discrete_sequence=['#228B22']  # Green bars
)

# Format the total revenue in a cleaner way
fig_received.update_traces(
    texttemplate='%{text:.2s}', 
    textposition='outside'
)

# Adjust the layout for the bar chart
fig_received.update_layout(
    title_font_size=16,
    xaxis_title_font_size=14,
    yaxis_title_font_size=14,
    font=dict(size=14, family='Arial, sans-serif'),
    bargap=0.15,  # Adjust gap between bars
    plot_bgcolor='white'  # Background color of the plot
)

# Show the bar chart
st.plotly_chart(fig_received)


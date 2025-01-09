import requests  # Import the requests library
from io import BytesIO  # Import BytesIO for handling in-memory files
import pandas as pd  # Import pandas for data handling
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Cache Data Load Function
@st.cache_data(max_entries=5)  # Keeps the cache to 5 entries
def load_data(shared_link: str):
    response = requests.get(shared_link)
    if response.status_code == 200:
        try:
            excel_file = BytesIO(response.content)

            # Load specific sheets
            ihs_nr_data = pd.read_excel(excel_file, sheet_name="ihs nr data", engine="openpyxl")
            ihs_matrix = pd.read_excel(excel_file, sheet_name="ihsmatrix", engine="openpyxl")

            # Merge tables on 'ihs_id'
            merged_data = pd.merge(ihs_nr_data, ihs_matrix, on="ihs_id", how="inner")

            # Specify the list of desired columns
            columns_to_select = [
                "request_date", "alt_id", "ihs_id", "Regional Manager", 
                "Zonal Coordinator", "region", "job_type", "requirement", "qty", "unit", 
                "total", "approval", "approval_date", "job_status", "closure_date", 
                "execution", "payment_ref", "executor", "qty_used", "unit_used", 
                "expense", "profit", "reference"
            ]

            # Filter the dataframe to keep only the specified columns
            filtered_data = merged_data[columns_to_select]

            return filtered_data  # Return the filtered dataframe
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

st.title('💼 Non Routine')

# Configuration Filters
with st.expander('**Filters**', icon='⚙️'):
    id_filter, ihs_filter, req_filter, job_status_filter, reference_filter, region_filter, date_filter = st.columns(7, gap='medium')

    # Alt ID Search box (using text_input for dynamic filtering)
    with id_filter:
        search_text = st.text_input('Search alt_id', '').strip()
        if search_text:
            filtered_df = df[df['alt_id'].str.contains(search_text, case=False, na=False)]
        else:
            filtered_df = df  # Show full table when no filter is applied

    # IHS ID Filter
    with ihs_filter:
        ihs_options = filtered_df['ihs_id'].unique()
        selected_ihs_id = st.selectbox('Select IHS ID', [''] + list(ihs_options))

    # Requirement Filter
    with req_filter:
        req_options = filtered_df['requirement'].unique()
        selected_req = st.selectbox('Select Requirement', [''] + list(req_options))

    # Job Status Filter
    with job_status_filter:
        status_options = filtered_df['job_status'].unique()
        selected_status = st.selectbox('Select Job Status', [''] + list(status_options))

    # Reference Filter
    with reference_filter:
        ref_options = filtered_df['reference'].unique()
        selected_ref = st.selectbox('Select Reference', [''] + list(ref_options))

    # Region Filter
    with region_filter:
        region_options = filtered_df['region'].unique()
        selected_region = st.selectbox('Select Region', [''] + list(region_options))

    # Date Filter
    with date_filter:
        min_date = filtered_df['request_date'].min().date()
        max_date = filtered_df['request_date'].max().date()

        # Date inputs for start and end date
        selected_start_date = st.date_input(
            'Start Date', min_value=min_date, max_value=max_date, value=min_date
        )
        selected_end_date = st.date_input(
            'End Date', min_value=min_date, max_value=max_date, value=max_date
        )

    # Clear Filters Button
    if st.button("Clear Filters"):
        search_text = ""
        selected_ihs_id = ''
        selected_req = ''
        selected_status = ''
        selected_ref = ''
        selected_region = ''
        selected_start_date = min_date
        selected_end_date = max_date
        st.rerun()  # Reload the app to reset all filters
    
    # Reload Data Button
    if st.button('Reload new data'):
        st.cache_data.clear()  # Clears the cache


# Apply Filters to DataFrame
if selected_ihs_id:
    filtered_df = filtered_df[filtered_df['ihs_id'] == selected_ihs_id]
if selected_req:
    filtered_df = filtered_df[filtered_df['requirement'] == selected_req]
if selected_status:
    filtered_df = filtered_df[filtered_df['job_status'] == selected_status]
if selected_ref:
    filtered_df = filtered_df[filtered_df['reference'] == selected_ref]
if selected_region:
    filtered_df = filtered_df[filtered_df['region'] == selected_region]

# Apply Date Range Filter
filtered_df = filtered_df[
    (filtered_df['request_date'].dt.date >= selected_start_date) & 
    (filtered_df['request_date'].dt.date <= selected_end_date)
]


# Metrics Display
row_metrics = st.columns(2)
Job_Count = len(filtered_df)

target_profit_perc = 35.0
Profit = filtered_df['profit'].mean()
Profit_perc = Profit * 100
delta_profit = Profit_perc - target_profit_perc

with row_metrics[0]:
    with st.container(border=True):
        st.metric('Job Count', Job_Count)
with row_metrics[1]:
    with st.container(border=True):
        st.metric('Profit', f"{Profit_perc:.2f}%", delta=f"{delta_profit:.2f}%")


# Display Dataframe
if filtered_df is not None:
    st.dataframe(filtered_df, hide_index=True)
else:
    st.write("No data to display.")


# Charts Display
charts = st.columns(2)

# Aggregate Data for Charts
count_by_month = filtered_df.groupby('request_date').agg(Count=('alt_id', 'count')).reset_index()
count_by_region = filtered_df.groupby('region').agg(Count=('alt_id', 'count')).reset_index()
count_by_job_type = filtered_df.groupby('job_type').agg(Count=('alt_id', 'count')).reset_index()

# Total and Closed Jobs (for the gauge chart)
total_jobs = len(filtered_df)
closed_jobs = len(filtered_df[filtered_df['job_status'] == 'Closed'])

# Chart 1: Amount of Items by Month (Line Chart - Big)
fig_amount_by_month = px.line(
    count_by_month,
    x='request_date',
    y='Count',
    title="Jobs by Month",
    labels={'request_date': 'Month', 'Count': 'Item Count'}
)

# Chart 2: Amount of Items by Region (Bar Chart - Medium)
fig_amount_by_region = px.bar(
    count_by_region,
    x='region',
    y='Count',
    title="Jobs by Region",
    labels={'Region': 'Region', 'Count': 'Item Count'}
)

# Chart 3: Amount of Items by Job Type (Column Chart - Medium)
fig_amount_by_job_type = px.bar(
    count_by_job_type,
    x='job_type',
    y='Count',
    title="Job Type Distribution",
    labels={'job_type': 'Job Type', 'Count': 'Item Count'}
)

# Chart 4: Closed Jobs from Total Jobs (Gauge Chart - Medium)
fig_closed_jobs = go.Figure(go.Indicator(
    mode="gauge+number",
    value=closed_jobs,
    title={'text': "Closed Jobs from Total Jobs"},
    gauge={
        'axis': {'range': [0, total_jobs]},
        'steps': [
            {'range': [0, closed_jobs], 'color': 'green'},
            {'range': [closed_jobs, total_jobs], 'color': 'maroon'}
        ]
    }
))

# Layout for the charts
charts_1_2 = st.columns(2)  # For Chart 1 and 2
charts_3_4 = st.columns(2)  # For Chart 3 and 4

# Chart 1: Amount of Items by Month (Big)
with charts_1_2[0]:
    st.plotly_chart(fig_amount_by_month, use_container_width=True)

# Chart 2: Amount of Items by Region (Medium)
with charts_1_2[1]:
    st.plotly_chart(fig_amount_by_region, use_container_width=True)

# Chart 3: Amount of Items by Job Type (Medium)
with charts_3_4[0]:
    st.plotly_chart(fig_amount_by_job_type, use_container_width=True)

# Chart 4: Closed Jobs from Total Jobs (Gauge Chart - Medium)
with charts_3_4[1]:
    st.plotly_chart(fig_closed_jobs, use_container_width=True)
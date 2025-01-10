
import streamlit as st
import pandas as pd
import requests
from io import BytesIO
import plotly.express as px
import plotly.graph_objects as go
from hashlib import sha256

# Authentication Setup
def authenticate_user():
    # Username and Password inputs
    st.session_state.username = st.text_input("Username", value="", type="default")
    st.session_state.password = st.text_input("Password", value="", type="password")

    # Login Button
    if st.button("Login"):
        if st.session_state.username and st.session_state.password:
            # Simple password hash check for demonstration
            hash_password = sha256(st.session_state.password.encode()).hexdigest()
            # Replace with actual user authentication logic
            if st.session_state.username == "admin" and hash_password == sha256("Olivia20$".encode()).hexdigest():
                st.session_state.authenticated = True
            else:
                st.session_state.authenticated = False
                st.error("Invalid username or password")
        else:
            st.error("Please enter both username and password.")

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# If not authenticated, show the login form
if not st.session_state.authenticated:
    st.title("Login to View Data")
    authenticate_user()
    st.stop()  # Stop execution if the user is not authenticated

# If authenticated, continue with the rest of the app
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

            # Ensure 'revenue_month' is datetime and handle invalid dates
            merged_data['revenue_month'] = pd.to_datetime(merged_data['revenue_month'], errors='coerce')

            # Specify the list of desired columns
            columns_to_select = [
                "request_date", "alt_id", "ihs_id", "Regional Manager", 
                "Zonal Coordinator", "region", "job_type", "requirement", "qty", "unit", 
                "total", "approval", "approval_date", "job_status", "closure_date", 
                "execution", "payment_ref", "executor", "qty_used", "unit_used", 
                "expense", "profit", "revenue_month", "reference"
            ]
            
            # Filter the dataframe to keep only the specified columns
            filtered_data = merged_data[columns_to_select]

            # Convert 'request_date' to datetime
            filtered_data['request_date'] = pd.to_datetime(filtered_data['request_date'], errors='coerce')

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

st.title('💼 Non Routine - IHS')

with st.expander('**Filters**', icon='⚙️'):
    id_filter, ihs_filter, req_filter, job_status_filter, reference_filter, region_filter, date_filter, revenue_month_filter = st.columns(8, gap='medium')

    # Alt ID Search box (using text_input for dynamic filtering)
    with id_filter:
        search_text = st.text_input('Search alt_id', '').strip()
        filtered_df = df[df['alt_id'].str.contains(search_text, case=False, na=False)] if search_text else df

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
        if not filtered_df['request_date'].isna().all():
            min_date = filtered_df['request_date'].min().date()
            max_date = filtered_df['request_date'].max().date()

            # Date inputs for start and end date
            selected_start_date = st.date_input('Start Date', min_value=min_date, max_value=max_date, value=min_date)
            selected_end_date = st.date_input('End Date', min_value=min_date, max_value=max_date, value=max_date)
        else:
            selected_start_date, selected_end_date = None, None

    # Revenue Month Filter
    with revenue_month_filter:
        if 'revenue_month' in filtered_df and filtered_df['revenue_month'].notna().any():
            # Convert `revenue_month` to Period (e.g., 'YYYY-MM') for chronological sorting
            filtered_df['revenue_month_period'] = filtered_df['revenue_month'].dt.to_period('M')
            
            # Sort options chronologically and convert to string for display
            revenue_month_options = (
                sorted(filtered_df['revenue_month_period'].unique())  # Sort Periods chronologically
            )
            revenue_month_options_str = [str(option) for option in revenue_month_options]  # Convert to strings
            
            # Create the selectbox with sorted options
            selected_revenue_month = st.selectbox('Select Revenue Month', [''] + revenue_month_options_str)
        else:
            selected_revenue_month = ''

    # Clear Filters Button
    if st.button("Clear Filters"):
        search_text, selected_ihs_id, selected_req = '', '', ''
        selected_status, selected_ref, selected_region = '', '', ''
        selected_start_date, selected_end_date, selected_revenue_month = None, None, ''
        st.rerun()

    # Reload Data Button
    if st.button('Reload new data'):
        st.cache_data.clear()

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
if selected_start_date and selected_end_date:
    filtered_df = filtered_df[
        (filtered_df['request_date'].dt.date >= selected_start_date) & 
        (filtered_df['request_date'].dt.date <= selected_end_date)
    ]

# Apply Revenue Month Filter
if selected_revenue_month:
    filtered_df = filtered_df[filtered_df['revenue_month'].dt.to_period('M').astype(str) == selected_revenue_month]












# Metrics Display
row_metrics = st.columns(2)
Job_Count = len(filtered_df)

target_profit_perc = 35.0
total_revenue = filtered_df['total'].sum()  # Sum of revenue (total)
total_expense = filtered_df['expense'].sum()  # Sum of expenses (cost)
total_profit = total_revenue - total_expense
Profit_perc = (total_profit / total_revenue) * 100
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









# Keep a copy of the original dataframe for the last four charts
df_for_last_charts = filtered_df.copy()

# Filter out NaT values from revenue_month for proper date representation for the first two charts only
filtered_df = filtered_df[filtered_df['revenue_month'].notna()]

# Aggregate Total Revenue for the first two charts
revenue_by_month = filtered_df.groupby('revenue_month').agg(Total_Revenue=('total', 'sum')).reset_index()

# Profit Percentage Calculation
revenue_by_month['Profit_Percentage'] = (revenue_by_month['Total_Revenue'] - 
                                          filtered_df.groupby('revenue_month')['expense'].sum().values) / revenue_by_month['Total_Revenue'] * 100



fig_total_revenue = go.Figure(go.Bar(
    x=revenue_by_month['revenue_month'],
    y=revenue_by_month['Total_Revenue'],
    name='Total Revenue',
    marker_color='royalblue'  
))
# Update Layout for Total Revenue Bar Chart
fig_total_revenue.update_layout(
    title="Total Revenue by Month",
    xaxis_title="Month",
    yaxis_title="Total Revenue (in millions)",
    template="plotly_dark"
)

# Display the Total Revenue Bar Chart
with st.container():
    st.plotly_chart(fig_total_revenue, use_container_width=True)




fig_profit_percentage = go.Figure(go.Scatter(
    x=revenue_by_month['revenue_month'],
    y=revenue_by_month['Profit_Percentage'],
    name='Profit Percentage',
    mode='lines+markers',
    marker_color='maroon'
))

# Add Target Line at 35% Profit Percentage
fig_profit_percentage.add_shape(
    type="line",
    x0=revenue_by_month['revenue_month'].min(),  # Start of the line (minimum revenue_month)
    x1=revenue_by_month['revenue_month'].max(),  # End of the line (maximum revenue_month)
    y0=35,  # Y-value for the target (35%)
    y1=35,  # Y-value for the target (35%)
    line=dict(
        color="royalblue",  # Line color
        width=2,  # Line width
        dash="dash",  # Dashed line
    ),
)

# Update Layout for Profit Percentage Line Chart
fig_profit_percentage.update_layout(
    title="Profit Percentage by Month",
    xaxis_title="Month",
    yaxis_title="Profit Percentage",
    template="plotly_dark"
)

# Display the Profit Percentage Line Chart
with st.container():
    st.plotly_chart(fig_profit_percentage, use_container_width=True)
    

# Now, for the last four charts, use the original `df_for_last_charts` to avoid any unintended filtering

# Aggregate Data for the other Charts (Job Distribution by Month, Region, Job Type, Closed Jobs)
count_by_month = df_for_last_charts.groupby('request_date').agg(Count=('alt_id', 'count')).reset_index()
count_by_region = df_for_last_charts.groupby('region').agg(Count=('alt_id', 'count')).reset_index()
count_by_job_type = df_for_last_charts.groupby('job_type').agg(Count=('alt_id', 'count')).reset_index()

# Total and Closed Jobs (for the gauge chart)
total_jobs = len(df_for_last_charts)
closed_jobs = len(df_for_last_charts[df_for_last_charts['job_status'] == 'Closed'])

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

# Layout for the other charts
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

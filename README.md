
# Non Routine Data Analysis Application

This Streamlit-based application is designed to analyze and visualize non-routine job data. It allows users to interactively filter and explore job-related metrics, with a focus on job counts, profit percentages, and job distributions across various categories such as regions and job types.

## Features
- **Data Filters**: Apply various filters such as:
    - Alt ID
    - IHS ID
    - Requirement
    - Job Status
    - Reference
    - Region
    - Date Range
- **Metrics Display**: Displays key metrics such as:
    - Job Count
    - Profit Percentage (with a comparison to a target value)
- **Interactive Charts**: Displays visualizations to help explore the data:
    - Jobs by Month (Line chart)
    - Jobs by Region (Bar chart)
    - Job Type Distribution (Bar chart)
- **Cache Data**: Efficient caching mechanism to reduce loading times for frequently accessed data.
- **Clear & Reload Buttons**: Options to clear filters and reload new data.

## Requirements
- **Python 3.x**
- **Streamlit**
- **Plotly**
- **Pandas**
- **Requests**

### Installing Dependencies
You can install the required dependencies using pip:

```bash
pip install streamlit plotly pandas requests openpyxl
```

## Usage
1. **Upload Excel File**: Provide the URL of the shared Excel file containing the data.
2. **Apply Filters**: Use the filters to narrow down the data based on your requirements.
3. **View Metrics & Charts**: The application will display relevant job metrics and interactive charts based on the filtered data.

## How to Run the Application
To run the application locally, execute the following command in your terminal:

```bash
streamlit run app.py
```

## License
This project is open-source and available under the MIT License.


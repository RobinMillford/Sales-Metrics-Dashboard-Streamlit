import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import plotly.express as px
import duckdb
import time

# Set page configuration
st.set_page_config(page_title="Sales Metrics Dashboard", page_icon="🛒", layout="wide")

# Load Data
@st.cache_data
def load_data(file_path):
    return pd.read_csv(file_path)

accounts = load_data('accounts.csv')
orders = load_data('orders.csv')
region = load_data('region.csv')
sales_reps = load_data('sales_reps.csv')
web_events = load_data('web_events.csv')

# Spinner for loading
with st.spinner('Loading Dashboard...'):
    time.sleep(1)

# Inject Google Font
st.markdown(
    """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Sriracha&display=swap" rel="stylesheet">
    """,
    unsafe_allow_html=True
)

# Custom Title with Styled Font
st.markdown(
    """
    <div style="text-align: left;">
        <h1 style="
            font-size: 5em; 
            font-family: 'Sriracha', serif; 
            font-weight: 600;
            color: rgb(64, 231, 35); 
            margin-bottom: 0;">
            Strategic Sales Performance Overview 📉
        </h1>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    ### Key Insights from the Analysis 🔍

    - **Regional Performance:** Our analysis shows distinct variations in customer behavior and order trends across different regions, enabling targeted strategies for each region. 🌍
    - **Customer Segmentation:** Identified customer groups based on order frequency and spending, such as **High Volume** and **High Spend** segments, which can inform tailored marketing campaigns. 🛍️
    - **Yearly Trends:** Notable trends in total sales between **2013 and 2017**, including seasonal variations, provide a clear understanding of demand cycles. 📅
    - **Order Patterns:** Insights into average order size and standard deviation across customer segments help identify consistency in spending habits. 📊
    - **High Performers:** Highlighted top accounts and sales representatives contributing to maximum revenue, enabling recognition and strategic focus. 🏆
    
    #### How These Insights Help in Business:
    - **Enhanced Decision-Making:** The detailed segmentation and trends allow for informed decisions on resource allocation and strategy. 🧠
    - **Targeted Marketing:** Insights into customer behaviors and spending habits support personalized offers and campaigns, boosting engagement. 🎯
    - **Revenue Optimization:** Understanding regional and yearly trends enables better forecasting and revenue growth strategies. 💸
    - **Operational Efficiency:** Identifying patterns in order sizes and lead times ensures more efficient operations. 🚚
    - **Customer Satisfaction:** Tailoring services to high-value customers improves satisfaction and retention. 😊
    """,
    unsafe_allow_html=True
)

# Sidebar region selection
region_choice = st.sidebar.selectbox(
    'Select Region',
    options=['All Regions'] + region['name'].unique().tolist()  # Adding 'All Regions' as an option
)

# Create three columns
col1, col2, col3 = st.columns(3)

with col1:
    #plot1
    # Define query based on region selection
    if region_choice == "All Regions":
        query = """
        SELECT r.name AS region_name,
               SUM(o.total_amt_usd) AS total_sales
        FROM orders o
        JOIN accounts a ON o.account_id = a.id
        JOIN sales_reps sr ON a.sales_rep_id = sr.id
        JOIN region r ON sr.region_id = r.id
        GROUP BY r.name
        ORDER BY total_sales DESC;
        """
    else:
        query = f"""
        SELECT r.name AS region_name,
               SUM(o.total_amt_usd) AS total_sales
        FROM orders o
        JOIN accounts a ON o.account_id = a.id
        JOIN sales_reps sr ON a.sales_rep_id = sr.id
        JOIN region r ON sr.region_id = r.id
        WHERE r.name = '{region_choice}'
        GROUP BY r.name
        ORDER BY total_sales DESC;
        """

    # Fetch the data for the selected region or all regions
    region_sales_data = duckdb.query(query).df()

    # Total sales for the selected region or sum for all regions
    if region_choice == "All Regions":
        total_sales = region_sales_data["total_sales"].sum().round()  # Sum all regions for "All Regions"
    else:
        total_sales = region_sales_data["total_sales"].iloc[0].round()  # Get sales for the selected region

    # Create an indicator chart
    fig = go.Figure()

    fig.add_trace(go.Indicator(
        mode="number",
        value=total_sales,
        title={"text": f"Total Sales Amount - {region_choice}"},
        number={'prefix': "$", 'valueformat': ".f"},
        domain={'x': [0, 1], 'y': [0, 1]}  # Full-width domain
    ))

    # Update layout for transparency and styling
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
        font=dict(size=24, color="darkgreen")  # Styling for the text
    )

    # Display the chart in the app
    st.plotly_chart(fig)

    # plot2 - Accounts by Sales Rep
    if region_choice == 'All Regions':
        query = """
        SELECT r.name AS Region,
               sr.name AS Rep_name,
               a.name AS account_name
        FROM region r
        JOIN sales_reps sr ON r.id = sr.region_id
        JOIN accounts a ON sr.id = a.sales_rep_id
        ORDER BY account_name ASC;
        """
    else:
        query = f"""
        SELECT r.name AS Region,
               sr.name AS Rep_name,
               a.name AS account_name
        FROM region r
        JOIN sales_reps sr ON r.id = sr.region_id
        JOIN accounts a ON sr.id = a.sales_rep_id
        WHERE r.name = '{region_choice}'
        ORDER BY account_name ASC;
        """
    
    # Get region data without caching to ensure fresh data on region change
    region_data = duckdb.query(query).df()

    # Prepare data for visualization
    grouped_data = region_data.groupby('Rep_name').size().reset_index(name='Account_Count')

    # Create the bar chart
    fig = px.bar(
        grouped_data,
        x='Rep_name',
        y='Account_Count',
        title=f"{region_choice}: Accounts by Sales Rep",
        labels={'Rep_name': 'Sales Representative', 'Account_Count': 'Number of Accounts'},
        text='Account_Count',
        color='Account_Count',
        color_continuous_scale='Blues'
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(
        xaxis_title="Sales Representative",
        yaxis_title="Number of Accounts",
        font=dict(size=14),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    # Display the chart
    st.plotly_chart(fig)

    #Plot3
    # Query for Web Event Occurrences by Sales Representative and Channel
    if region_choice == 'All Regions':
        query = """
        SELECT sr.name AS sales_rep_name,
               we.channel,
               COUNT(*) AS number_of_occurrences
        FROM web_events we
        JOIN accounts a ON we.account_id = a.id
        JOIN sales_reps sr ON a.sales_rep_id = sr.id
        GROUP BY sr.name, we.channel
        ORDER BY number_of_occurrences DESC;
        """
    else:
        query = f"""
        SELECT sr.name AS sales_rep_name,
               we.channel,
               COUNT(*) AS number_of_occurrences
        FROM web_events we
        JOIN accounts a ON we.account_id = a.id
        JOIN sales_reps sr ON a.sales_rep_id = sr.id
        JOIN region r ON sr.region_id = r.id
        WHERE r.name = '{region_choice}'
        GROUP BY sr.name, we.channel
        ORDER BY number_of_occurrences DESC;
        """

    # Get the data for the selected region
    web_event_data = duckdb.query(query).df()

    # Pivot the data for a stacked bar chart
    pivot_data = web_event_data.pivot(index='sales_rep_name', columns='channel', values='number_of_occurrences').fillna(0)

    # Create the stacked bar chart
    fig = go.Figure()
    for channel in pivot_data.columns:
        fig.add_trace(go.Bar(
            x=pivot_data.index,
            y=pivot_data[channel],
            name=channel
        ))

    # Update the layout for better visualization
    fig.update_layout(
        title=f"{region_choice}: Web Event Occurrences by Sales Representative and Channel",
        xaxis_title="Sales Representative",
        yaxis_title="Number of Occurrences",
        barmode='stack',  # Stacked bar mode
        font=dict(size=14),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_tickangle=-45,  # Rotate x-axis labels for better readability
        legend_title_text='Channel'
    )

    # Display the chart in the app
    st.plotly_chart(fig)

    #plot4
    # Define query based on region selection
    if region_choice == "All Regions":
        query = """
        SELECT sr.name AS sales_representative,
               COUNT(DISTINCT a.id) AS new_customers_acquired,
               EXTRACT(YEAR FROM CAST(MIN(o.occurred_at) AS TIMESTAMP)) AS first_order_year
        FROM sales_reps sr
        LEFT JOIN accounts a ON sr.id = a.sales_rep_id
        LEFT JOIN orders o ON a.id = o.account_id
        GROUP BY sr.name
        ORDER BY new_customers_acquired DESC;
        """
    else:
        query = f"""
        SELECT sr.name AS sales_representative,
               COUNT(DISTINCT a.id) AS new_customers_acquired,
               EXTRACT(YEAR FROM CAST(MIN(o.occurred_at) AS TIMESTAMP)) AS first_order_year
        FROM sales_reps sr
        LEFT JOIN accounts a ON sr.id = a.sales_rep_id
        LEFT JOIN orders o ON a.id = o.account_id
        LEFT JOIN region r ON sr.region_id = r.id
        WHERE r.name = '{region_choice}'
        GROUP BY sr.name
        ORDER BY new_customers_acquired DESC;
        """
    
    # Fetch the data
    acquisition_data = duckdb.query(query).df()

    # Create a scatter plot with better hover readability
    fig = go.Figure()

    # Add traces for overlapping data (each sales rep's data points)
    for i, rep in enumerate(acquisition_data['sales_representative'].unique()):
        rep_data = acquisition_data[acquisition_data['sales_representative'] == rep]
        
        fig.add_trace(go.Scatter(
            x=rep_data['first_order_year'],
            y=rep_data['new_customers_acquired'],
            mode='markers',
            name=rep,
            marker=dict(
                size=12,
                color=f'rgba({(i * 50) % 255}, {(i * 80) % 255}, {(i * 100) % 255}, 0.8)',  # Unique color per rep
                line=dict(width=1.5, color='black')
            ),
            hovertemplate=(
                f"<b>Sales Rep:</b> {rep}<br>"
                "<b>Year of First Order:</b> %{x}<br>"
                "<b>New Customers Acquired:</b> %{y}<extra></extra>"
            )
        ))

    # Update the layout for better visualization
    fig.update_layout(
        title=f"Customer Acquisition Analysis by Sales Rep ({region_choice})",
        xaxis_title="Year of First Order",
        yaxis_title="New Customers Acquired",
        font=dict(size=14),
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
        plot_bgcolor='rgba(0,0,0,0)',  # Transparent plot area
        xaxis=dict(tickmode='linear', dtick=1),  # Ensure each year is shown on the x-axis
        showlegend=True  # Show legend for sales representatives
    )

    # Display the chart in the app
    st.plotly_chart(fig)

    #plot5
    # Query to fetch data based on region choice
    query = f"""
    SELECT
        r.name AS region_name,
        AVG(o.total_amt_usd) AS avg_order_size
    FROM orders o
    JOIN accounts a ON o.account_id = a.id
    JOIN sales_reps sr ON a.sales_rep_id = sr.id
    JOIN region r ON sr.region_id = r.id
    WHERE r.name = '{region_choice}' OR '{region_choice}' = 'All Regions'
    GROUP BY r.name
    ORDER BY avg_order_size DESC;
    """

    # Fetch data from DuckDB
    avg_order_data = duckdb.query(query).df()

    # Create a horizontal bar chart for average order size
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=avg_order_data['avg_order_size'],
        y=avg_order_data['region_name'],
        orientation='h',  # Horizontal bars
        marker=dict(
            color=avg_order_data['avg_order_size'],  # Gradient color based on values
            colorscale='blues',  # Blue gradient for bars
            showscale=True,  # Show color scale
            colorbar=dict(
                title='Avg Order Size (USD)',
                titlefont=dict(size=14, color='white'),
                tickfont=dict(size=12, color='white')
            )
        ),
        text=avg_order_data['avg_order_size'].apply(lambda x: f"${x:,.2f}"),  # Add text labels
        textposition='inside',  # Inside the bars
        insidetextanchor='middle'
    ))

    # Update layout for better visualization
    fig.update_layout(
        title=dict(
            text="Average Order Size Comparison Across Regions",
            font=dict(size=18, color='white')
        ),
        xaxis=dict(
            title="Average Order Size (USD)",
            titlefont=dict(size=14, color='white'),
            tickfont=dict(size=12, color='white'),
            gridcolor='rgba(255, 255, 255, 0.1)'
        ),
        yaxis=dict(
            title="Region",
            titlefont=dict(size=14, color='white'),
            tickfont=dict(size=12, color='white'),
            automargin=True
        ),
        font=dict(size=14, color='white'),
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
        plot_bgcolor='rgba(0,0,0,0)',  # Transparent plot area
        bargap=0.2  # Adjust spacing between bars
    )

    # Display the chart in col1
    st.plotly_chart(fig)

# Define the query to fetch the data based on region selection
query = f"""
WITH order_summary AS (
    SELECT
        a.id AS account_id,
        a.name AS account_name,
        AVG(o.total_amt_usd) AS avg_order_amt_usd,
        STDDEV(o.total_amt_usd) AS order_amt_std_dev,
        COUNT(o.id) AS total_orders,
        SUM(o.total_amt_usd) AS total_sales
    FROM accounts a
    LEFT JOIN orders o ON a.id = o.account_id
    LEFT JOIN sales_reps sr ON a.sales_rep_id = sr.id
    LEFT JOIN region r ON sr.region_id = r.id
    WHERE r.name = '{region_choice}' OR '{region_choice}' = 'All Regions'
    GROUP BY a.id, a.name
),
segmented_orders AS (
    SELECT
        account_id,
        account_name,
        avg_order_amt_usd,
        order_amt_std_dev,
        total_orders,
        total_sales,
        CASE
            WHEN total_orders > 50 THEN 'High Volume'
            WHEN total_orders > 10 THEN 'Moderate Volume'
            ELSE 'Low Volume'
        END AS order_volume_segment,
        CASE
            WHEN avg_order_amt_usd > 1000 THEN 'High Value'
            ELSE 'Low Value'
        END AS order_value_segment
    FROM order_summary
)
SELECT
    order_volume_segment,
    order_value_segment,
    COUNT(account_id) AS num_accounts,
    AVG(avg_order_amt_usd) AS avg_order_size_usd,
    AVG(order_amt_std_dev) AS avg_order_std_dev_usd,
    SUM(total_sales) AS total_sales_in_segment
FROM segmented_orders
GROUP BY order_volume_segment, order_value_segment
ORDER BY num_accounts DESC;
"""

# Fetch data from DuckDB
avg_order_size_data = duckdb.query(query).df()

# Create a bar chart for Average Order Size by Customer Segment
fig = go.Figure()

# Add bar trace for Average Order Size
fig.add_trace(go.Bar(
    x=avg_order_size_data['order_volume_segment'] + " - " + avg_order_size_data['order_value_segment'],  # Combining both segments
    y=avg_order_size_data['avg_order_size_usd'],
    name='Avg Order Size (USD)',
    marker=dict(color='rgb(53, 151, 255)'),
))

# Add bar trace for Number of Accounts
fig.add_trace(go.Bar(
    x=avg_order_size_data['order_volume_segment'] + " - " + avg_order_size_data['order_value_segment'],  # Combining both segments
    y=avg_order_size_data['num_accounts'],
    name='Number of Accounts',
    marker=dict(color='rgb(255, 130, 50)'),
))

# Add bar trace for Total Sales in Each Segment
fig.add_trace(go.Bar(
    x=avg_order_size_data['order_volume_segment'] + " - " + avg_order_size_data['order_value_segment'],  # Combining both segments
    y=avg_order_size_data['total_sales_in_segment'],
    name='Total Sales (USD)',
    marker=dict(color='rgb(255, 99, 132)'),
))

# Add bar trace for Standard Deviation of Order Size
fig.add_trace(go.Bar(
    x=avg_order_size_data['order_volume_segment'] + " - " + avg_order_size_data['order_value_segment'],  # Combining both segments
    y=avg_order_size_data['avg_order_std_dev_usd'],
    name='Order Std. Dev. (USD)',
    marker=dict(color='rgb(75, 192, 192)'),
))

# Update layout for the chart
fig.update_layout(
    barmode='group',
    title=f"Analysis of Order Size, Number of Accounts, and Total Sales by Segment ({region_choice})",
    xaxis_title="Customer Segment",
    yaxis_title="Values (USD / Accounts)",
    legend_title="Metrics",
    font=dict(size=14),
    paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
    plot_bgcolor='rgba(0,0,0,0)',  # Transparent plot area
)

# Display the plot in col1
with col1:
    st.plotly_chart(fig)

with col2:
    # plot1 - Unit Price for Orders
    if region_choice == 'All Regions':
        query = """
        SELECT r.name AS region,
               a.name AS account_name,
               o.total_amt_usd / (o.total + 0.01) AS unit_price
        FROM region r
        JOIN sales_reps sr ON r.id = sr.region_id
        JOIN accounts a ON sr.id = a.sales_rep_id
        JOIN orders o ON a.id = o.account_id
        WHERE o.standard_qty > 100
          AND o.poster_qty > 50
        ORDER BY unit_price DESC;
        """
    else:
        query = f"""
        SELECT r.name AS region,
               a.name AS account_name,
               o.total_amt_usd / (o.total + 0.01) AS unit_price
        FROM region r
        JOIN sales_reps sr ON r.id = sr.region_id
        JOIN accounts a ON sr.id = a.sales_rep_id
        JOIN orders o ON a.id = o.account_id
        WHERE o.standard_qty > 100
          AND o.poster_qty > 50
          AND r.name = '{region_choice}'
        ORDER BY unit_price DESC;
        """
    
    # Get the data for the selected region
    region_data = duckdb.query(query).df()

    # Prepare the data for the plot
    region_data_sorted = region_data[['account_name', 'unit_price']]

    # Create the bar chart for Unit Price by Account
    fig = px.bar(
        region_data_sorted,
        x='account_name',
        y='unit_price',
        title=f"{region_choice}: Unit Price for Orders with Quantity Conditions",
        labels={'account_name': 'Account Name', 'unit_price': 'Unit Price (USD)'},
        color='unit_price',
        color_continuous_scale='Viridis'
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(
        xaxis_title="Account Name",
        yaxis_title="Unit Price (USD)",
        font=dict(size=14),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_tickangle=-45  # Rotate x-axis labels for better readability
    )

    # Display the chart in the app
    st.plotly_chart(fig)

    #plot2
    # Add regional filtering to the query
    if region_choice == "All Regions":
        query = """
        SELECT CAST(EXTRACT(YEAR FROM CAST(occurred_at AS TIMESTAMP)) AS INT) AS year,
               SUM(total_amt_usd) AS total_usd
        FROM orders
        GROUP BY year
        ORDER BY total_usd ASC;
        """
    else:
        query = f"""
        SELECT CAST(EXTRACT(YEAR FROM CAST(occurred_at AS TIMESTAMP)) AS INT) AS year,
               SUM(o.total_amt_usd) AS total_usd
        FROM orders o
        JOIN accounts a ON o.account_id = a.id
        JOIN sales_reps sr ON a.sales_rep_id = sr.id
        JOIN region r ON sr.region_id = r.id
        WHERE r.name = '{region_choice}'
        GROUP BY year
        ORDER BY total_usd ASC;
        """

    # Fetch the data for the selected region or all regions
    yearly_order_data = duckdb.query(query).df()

    # Create an area chart for Total USD Amount by Year
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=yearly_order_data['year'],
        y=yearly_order_data['total_usd'],
        mode='lines+markers',  # Line with markers
        fill='tozeroy',  # Fill the area under the line
        line=dict(color='mediumslateblue', width=3),  # Line styling
        marker=dict(color='darkorange', size=8, symbol='diamond'),  # Marker styling
        name='Total USD'
    ))

    # Update the layout for transparency and improved readability
    fig.update_layout(
        title=f"Total USD Amount of Orders by Year ({region_choice})",
        xaxis_title="Year",
        yaxis_title="Total USD Amount (in millions)",
        font=dict(size=14),
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
        plot_bgcolor='rgba(0,0,0,0)',  # Transparent plot area
        xaxis_tickangle=-45,  # Rotate x-axis labels for better readability
        showlegend=True
    )

    # Add annotations to highlight the highest and lowest values
    min_value = yearly_order_data.loc[yearly_order_data['total_usd'].idxmin()]
    max_value = yearly_order_data.loc[yearly_order_data['total_usd'].idxmax()]
    fig.add_annotation(x=min_value['year'], y=min_value['total_usd'],
                       text=f"Lowest: ${min_value['total_usd']:.2f}",
                       showarrow=True, arrowhead=2, ax=-40, ay=-40, bgcolor="blue")
    fig.add_annotation(x=max_value['year'], y=max_value['total_usd'],
                       text=f"Highest: ${max_value['total_usd']:.2f}",
                       showarrow=True, arrowhead=2, ax=40, ay=-40, bgcolor="green")

    # Display the chart in the app
    st.plotly_chart(fig)
    

    #plot3
    # Define query based on region selection
    if region_choice == "All Regions":
        query = """
        SELECT a.id AS account_id,
               a.name AS account_name,
               SUM(o.total_amt_usd) AS total_spent,
               COUNT(o.id) AS total_orders,
               AVG(o.total_amt_usd) AS average_order_amount
        FROM accounts a
        LEFT JOIN orders o ON a.id = o.account_id
        GROUP BY a.id, a.name
        ORDER BY total_spent DESC;
        """
    else:
        query = f"""
        SELECT a.id AS account_id,
               a.name AS account_name,
               SUM(o.total_amt_usd) AS total_spent,
               COUNT(o.id) AS total_orders,
               AVG(o.total_amt_usd) AS average_order_amount
        FROM accounts a
        LEFT JOIN orders o ON a.id = o.account_id
        JOIN sales_reps sr ON a.sales_rep_id = sr.id
        JOIN region r ON sr.region_id = r.id
        WHERE r.name = '{region_choice}'
        GROUP BY a.id, a.name
        ORDER BY total_spent DESC;
        """

    # Fetch the data
    clv_data = duckdb.query(query).df()

    # Replace NaN in `average_order_amount` with a default value (e.g., 1)
    clv_data['average_order_amount'] = clv_data['average_order_amount'].fillna(1)

    # Create a scatter plot
    fig = px.scatter(
        clv_data,
        x="total_orders",
        y="total_spent",
        size="average_order_amount",
        color="total_spent",
        hover_data=["account_name"],
        labels={
            "total_orders": "Total Orders",
            "total_spent": "Total Spent (USD)",
            "average_order_amount": "Avg Order Amount (USD)"
        },
        title=f"Customer Lifetime Value Analysis - {region_choice}",
        color_continuous_scale="Viridis"
    )

    # Update layout
    fig.update_layout(
        xaxis_title="Total Orders",
        yaxis_title="Total Spent (USD)",
        font=dict(size=14),
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
        plot_bgcolor='rgba(0,0,0,0)',  # Transparent plot area
        xaxis_tickangle=-45  # Rotate x-axis labels
    )

    # Display the chart in the app
    st.plotly_chart(fig)

    #plot4
    # Define query based on region selection
    query = f"""
    WITH last_order_dates AS (
        SELECT
            account_id,
            MAX(occurred_at) AS last_order_date
        FROM orders
        GROUP BY account_id
    )
    SELECT
        COUNT(DISTINCT l.account_id) AS active_customers,
        COUNT(DISTINCT a.id) - COUNT(DISTINCT l.account_id) AS churned_customers
    FROM accounts a
    LEFT JOIN last_order_dates l ON a.id = l.account_id
    LEFT JOIN sales_reps sr ON a.sales_rep_id = sr.id
    LEFT JOIN region r ON sr.region_id = r.id
    WHERE r.name = '{region_choice}' OR '{region_choice}' = 'All Regions';
    """

    # Fetch data from DuckDB
    churn_data = duckdb.query(query).df()

    # Extract data for visualization
    active_customers = churn_data['active_customers'][0]
    churned_customers = churn_data['churned_customers'][0]

    # Create the bar chart
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=[active_customers],
        y=['Active Customers'],
        orientation='h',
        name='Active Customers',
        marker=dict(color='green', line=dict(color='darkgreen', width=1.5)),
        hovertemplate="Active Customers: %{x}<extra></extra>"
    ))

    fig.add_trace(go.Bar(
        x=[churned_customers],
        y=['Churned Customers'],
        orientation='h',
        name='Churned Customers',
        marker=dict(color='red', line=dict(color='darkred', width=1.5)),
        hovertemplate="Churned Customers: %{x}<extra></extra>"
    ))

    # Update layout
    fig.update_layout(
        title=f"Customer Churn Analysis ({region_choice})",
        xaxis_title="Number of Customers",
        yaxis_title="Customer Status",
        font=dict(size=14),
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
        plot_bgcolor='rgba(0,0,0,0)',  # Transparent plot area
        barmode='stack',
        showlegend=True
    )

    # Display the chart
    st.plotly_chart(fig)

    #plot5
    # Query to fetch data based on region choice
    query = f"""
    SELECT
        r.name AS region_name,
        we.channel,
        COUNT(we.id) AS total_events,
        COUNT(DISTINCT a.id) AS unique_accounts_impacted
    FROM web_events we
    LEFT JOIN accounts a ON we.account_id = a.id
    LEFT JOIN sales_reps sr ON a.sales_rep_id = sr.id
    LEFT JOIN region r ON sr.region_id = r.id
    WHERE r.name = '{region_choice}' OR '{region_choice}' = 'All Regions'
    GROUP BY r.name, we.channel
    ORDER BY r.name, total_events DESC;
    """

    # Fetch data from DuckDB
    web_event_data = duckdb.query(query).df()

    # Create a stacked bar chart for web event effectiveness by region and channel
    fig = go.Figure()

    # Define a list of unique channels
    channels = web_event_data['channel'].unique()

    # Color palette to use for the channels
    channel_colors = {
        'direct': 'rgba(255, 99, 132, 0.6)',
        'facebook': 'rgba(54, 162, 235, 0.6)',
        'organic': 'rgba(75, 192, 192, 0.6)',
        'adwords': 'rgba(153, 102, 255, 0.6)',
        'twitter': 'rgba(255, 159, 64, 0.6)',
        'banner': 'rgba(255, 205, 86, 0.6)'
    }

    # Add bar traces for each channel, stacking them within each region
    for channel in channels:
        channel_data = web_event_data[web_event_data['channel'] == channel]
        fig.add_trace(go.Bar(
            x=channel_data['region_name'],
            y=channel_data['total_events'],
            name=f'Channel: {channel}',
            text=channel_data['unique_accounts_impacted'].apply(lambda x: f"Unique Accounts: {x}"),
            textposition='inside',
            hoverinfo='x+text+y',  # Show text (unique accounts) and value on hover
            marker=dict(
                color=channel_colors[channel],  # Use the predefined color for each channel
                line=dict(color='white', width=1),  # White outline for better visibility
            )
        ))

    # Update layout for better visualization
    fig.update_layout(
        title=f"Web Event Effectiveness by Region and Channel",
        xaxis=dict(
            title="Region",
            titlefont=dict(size=14, color='white'),
            tickfont=dict(size=12, color='white'),
            tickangle=45,  # Rotate x-axis labels for better readability
        ),
        yaxis=dict(
            title="Total Events",
            titlefont=dict(size=14, color='white'),
            tickfont=dict(size=12, color='white')
        ),
        barmode='stack',  # Stack bars to combine events of each channel per region
        font=dict(size=14, color='white'),
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
        plot_bgcolor='rgba(0,0,0,0)',  # Transparent plot area
        legend=dict(
            title="Channels",
            orientation="v",  # Vertical orientation for the legend
            x=1.05,  # Position legend to the right
            y=0.5,  # Center the legend vertically
            xanchor="left",
            yanchor="middle",
            traceorder='normal',  # Order items in the legend
            font=dict(size=12, color='white'),
            bgcolor='rgba(0,0,0,0)',  # Transparent background for the legend
            bordercolor='white',  # White border around the legend
            borderwidth=1
        ),
        showlegend=True
    )

    # Display the chart in col2
    st.plotly_chart(fig)

    #plot6
    query = f"""
WITH sales_contribution AS (
    SELECT
        r.name AS region_name,
        sr.name AS sales_representative,
        COUNT(o.id) AS num_orders,
        SUM(o.total_amt_usd) AS total_amt_usd
    FROM sales_reps sr
    JOIN accounts a ON sr.id = a.sales_rep_id
    JOIN orders o ON a.id = o.account_id
    JOIN region r ON sr.region_id = r.id
    GROUP BY r.name, sr.name
),
region_total_sales AS (
    SELECT
        region_name,
        SUM(total_amt_usd) AS region_total_amt_usd
    FROM sales_contribution
    GROUP BY region_name
)
SELECT
    sc.region_name,
    sc.sales_representative,
    sc.num_orders,
    sc.total_amt_usd,
    rt.region_total_amt_usd,
    ROUND(sc.total_amt_usd / rt.region_total_amt_usd * 100, 2) AS contribution_percent_of_region
FROM sales_contribution sc
JOIN region_total_sales rt ON sc.region_name = rt.region_name
WHERE sc.region_name = '{region_choice}' OR '{region_choice}' = 'All Regions'
ORDER BY sc.region_name, contribution_percent_of_region DESC;
"""

# Fetch data from DuckDB
    sales_contribution_data = duckdb.query(query).df()

    # Create the bar chart
    fig = px.bar(
        sales_contribution_data,
        x='sales_representative',
        y='contribution_percent_of_region',
        color='sales_representative',
        text='sales_representative',
        title=f"Sales Contribution by Sales Rep and Region ({region_choice})",
        labels={
            'sales_representative': 'Sales Representative',
            'contribution_percent_of_region': 'Contribution (%)'
        },
        hover_data=['num_orders', 'total_amt_usd'],  # Show additional data on hover
    )

    # Update layout for the bar chart
    fig.update_layout(
        xaxis_title='Sales Representative',
        yaxis_title='Contribution Percentage (%)',
        title_font=dict(size=16, color='white'),
        font=dict(size=14, color='white'),
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
        plot_bgcolor='rgba(0,0,0,0)',  # Transparent plot area
        showlegend=False  # Hide legend for clarity
    )

    # Display the chart in col2
    st.plotly_chart(fig)

# Define the query to fetch the data based on region selection
if region_choice == "All Regions":
    query = """
    SELECT CAST(EXTRACT(YEAR FROM CAST(occurred_at AS TIMESTAMP)) AS INT) AS year,
           CAST(EXTRACT(MONTH FROM CAST(occurred_at AS TIMESTAMP)) AS INT) AS month,
           SUM(total_amt_usd) AS total_usd,
           AVG(total_amt_usd) AS avg_order_amt,
           COUNT(id) AS total_orders,
           MAX(total_amt_usd) AS max_order_amt
    FROM orders
    WHERE CAST(EXTRACT(YEAR FROM CAST(occurred_at AS TIMESTAMP)) AS INT) IN (2013, 2017)
    GROUP BY year, month
    ORDER BY year ASC, month ASC;
    """
else:
    query = f"""
    SELECT CAST(EXTRACT(YEAR FROM CAST(occurred_at AS TIMESTAMP)) AS INT) AS year,
           CAST(EXTRACT(MONTH FROM CAST(occurred_at AS TIMESTAMP)) AS INT) AS month,
           SUM(o.total_amt_usd) AS total_usd,
           AVG(o.total_amt_usd) AS avg_order_amt,
           COUNT(o.id) AS total_orders,
           MAX(o.total_amt_usd) AS max_order_amt
    FROM orders o
    JOIN accounts a ON o.account_id = a.id
    JOIN sales_reps sr ON a.sales_rep_id = sr.id
    JOIN region r ON sr.region_id = r.id
    WHERE r.name = '{region_choice}'
      AND CAST(EXTRACT(YEAR FROM CAST(occurred_at AS TIMESTAMP)) AS INT) IN (2013, 2017)
    GROUP BY year, month
    ORDER BY year ASC, month ASC;
    """

# Fetch data from DuckDB
year_month_data = duckdb.query(query).df()

# Prepare data for visualization
year_month_data['month'] = year_month_data['month'].apply(lambda x: f"{x:02d}")  # Format month as two digits
year_month_data['year_month'] = year_month_data['year'].astype(str) + "-" + year_month_data['month']

# Ensure that the x-axis is ordered correctly
year_month_data = year_month_data.sort_values(by=['year', 'month'])

# Create a figure
fig = go.Figure()

# Add Line Plot for Total USD
fig.add_trace(go.Scatter(
    x=year_month_data['year_month'],
    y=year_month_data['total_usd'],
    mode='lines+markers',
    name='Total USD',
    line=dict(color='rgb(53, 151, 255)', width=2),
    marker=dict(color='rgb(53, 151, 255)', size=8)
))

# Add Line Plot for Average Order Amount
fig.add_trace(go.Scatter(
    x=year_month_data['year_month'],
    y=year_month_data['avg_order_amt'],
    mode='lines+markers',
    name='Average Order Amount (USD)',
    line=dict(color='rgb(255, 130, 50)', width=2),
    marker=dict(color='rgb(255, 130, 50)', size=8)
))

# Add Line Plot for Total Orders
fig.add_trace(go.Scatter(
    x=year_month_data['year_month'],
    y=year_month_data['total_orders'],
    mode='lines+markers',
    name='Total Orders',
    line=dict(color='rgb(255, 99, 132)', width=2),
    marker=dict(color='rgb(255, 99, 132)', size=8)
))

# Add Line Plot for Max Order Amount
fig.add_trace(go.Scatter(
    x=year_month_data['year_month'],
    y=year_month_data['max_order_amt'],
    mode='lines+markers',
    name='Max Order Amount (USD)',
    line=dict(color='rgb(54, 162, 235)', width=2),
    marker=dict(color='rgb(54, 162, 235)', size=8)
))

# Update layout for better visualization
fig.update_layout(
    title=f"Order Trends by Year and Month ({region_choice})",
    xaxis_title="Year-Month",
    yaxis_title="Amount / Number of Orders",
    xaxis_tickangle=-45,
    font=dict(size=14),
    paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
    plot_bgcolor='rgba(0,0,0,0)',  # Transparent plot area
    showlegend=True
)

# Display the plot in col2
with col3:
    st.plotly_chart(fig)

with col3:
    # plot1 - Average Order Amounts by Account Name
    if region_choice == 'All Regions':
        query = """
        SELECT 
            a.name AS account_name,
            AVG(o.standard_amt_usd) AS avg_standard_amt_usd,
            AVG(o.gloss_amt_usd) AS avg_gloss_amt_usd,
            AVG(o.poster_amt_usd) AS avg_poster_amt_usd
        FROM
            accounts a
                JOIN
            orders o ON a.id = o.account_id
        GROUP BY a.name;
        """
    else:
        query = f"""
        SELECT 
            a.name AS account_name,
            AVG(o.standard_amt_usd) AS avg_standard_amt_usd,
            AVG(o.gloss_amt_usd) AS avg_gloss_amt_usd,
            AVG(o.poster_amt_usd) AS avg_poster_amt_usd
        FROM
            accounts a
                JOIN
            orders o ON a.id = o.account_id
                JOIN
            sales_reps sr ON a.sales_rep_id = sr.id
                JOIN
            region r ON sr.region_id = r.id  -- Joining region via sales_reps
        WHERE r.name = '{region_choice}'  -- Filtering by region
        GROUP BY a.name;
        """
    
    # Get the data for the selected region
    avg_order_data = duckdb.query(query).df()

    # Prepare data for visualization
    fig = go.Figure()

    # Add traces for each type of order amount
    fig.add_trace(go.Scatter(
        x=avg_order_data['account_name'],
        y=avg_order_data['avg_standard_amt_usd'],
        mode='lines+markers',
        name='Avg Standard Amt (USD)',
        line=dict(color='royalblue'),
        marker=dict(symbol='circle')
    ))

    fig.add_trace(go.Scatter(
        x=avg_order_data['account_name'],
        y=avg_order_data['avg_gloss_amt_usd'],
        mode='lines+markers',
        name='Avg Gloss Amt (USD)',
        line=dict(color='green'),
        marker=dict(symbol='square')
    ))

    fig.add_trace(go.Scatter(
        x=avg_order_data['account_name'],
        y=avg_order_data['avg_poster_amt_usd'],
        mode='lines+markers',
        name='Avg Poster Amt (USD)',
        line=dict(color='orange'),
        marker=dict(symbol='diamond')
    ))

    # Update the layout for better visualization
    fig.update_layout(
        title=f"{region_choice}: Average Order Amounts by Account Name",
        xaxis_title="Account Name",
        yaxis_title="Average Order Amount (USD)",
        font=dict(size=14),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_tickangle=-45,  # Rotate x-axis labels for better readability
        showlegend=True
    )

    # Display the chart in the app
    st.plotly_chart(fig)

    #plot3
    # Define query based on region selection
    if region_choice == "All Regions":
        query = """
        SELECT we.channel,
               COUNT(we.id) AS total_events,
               COUNT(DISTINCT we.account_id) AS unique_accounts,
               COUNT(DISTINCT a.id) AS total_customers
        FROM web_events we
        LEFT JOIN accounts a ON we.account_id = a.id
        GROUP BY we.channel
        ORDER BY total_events DESC;
        """
    else:
        query = f"""
        SELECT we.channel,
               COUNT(we.id) AS total_events,
               COUNT(DISTINCT we.account_id) AS unique_accounts,
               COUNT(DISTINCT a.id) AS total_customers
        FROM web_events we
        LEFT JOIN accounts a ON we.account_id = a.id
        LEFT JOIN sales_reps sr ON a.sales_rep_id = sr.id
        LEFT JOIN region r ON sr.region_id = r.id
        WHERE r.name = '{region_choice}'
        GROUP BY we.channel
        ORDER BY total_events DESC;
        """

    # Fetch the data
    channel_data = duckdb.query(query).df()

    # Create a bar chart for Channel Effectiveness Analysis
    fig = go.Figure()

    # Add bars for total events
    fig.add_trace(go.Bar(
        x=channel_data['channel'],
        y=channel_data['total_events'],
        name='Total Events',
        marker_color='indianred'
    ))

    # Add bars for unique accounts
    fig.add_trace(go.Bar(
        x=channel_data['channel'],
        y=channel_data['unique_accounts'],
        name='Unique Accounts',
        marker_color='lightskyblue'
    ))

    # Add bars for total customers
    fig.add_trace(go.Bar(
        x=channel_data['channel'],
        y=channel_data['total_customers'],
        name='Total Customers',
        marker_color='lightgreen'
    ))

    # Update layout for better visualization
    fig.update_layout(
        title=f"Channel Effectiveness Analysis - {region_choice}",
        xaxis_title="Channel",
        yaxis_title="Count",
        barmode='group',  # Group bars side-by-side
        font=dict(size=14),
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
        plot_bgcolor='rgba(0,0,0,0)',  # Transparent plot area
        legend=dict(title="Metrics", orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        xaxis_tickangle=-45  # Rotate x-axis labels
    )

    # Display the chart in the app
    st.plotly_chart(fig)

    #plot4
    # Define query based on selected region
    query = f"""
    SELECT
        EXTRACT(MONTH FROM CAST(o.occurred_at AS TIMESTAMP)) AS month,
        SUM(o.total_amt_usd) AS total_sales
    FROM orders o
    LEFT JOIN accounts a ON o.account_id = a.id
    LEFT JOIN sales_reps sr ON a.sales_rep_id = sr.id
    LEFT JOIN region r ON sr.region_id = r.id
    WHERE r.name = '{region_choice}' OR '{region_choice}' = 'All Regions'
    GROUP BY month
    ORDER BY month;
    """

    # Fetch data from DuckDB
    seasonal_data = duckdb.query(query).df()

    # Map months to names
    month_names = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    seasonal_data['month_name'] = seasonal_data['month'].apply(lambda x: month_names[int(x) - 1])

    # Create a polar bar chart for seasonal trends
    fig = go.Figure()

    fig.add_trace(go.Barpolar(
        r=seasonal_data['total_sales'],
        theta=seasonal_data['month_name'],
        width=[30] * len(seasonal_data),  # Bar width
        marker=dict(
            color=seasonal_data['total_sales'],
            colorscale='viridis',  # Gradient color scheme with good contrast
            showscale=True,
            colorbar=dict(
                title='Total Sales (USD)',
                titlefont=dict(size=14, color='white'),
                tickfont=dict(size=12, color='white')
            )
        ),
        name='Seasonal Sales'
    ))

    # Update layout for better readability
    fig.update_layout(
        title=dict(
            text=f"Seasonal Sales Trends ({region_choice})",
            font=dict(size=18, color='white')
        ),
        polar=dict(
            angularaxis=dict(
                direction='clockwise',
                tickmode='array',
                tickvals=list(range(1, 13)),
                ticktext=month_names,
                tickfont=dict(size=12, color='white')  # White for contrast
            ),
            radialaxis=dict(
                visible=True,
                title="Total Sales (USD)",
                titlefont=dict(size=14, color='white'),
                tickfont=dict(size=12, color='white')
            )
        ),
        font=dict(size=14, color='white'),
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
        plot_bgcolor='rgba(0,0,0,0)'  # Transparent plot area
    )

    # Display the chart in col3
    st.plotly_chart(fig)

    #plot5
    # Query to fetch data based on region choice
    query = f"""
    WITH customer_summary AS (
        SELECT
            a.id AS account_id,
            a.name AS account_name,
            COUNT(o.id) AS total_orders,
            SUM(o.total_amt_usd) AS total_spend,
            DENSE_RANK() OVER (ORDER BY COUNT(o.id) DESC) AS order_rank,
            DENSE_RANK() OVER (ORDER BY SUM(o.total_amt_usd) DESC) AS spend_rank
        FROM accounts a
        LEFT JOIN orders o ON a.id = o.account_id
        LEFT JOIN sales_reps sr ON a.sales_rep_id = sr.id
        LEFT JOIN region r ON sr.region_id = r.id
        WHERE r.name = '{region_choice}' OR '{region_choice}' = 'All Regions'
        GROUP BY a.id, a.name
    )
    SELECT
        account_name,
        total_orders,
        total_spend,
        CASE
            WHEN order_rank <= 3 THEN 'Highly Active'
            WHEN order_rank <= 10 THEN 'Moderately Active'
            ELSE 'Less Active'
        END AS order_activity_segment,
        CASE
            WHEN spend_rank <= 3 THEN 'High Spender'
            WHEN spend_rank <= 10 THEN 'Moderate Spender'
            ELSE 'Low Spender'
        END AS spending_segment
    FROM customer_summary
    ORDER BY order_rank, spend_rank;
    """

    # Fetch data from DuckDB
    customer_segmentation_data = duckdb.query(query).df()

    # Create a scatter plot for customer segmentation
    fig = go.Figure()

    # Add a scatter plot for customer segments
    fig.add_trace(go.Scatter(
        x=customer_segmentation_data['total_orders'],
        y=customer_segmentation_data['total_spend'],
        mode='markers',
        text=customer_segmentation_data['account_name'],
        hoverinfo='text+x+y',  # Show account name, orders, and spend on hover
        marker=dict(
            size=12,
            color=customer_segmentation_data['order_activity_segment'].apply(
                lambda x: {'Highly Active': 'rgba(54, 162, 235, 0.6)', 
                           'Moderately Active': 'rgba(255, 159, 64, 0.6)', 
                           'Less Active': 'rgba(255, 99, 132, 0.6)'}[x]
            ),
            line=dict(color='black', width=1)  # Black outline for better visibility
        ),
        name="Customer Segmentation"
    ))

    # Update layout for the scatter plot
    fig.update_layout(
        title=f"Customer Segmentation by Purchase Frequency and Total Spend ({region_choice})",
        xaxis=dict(
            title="Total Orders",
            titlefont=dict(size=14, color='white'),
            tickfont=dict(size=12, color='white')
        ),
        yaxis=dict(
            title="Total Spend (USD)",
            titlefont=dict(size=14, color='white'),
            tickfont=dict(size=12, color='white')
        ),
        font=dict(size=14, color='white'),
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
        plot_bgcolor='rgba(0,0,0,0)',  # Transparent plot area
        showlegend=False  # Hide legend for clarity
    )

    # Display the chart in col3
    st.plotly_chart(fig)

# Define the query to fetch the data based on region selection
query = f"""
WITH account_order_count AS (
    SELECT
        a.id AS account_id,
        a.name AS account_name,
        COUNT(o.id) AS order_count,
        SUM(o.total_amt_usd) AS total_sales,
        r.name AS region_name
    FROM accounts a
    LEFT JOIN orders o ON a.id = o.account_id
    LEFT JOIN sales_reps sr ON a.sales_rep_id = sr.id
    LEFT JOIN region r ON sr.region_id = r.id
    WHERE r.name = '{region_choice}' OR '{region_choice}' = 'All Regions'
    GROUP BY a.id, a.name, r.name
),
activity_segments AS (
    SELECT
        account_id,
        account_name,
        total_sales,
        region_name,
        CASE
            WHEN order_count > 20 THEN 'High Activity'
            WHEN order_count BETWEEN 10 AND 20 THEN 'Medium Activity'
            ELSE 'Low Activity'
        END AS activity_segment
    FROM account_order_count
)
SELECT
    region_name,
    activity_segment,
    AVG(total_sales) AS avg_sales
FROM activity_segments
GROUP BY region_name, activity_segment
ORDER BY region_name, avg_sales DESC;
"""

# Fetch data from DuckDB based on the selected region
activity_sales_data = duckdb.query(query).df()

# Create a plot with colors corresponding to different regions
fig = go.Figure()

# Define colors for each region
region_colors = {
    'North': 'rgba(54, 162, 235, 0.6)',   # Blue
    'South': 'rgba(255, 159, 64, 0.6)',   # Orange
    'East': 'rgba(75, 192, 192, 0.6)',    # Green
    'West': 'rgba(153, 102, 255, 0.6)',   # Purple
    'Central': 'rgba(255, 99, 132, 0.6)', # Red
}

# Add traces for each region in the selected data
for region in activity_sales_data['region_name'].unique():
    region_data = activity_sales_data[activity_sales_data['region_name'] == region]
    
    fig.add_trace(go.Bar(
        x=region_data['activity_segment'],
        y=region_data['avg_sales'],
        name=region,
        marker=dict(color=region_colors.get(region, 'rgba(169, 169, 169, 0.6)')),  # Default color if region is not listed
        text=region_data['activity_segment'],
        hoverinfo='text+y',  # Show activity segment and avg sales
    ))

# Update layout for the bar chart
fig.update_layout(
    title=f"Average Sales by Account Activity Segment ({region_choice})",
    xaxis=dict(title="Account Activity Segment"),
    yaxis=dict(title="Average Sales (USD)"),
    barmode='stack',  # Stack bars for each region
    paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
    plot_bgcolor='rgba(0,0,0,0)',  # Transparent plot area
    font=dict(size=14, color='white'),
)

# Display the plot in col3
with col3:
    st.plotly_chart(fig)

st.markdown(
    """
    <hr>
    <div style='text-align: center;'>
        <p style='font-size: 1.2em; font-family: "Arial", sans-serif;'>
            © 2025 All rights reserved by <a href='https://github.com/RobinMillford' target='_blank'><img src='https://img.icons8.com/?size=100&id=LoL4bFzqmAa0&format=png&color=000000' height='30' style='vertical-align: middle;'></a>
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# Customer Insights and Regional Sales Dashboard

## Overview

This Streamlit dashboard provides an interactive and comprehensive analysis of customer behavior, regional sales trends, and revenue insights. The dashboard enables businesses to identify key performance metrics, customer segments, and revenue drivers, supporting data-driven decision-making.

The visualizations and analyses span several dimensions, including order frequency, spending behavior, regional trends, and yearly comparisons. It highlights critical insights to help optimize strategies and improve business outcomes.

## Features

### Key Dashboard Highlights:

- **Regional Sales Analysis**:
  - Filter by region to explore sales performance across different locations.
  - Compare total sales amounts and customer activity for targeted decision-making.

- **Customer Segmentation**:
  - Categorize customers into segments like "High Volume" or "High Spender" based on their order and spending patterns.
  - Analyze customer distribution and behavior with scatter plots and bar charts.

- **Yearly Trends and Seasonal Insights**:
  - Compare total sales trends between 2013 and 2017.
  - Visualize monthly patterns using line and scatter plots.

- **Order Patterns**:
  - Explore average order sizes and standard deviations by customer segments.
  - Highlight consistency in spending and order behavior across regions.

- **Top Performers**:
  - Identify high-performing accounts and sales representatives contributing to revenue growth.

### Data Visualizations:

- Line, scatter, and bar charts for order trends and revenue analysis.
- Segmented visualizations to identify patterns in spending and customer activity.
- Interactive filters for region and year to drill down into data insights.

## Setup and Installation

### Clone the Repository

```bash
git clone https://github.com/RobinMillford/Sales-Metrics-Dashboard-Streamlit.git
cd Sales-Metrics-Dashboard-Streamlit
```

### Install Dependencies

Ensure you have Python installed. It is recommended to use a virtual environment:

```bash
python -m venv venv
source venv/bin/activate   # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```

### Run the Dashboard Locally

```bash
streamlit run sales_dashboard.py
```

### Deployment

The dashboard is deployed on **Streamlit Community Cloud**. Access it here: [Customer Sales Dashboard](https://sales-metrics-dashboard-app.streamlit.app/)

## Data

Ensure that the dataset used for analysis is correctly formatted and located in the appropriate directory. For this project, a preprocessed dataset containing accounts, orders, sales representatives, and regions is used to power the dashboard's insights.

### Dataset Includes:
- Order details (e.g., amounts, dates).
- Customer account information.
- Sales representative and region mapping.

## Insights and Findings

- **Increased Revenue Awareness:** Clear understanding of high-value accounts and regions driving revenue growth.
- **Customer Behavior:** Identification of spending patterns and order frequency across different segments.
- **Seasonality:** Trends highlighting seasonal peaks and troughs for better demand planning.
- **Operational Insights:** Patterns in order size and variability to improve consistency and efficiency.

## Contributing

Contributions are welcome! Please fork the repository and create a pull request with your changes.

## License

This project is licensed under the AGPL-3.0 license License - see the LICENSE file for details.


import streamlit as st
import pandas as pd
import plotly.express as px

# Page Configuration
st.set_page_config(page_title="NovaRetail Dashboard", layout="wide")

# 1. Load Data
@st.cache_data
def load_data():
    try:
        # Load the dataset
        df = pd.read_excel("NR_dataset.xlsx")
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # 2. Sidebar Filters
    st.sidebar.header("Filter Options")

    # Segment Filter
    segments = df['label'].dropna().unique().tolist()
    selected_segments = st.sidebar.multiselect("Select Customer Segment", segments, default=segments)

    # Region Filter
    regions = df['CustomerRegion'].unique().tolist()
    selected_regions = st.sidebar.multiselect("Select Region", regions, default=regions)

    # Category Filter
    categories = df['ProductCategory'].unique().tolist()
    selected_categories = st.sidebar.multiselect("Select Product Category", categories, default=categories)

    # Channel Filter
    channels = df['RetailChannel'].unique().tolist()
    selected_channels = st.sidebar.multiselect("Select Retail Channel", channels, default=channels)

    # Apply Filters
    filtered_df = df[
        (df['label'].isin(selected_segments)) &
        (df['CustomerRegion'].isin(selected_regions)) &
        (df['ProductCategory'].isin(selected_categories)) &
        (df['RetailChannel'].isin(selected_channels))
    ]

    # 3. Title and Intro
    st.title("NovaRetail Strategic Dashboard")
    st.markdown("""
    This dashboard provides an interactive view of NovaRetail's customer data, highlighting revenue drivers,
    satisfaction levels, and high-value customers to support strategic decision-making.
    """)

    # 4. KPI Section
    if not filtered_df.empty:
        kpi1, kpi2, kpi3 = st.columns(3)

        total_revenue = filtered_df['PurchaseAmount'].sum()
        avg_satisfaction = filtered_df['CustomerSatisfaction'].mean()
        total_transactions = len(filtered_df)

        kpi1.metric("Total Revenue", f"${total_revenue:,.2f}")
        kpi2.metric("Avg Satisfaction", f"{avg_satisfaction:.2f}")
        kpi3.metric("Total Transactions", f"{total_transactions}")

        st.markdown("---")

        # 5. Charts
        col1, col2 = st.columns(2)

        # Revenue by Segment
        with col1:
            st.subheader("Revenue by Customer Segment")
            rev_by_segment = filtered_df.groupby('label')['PurchaseAmount'].sum().reset_index()
            fig_segment = px.bar(rev_by_segment, x='label', y='PurchaseAmount',
                                 color='label', title="Total Revenue by Segment",
                                 labels={'PurchaseAmount': 'Revenue ($)', 'label': 'Segment'})
            st.plotly_chart(fig_segment, use_container_width=True)

        # Revenue by Region
        with col2:
            st.subheader("Revenue by Region")
            rev_by_region = filtered_df.groupby('CustomerRegion')['PurchaseAmount'].sum().reset_index()
            fig_region = px.pie(rev_by_region, values='PurchaseAmount', names='CustomerRegion',
                                title="Revenue Distribution by Region")
            st.plotly_chart(fig_region, use_container_width=True)

        col3, col4 = st.columns(2)

        # Satisfaction by Segment
        with col3:
            st.subheader("Satisfaction Distribution")
            fig_sat = px.box(filtered_df, x='label', y='CustomerSatisfaction', color='label',
                             title="Customer Satisfaction by Segment",
                             labels={'CustomerSatisfaction': 'Score (1-5)', 'label': 'Segment'})
            st.plotly_chart(fig_sat, use_container_width=True)

        # Top Customers
        with col4:
            st.subheader("Top 5 High-Value Customers")
            top_customers = filtered_df.groupby('CustomerID')['PurchaseAmount'].sum().reset_index()
            top_5 = top_customers.sort_values(by='PurchaseAmount', ascending=False).head(5)
            fig_top = px.bar(top_5, x='PurchaseAmount', y='CustomerID', orientation='h',
                             title="Top 5 Customers by Revenue",
                             labels={'PurchaseAmount': 'Total Spend ($)', 'CustomerID': 'Customer ID'})
            # Force CustomerID to be treated as category/string on axis to display properly
            fig_top.update_yaxes(type='category')
            st.plotly_chart(fig_top, use_container_width=True)

        # 6. Raw Data
        with st.expander("View Raw Data"):
            st.dataframe(filtered_df)
    else:
        st.warning("No data available for the selected filters. Please adjust your selection.")
else:
    st.warning("Dataset is empty or could not be loaded.")

import streamlit as st
import urllib
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from func import DataAnalyzer, BrazilMapPlotter

# Setup style
sns.set_theme(style='darkgrid')

# Load datasets
date_fields = ["order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date",
               "order_estimated_delivery_date", "order_purchase_timestamp", "shipping_limit_date"]

orders_df = pd.read_csv("https://raw.githubusercontent.com/anwarJIHAD/data-analyst-python/refs/heads/main/dashboard/df.csv")
orders_df.sort_values("order_approved_at", inplace=True)
orders_df.reset_index(drop=True, inplace=True)

geo_df = pd.read_csv("https://raw.githubusercontent.com/anwarJIHAD/data-analyst-python/refs/heads/main/dashboard/geolocation.csv")
unique_customers = geo_df.drop_duplicates(subset='customer_unique_id')

# Convert datetime columns
for field in date_fields:
    orders_df[field] = pd.to_datetime(orders_df[field])

# Determine date boundaries
earliest = orders_df["order_approved_at"].min()
latest = orders_df["order_approved_at"].max()

# Sidebar UI
with st.sidebar:
    _, logo, _ = st.columns(3)
    with logo:
        st.image("https://raw.githubusercontent.com/anwarJIHAD/data-analyst-python/refs/heads/main/dashboard/logo.png", width=100)

    selected_start, selected_end = st.date_input(
        "Select Date Range",
        value=[earliest, latest],
        min_value=earliest,
        max_value=latest
    )

# Filter data by selected dates
filtered_data = orders_df[(orders_df["order_approved_at"] >= str(selected_start)) & 
                          (orders_df["order_approved_at"] <= str(selected_end))]

# Init custom classes
analyzer = DataAnalyzer(filtered_data)
plotter = BrazilMapPlotter(unique_customers, plt, mpimg, urllib, st)

# Process data
daily_data = analyzer.create_daily_orders_df()
customer_spend = analyzer.create_sum_spend_df()
product_items = analyzer.create_sum_order_items_df()
ratings, common_rating = analyzer.review_score_df()
by_region, top_state = analyzer.create_bystate_df()
status_info, frequent_status = analyzer.create_order_status()

# Dashboard
st.title("analisa data e commerce")
st.markdown("Sebuah visualisasi data e commerce yang lagi trand dengan menggunakan data yang public")

# --- Section: Daily Orders ---
st.subheader("Order Delivery Trend")
left, right = st.columns(2)

with left:
    st.markdown(f"**Total Orders:** {daily_data['order_count'].sum()}")

with right:
    st.markdown(f"**Total Revenue:** {daily_data['revenue'].sum()}")

plt.figure(figsize=(12, 6))
sns.lineplot(x=daily_data["order_approved_at"], y=daily_data["order_count"], marker="o", linewidth=2, color="skyblue")
plt.xticks(rotation=45)
st.pyplot(plt)

# --- Section: Customer Spending ---
st.subheader("Spending Behavior")

col_spend_1, col_spend_2 = st.columns(2)
col_spend_1.metric("Total Spend", f"{customer_spend['total_spend'].sum():,.0f}")
col_spend_2.metric("Avg Spend per Order", f"{customer_spend['total_spend'].mean():,.2f}")

fig_spend, ax_spend = plt.subplots(figsize=(12, 6))
sns.lineplot(data=customer_spend, x="order_approved_at", y="total_spend", marker="o", ax=ax_spend, color="blue")
ax_spend.tick_params(axis="x", rotation=45)
st.pyplot(fig_spend)

# --- Section: Product Orders ---
st.subheader("Product Sales Overview")

top_items = product_items.head(5)
least_items = product_items.sort_values(by="product_count", ascending=True).head(5)

fig_bar, axes = plt.subplots(1, 2, figsize=(30, 12))
sns.barplot(data=top_items, x="product_count", y="product_category_name_english", ax=axes[0], palette="plasma")
axes[0].set_title("Top 5 Products")

sns.barplot(data=least_items, x="product_count", y="product_category_name_english", ax=axes[1], palette="plasma")
axes[1].invert_xaxis()
axes[1].set_title("Least 5 Products")

st.pyplot(fig_bar)

# --- Section: Reviews ---
st.subheader("Customer Reviews Summary")

st.markdown(f"**Average Score:** {ratings.mean():.2f}")
st.markdown(f"**Most Frequent Rating:** {ratings.value_counts().idxmax()}")

fig_review, ax_review = plt.subplots(figsize=(12, 6))
colors = sns.color_palette("mako", len(ratings))
sns.barplot(x=ratings.index, y=ratings.values, palette=colors, ax=ax_review)
for i, val in enumerate(ratings.values):
    ax_review.text(i, val + 3, str(val), ha='center')
st.pyplot(fig_review)

# --- Section: Demographics ---
st.subheader("Customer Demographics")
tab_states, tab_map = st.tabs(["State Distribution", "Customer Locations"])

with tab_states:
    st.markdown(f"**Most Common State:** {by_region.customer_state.value_counts().idxmax()}")
    fig_state, ax_state = plt.subplots(figsize=(12, 6))
    sns.barplot(x=by_region.customer_state.value_counts().index, y=by_region.customer_count.values, ax=ax_state, palette="viridis")
    st.pyplot(fig_state)

with tab_map:
    plotter.plot()
    with st.expander("Map Insights"):
        st.write("Customers are concentrated in southeastern Brazil, especially around major cities.")

# Footer
st.caption("© 2025 MHD Anwar – E-Commerce Insights Platform")

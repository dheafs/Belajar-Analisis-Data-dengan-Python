import streamlit as st
import pandas as pd
import geopandas as gpd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import datetime as dt
import urllib

sns.set(style="darkgrid")

# read dataset
all_df = pd.read_csv('https://raw.githubusercontent.com/dheafs/Belajar-Analisis-Data-dengan-Python/refs/heads/main/dashboard/main_data.csv')
geo_df = pd.read_csv('https://raw.githubusercontent.com/dheafs/Belajar-Analisis-Data-dengan-Python/refs/heads/main/dashboard/geolocation.csv')

# change type str/obj -> datetime
datetime_cols = [
    'order_purchase_timestamp',
    'order_approved_at',
    'order_delivered_carrier_date',
    'order_delivered_customer_date',
    'order_estimated_delivery_date',
    'review_creation_date',
    'review_answer_timestamp',
    'shipping_limit_date'
]
for col in datetime_cols:
    all_df[col] = pd.to_datetime(all_df[col], errors='coerce')

# define function
def order_per_month(df, start_date, end_date):
    monthly_df = df.resample(rule='ME', on='order_purchase_timestamp').agg({
        "order_id": "size"
        }).rename(columns={
            "order_id": "order_count"
            })

    monthly_df = monthly_df[(monthly_df.index >= start_date) & (monthly_df.index <= end_date)]
    monthly_df = monthly_df.reset_index()
    monthly_df['order_purchase_timestamp'] = monthly_df['order_purchase_timestamp'].dt.strftime('%Y-%m')

    plt.figure(figsize=(10, 5))
    plt.plot(
        monthly_df["order_purchase_timestamp"],
        monthly_df["order_count"],
        marker='o',
        linewidth=2,
        color="#E2725B"
    )
    plt.xticks(fontsize=10, rotation=45)
    plt.yticks(fontsize=10)
    plt.xlabel("Month")
    plt.ylabel("Order Count")
    plt.grid()
    plt.show()

def order_per_day(df, start_date, end_date):
    daily_df = df.resample(rule='D', on='order_purchase_timestamp').agg({
        "order_id": "size"
        }).rename(columns={
            "order_id": "order_count"
            })

    daily_df = daily_df[(daily_df.index >= start_date) & (daily_df.index <= end_date)]
    daily_df = daily_df.reset_index()

    daily_df['order_purchase_timestamp'] = daily_df['order_purchase_timestamp'].dt.strftime('%Y-%m-%d')

    plt.figure(figsize=(10, 5))
    plt.plot(
        daily_df["order_purchase_timestamp"],
        daily_df["order_count"],
        linewidth=1,
        color="#E2725B"
    )
    plt.xticks(fontsize=10, rotation=90)
    plt.yticks(fontsize=10)
    plt.xlabel("Date")
    plt.ylabel("Order Count")
    plt.grid()
    plt.show()

def sum_order_revenue(df, start_date, end_date):
    order_revenue_df = df.resample(rule='D', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "payment_value": "sum"
    })
    order_revenue_df = order_revenue_df[(order_revenue_df.index >= start_date) & (order_revenue_df.index <= end_date)]
    order_revenue_df = order_revenue_df.reset_index()
    order_revenue_df.rename(columns={
        "order_id": "order_count",
        "payment_value": "revenue"
    }, inplace=True)
    return order_revenue_df

def customer_spend_per_month(df, start_date, end_date):
    sum_spend_df = df.resample(rule='ME', on='order_approved_at').agg({
        "price": "sum"
        }).rename(columns={
            "price": "total_spend"
            })

    sum_spend_df = sum_spend_df[(sum_spend_df.index >= start_date) & (sum_spend_df.index <= end_date)]
    sum_spend_df = sum_spend_df.reset_index()
    sum_spend_df['order_approved_at'] = sum_spend_df['order_approved_at'].dt.strftime('%Y-%m')

    plt.figure(figsize=(10, 5))
    plt.plot(
        sum_spend_df["order_approved_at"],
        sum_spend_df["total_spend"],
        marker='o',
        linewidth=2,
        color="#E2725B"
    )
    plt.xticks(fontsize=10, rotation=45)
    plt.yticks(fontsize=10)
    plt.xlabel("Month")
    plt.ylabel("Total Spend")
    plt.grid()
    plt.show()

def customer_spend_per_day(df, start_date, end_date):
    sum_spend_df = df.resample(rule='D', on='order_approved_at').agg({
        "price": "sum"
        }).rename(columns={
            "price": "total_spend"
            })

    sum_spend_df = sum_spend_df[(sum_spend_df.index >= start_date) & (sum_spend_df.index <= end_date)]
    sum_spend_df = sum_spend_df.reset_index()

    sum_spend_df['order_approved_at'] = sum_spend_df['order_approved_at'].dt.strftime('%Y-%m-%d')

    plt.figure(figsize=(10, 5))
    plt.plot(
        sum_spend_df["order_approved_at"],
        sum_spend_df["total_spend"],
        linewidth=1,
        color="#E2725B"
    )
    plt.xticks(fontsize=10, rotation=90)
    plt.yticks(fontsize=10)
    plt.xlabel("Date")
    plt.ylabel("Total Spend")
    plt.grid()
    plt.show()

def sum_customer_spend(df, start_date, end_date):
    sum_spend_df = df.resample(rule='D', on='order_approved_at').agg({
        "payment_value": "sum"
    })
    sum_spend_df = sum_spend_df[(sum_spend_df.index >= start_date) & (sum_spend_df.index <= end_date)]
    sum_spend_df = sum_spend_df.reset_index()
    sum_spend_df.rename(columns={
        "payment_value": "total_spend"
    }, inplace=True)
    return sum_spend_df

def highest_selling(df, start_date, end_date):
    filtered_df_sell = df[(df['order_approved_at'] >= start_date) & (df['order_approved_at'] <= end_date)]
    product_id_counts = filtered_df_sell.groupby('product_category_name_english')['product_id'].count().reset_index()
    sorted_df = product_id_counts.sort_values(by='product_id', ascending=False)

    fig, ax = plt.subplots(figsize=(12, 8))
    colors = ["#E1785B", "#d14b80", "#d14b80", "#d14b80", "#d14b80"]

    sns.barplot(x="product_id", y="product_category_name_english", data=sorted_df.head(5), hue="product_category_name_english", palette=colors, ax=ax, legend=False)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='y', labelsize=20)
    ax.tick_params(axis='x', labelsize=20)

    plt.tight_layout()
    plt.show()

def lowest_selling(df, start_date, end_date):
    filtered_df_sell = df[(df['order_approved_at'] >= start_date) & (df['order_approved_at'] <= end_date)]
    product_id_counts = filtered_df_sell.groupby('product_category_name_english')['product_id'].count().reset_index()
    sorted_df = product_id_counts.sort_values(by='product_id', ascending=True)

    fig, ax = plt.subplots(figsize=(12, 8))
    colors = ["#E1785B", "#d14b80", "#d14b80", "#d14b80", "#d14b80"]

    sns.barplot(x="product_id", y="product_category_name_english", data=sorted_df.head(5), hue="product_category_name_english", palette=colors, ax=ax, legend=False)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.invert_xaxis()
    ax.yaxis.set_label_position("right")
    ax.yaxis.tick_right()
    ax.tick_params(axis='y', labelsize=20)
    ax.tick_params(axis='x', labelsize=20)

    plt.tight_layout()
    plt.show()

def sum_order_items(df, start_date, end_date):
    sum_order_items_df = df[(df['order_approved_at'] >= start_date) & (df['order_approved_at'] <= end_date)]
    sum_order_items_df = df.groupby("product_category_name_english")["product_id"].count().reset_index()
    sum_order_items_df.rename(columns={
        "product_id": "product_count"
    }, inplace=True)
    sum_order_items_df = sum_order_items_df.sort_values(by='product_count', ascending=False)
    return sum_order_items_df

def review_score(df, start_date, end_date):
    filtered_df_rat = df[(df['order_approved_at'] >= start_date) & (df['order_approved_at'] <= end_date)]

    rating_service = filtered_df_rat['review_score'].value_counts().sort_index(ascending=False)
    rating_service.index = pd.CategoricalIndex(rating_service.index, categories=[5, 4, 3, 2, 1], ordered=True)

    colors = ["#E1785B", "#d14b80", "#d14b80", "#d14b80", "#d14b80"]

    plt.figure(figsize=(10, 5))
    sns.barplot(x=rating_service.index,
                y=rating_service.values,
                hue=rating_service.index,
                palette=colors,
                legend=False
                )

    plt.xlabel("Rating")
    plt.ylabel("Number of Customers")
    plt.xticks(fontsize=12)
    plt.show()

def most_review_score(df, start_date, end_date):
    review_scores = df[(df['order_approved_at'] >= start_date) & (df['order_approved_at'] <= end_date)]
    review_scores = review_scores['review_score'].value_counts().sort_values(ascending=False)
    return review_scores

def calculate_rfm(df, now, start_date, end_date):
    filtered_df_rfm = df[(df['order_purchase_timestamp'] >= start_date) & (df['order_purchase_timestamp'] <= end_date)]

    recency = (now - filtered_df_rfm.groupby('customer_id')['order_purchase_timestamp'].max()).dt.days
    frequency = filtered_df_rfm.groupby('customer_id')['order_id'].count()
    monetary = filtered_df_rfm.groupby('customer_id')['price'].sum()

    rfm = pd.DataFrame({
        'customer_id': recency.index,
        'Recency': recency.values,
        'Frequency': frequency.values,
        'Monetary': monetary.values
    })

    return rfm

def recency(rfm):
    recency_data = rfm.sort_values(by="Recency", ascending=True).head(5)

    fig, ax = plt.subplots(figsize=(12, 8))
    colors = ["#E2725B"] * len(recency_data)

    sns.barplot(y="Recency", x="customer_id", data=recency_data, hue="customer_id", palette=colors, ax=ax, legend=False)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='x', labelsize=20)
    ax.tick_params(axis='y', labelsize=20)
    ax.set_xticks(range(len(recency_data)))
    ax.set_xticklabels(recency_data['customer_id'].values, rotation=90)

    plt.show()

def frequency(rfm):
    frequency_data = rfm.sort_values(by="Frequency", ascending=False).head(5)

    fig, ax = plt.subplots(figsize=(12, 8))
    colors = ["#E2725B"] * len(frequency_data)

    sns.barplot(y="Frequency", x="customer_id", data=frequency_data, hue="customer_id", palette=colors, ax=ax, legend=False)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='x', labelsize=20)
    ax.tick_params(axis='y', labelsize=20)
    ax.set_xticks(range(len(frequency_data)))
    ax.set_xticklabels(frequency_data['customer_id'].values, rotation=90)

    plt.show()

def monetary(rfm):
    monetary_data = rfm.sort_values(by="Monetary", ascending=False).head(5)

    fig, ax = plt.subplots(figsize=(12, 8))
    colors = ["#E2725B"] * len(monetary_data)

    sns.barplot(y="Monetary", x="customer_id", data=monetary_data, hue="customer_id", palette=colors, ax=ax, legend=False)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='x', labelsize=20)
    ax.tick_params(axis='y', labelsize=20)
    ax.set_xticks(range(len(monetary_data)))
    ax.set_xticklabels(monetary_data['customer_id'].values, rotation=90)

    plt.show()

def geo(df):
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df['geolocation_lng'], df['geolocation_lat']))

    brazil = mpimg.imread(urllib.request.urlopen('https://i.pinimg.com/originals/3a/0c/e1/3a0ce18b3c842748c255bc0aa445ad41.jpg'), 'jpg')

    fig, ax = plt.subplots(figsize=(10, 10))
    gdf.drop_duplicates(subset='customer_unique_id').plot(ax=ax, marker='o', color='#E2725B', markersize=5, alpha=0.5)
    plt.axis('off')
    ax.imshow(brazil, extent=[-73.98283055, -33.8, -33.75116944, 5.4])
    plt.show()

def most_common_state(df):
    bystate_df = df.groupby(by="customer_state").customer_id.nunique().reset_index()
    bystate_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    bystate_df = bystate_df.sort_values(by='customer_count', ascending=False)
    return bystate_df

# page
st.set_page_config(
    layout='wide',
    page_title='E-Commerce Dashboard',
    page_icon=':shopping_trolley:'
)

# sidebar
min_date = all_df['order_purchase_timestamp'].min()
max_date = all_df['order_purchase_timestamp'].max()

with st.sidebar:
    st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQCVvQ1EpMaLkYitvXRNJIGlDczpEr3F7IXCQ&s", width=200)

    # date range
    start_date, end_date = st.date_input(
        label="Select Date Range",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )

    st.caption('Copyright (C) Dhea 2024')

start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# main
st.title("Brazilian E-Commerce Public Dashboard")

st.write("**This is a dashboard for analyzing Brazilian E-Commerce Public Dataset.**")
url = "https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce"
link_text = "Visit Kaggle Dataset "
st.write(f"[{link_text}]({url})")

duration = (end_date - start_date).days

if duration <= 45:
    # order
    st.subheader('Total Orders per Day')

    col1, col2 = st.columns(2)
    with col1:
        total_order = sum_order_revenue(all_df, start_date, end_date)["order_count"].sum()
        st.markdown(f"Total Order: **{total_order}**")
    with col2:
        total_revenue = sum_order_revenue(all_df, start_date, end_date)["revenue"].sum()
        st.markdown(f"Total Revenue: **{total_revenue:.2f}**")

    order_per_day(all_df, start_date, end_date)
    st.pyplot(plt)

    # customer spend
    st.subheader('Total Customer Spend per Day')

    col1, col2 = st.columns(2)
    with col1:
        total_spend = sum_customer_spend(all_df, start_date, end_date)["total_spend"].sum()
        st.markdown(f"Total Spend: **{total_spend}**")
    with col2:
        avg_spend = sum_customer_spend(all_df, start_date, end_date)["total_spend"].mean()
        st.markdown(f"Average Spend: **{avg_spend:.2f}**")

    customer_spend_per_day(all_df, start_date, end_date)
    st.pyplot(plt)
else:
    tabs = st.tabs(["Monthly", "Daily"])

    with tabs[0]:
        # order
        st.subheader('Total Orders per Month')

        col1, col2 = st.columns(2)
        with col1:
            total_order = sum_order_revenue(all_df, start_date, end_date)["order_count"].sum()
            st.markdown(f"Total Order: **{total_order}**")
        with col2:
            total_revenue = sum_order_revenue(all_df, start_date, end_date)["revenue"].sum()
            st.markdown(f"Total Revenue: **{total_revenue:.2f}**")

        order_per_month(all_df, start_date, end_date)
        st.pyplot(plt)

        # customer spend
        st.subheader('Total Customer Spend per Month')

        col1, col2 = st.columns(2)
        with col1:
            total_spend = sum_customer_spend(all_df, start_date, end_date)["total_spend"].sum()
            st.markdown(f"Total Spend: **{total_spend}**")
        with col2:
            avg_spend = sum_customer_spend(all_df, start_date, end_date)["total_spend"].mean()
            st.markdown(f"Average Spend: **{avg_spend:.2f}**")

        customer_spend_per_month(all_df, start_date, end_date)
        st.pyplot(plt)
    with tabs[1]:
        # order
        st.subheader('Total Orders per Day')

        col1, col2 = st.columns(2)
        with col1:
            total_order = sum_order_revenue(all_df, start_date, end_date)["order_count"].sum()
            st.markdown(f"Total Order: **{total_order}**")
        with col2:
            total_revenue = sum_order_revenue(all_df, start_date, end_date)["revenue"].sum()
            st.markdown(f"Total Revenue: **{total_revenue:.2f}**")

        order_per_day(all_df, start_date, end_date)
        plt.xticks([])
        plt.xlabel(None)
        st.pyplot(plt)
        plt.clf()

        # customer spend
        st.subheader('Total Customer Spend per Day')

        col1, col2 = st.columns(2)
        with col1:
            total_spend = sum_customer_spend(all_df, start_date, end_date)["total_spend"].sum()
            st.markdown(f"Total Spend: **{total_spend}**")
        with col2:
            avg_spend = sum_customer_spend(all_df, start_date, end_date)["total_spend"].mean()
            st.markdown(f"Average Spend: **{avg_spend:.2f}**")

        customer_spend_per_day(all_df, start_date, end_date)
        plt.xticks([])
        plt.xlabel(None)
        st.pyplot(plt)
        plt.clf()

# high low order
st.subheader("Most And Least Sold Product")

col1, col2 = st.columns(2)
with col1:
    total_items = sum_order_items(all_df, start_date, end_date)["product_count"].sum()
    st.markdown(f"Total Items: **{total_items}**")

    st.markdown("**Products with the Highest Sales**")
    highest_selling(all_df, start_date, end_date)
    st.pyplot(plt)
with col2:
    avg_items = sum_order_items(all_df, start_date, end_date)["product_count"].mean()
    st.markdown(f"Average Items: **{avg_items:.2f}**")

    st.markdown("**Products with the Lowest Sales**")
    lowest_selling(all_df, start_date, end_date)
    st.pyplot(plt)

# review score
st.subheader("Rating Customer By Service")

col1, col2 = st.columns(2)
common_review_score = most_review_score(all_df, start_date, end_date)
with col1:
    avg_review_score = common_review_score.mean()
    st.markdown(f"Average Review Score: **{avg_review_score:.2f}**")
with col2:
    most_common_review_score = common_review_score.value_counts().idxmax()
    st.markdown(f"Most Common Review Score: **{most_common_review_score}**")

review_score(all_df, start_date, end_date)
st.pyplot(plt)

# rfm
st.subheader("Best Customer Based on RFM Parameters (customer_id)")

now = st.date_input(
    label="Select Date for RFM",
    value=dt.datetime(2018,10,20),
    min_value=min_date,
    max_value=dt.datetime(2018,10,20)
)
now = pd.to_datetime(now)
rfm = calculate_rfm(all_df, now, start_date, end_date)

if now >= end_date:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**By Recency (days)**")
        recency(rfm)
        st.pyplot(plt)
    with col2:
        st.markdown("**By Frequency**")
        frequency(rfm)
        st.pyplot(plt)
    with col3:
        st.markdown("**By Monetary**")
        monetary(rfm)
        st.pyplot(plt)

else:
    st.warning("The 'date' value must be greater than the 'end date'. Reset the 'date' value to 'end date'.")
    now = end_date
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**By Recency (days)**")
        recency(rfm)
        st.pyplot(plt)
    with col2:
        st.markdown("**By Frequency**")
        frequency(rfm)
        st.pyplot(plt)
    with col3:
        st.markdown("**By Monetary**")
        monetary(rfm)
        st.pyplot(plt)

# customer demographic
st.subheader("Customer Demographic in Brazil")
common_state = most_common_state(geo_df).customer_state.value_counts().index[0]
st.markdown(f"Most Common State: **{common_state}**")
geo(geo_df)
st.pyplot(plt)

st.caption('Copyright (C) Dhea 2024')


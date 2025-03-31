# Import Library
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from pyarrow import nulls

sns.set_style(style='dark')

# Helper Function
def create_quarterly_df(df):
    quarterly_data = df.groupby("Quarter")["cnt_daily"].sum().reset_index()
    return quarterly_data

def create_temp_usage(df):
    temp_usage = df.groupby('temp_hourly')['cnt_hourly'].sum().reset_index()
    most_popular_temp = temp_usage.loc[temp_usage['cnt_hourly'].idxmax()]
    return temp_usage, most_popular_temp

def create_rfm_df(df):
    rfm_df = df.groupby('dteday').agg(
        Recency=('dteday', lambda x: (df['dteday'].max() - x.max()).days),
        Frequency=('dteday', 'count'),
        Monetary=('cnt_daily', 'sum')
    )

    rfm_df['R_Score'] = pd.qcut(rfm_df['Recency'], q=4, labels=[4, 3, 2, 1])
    rfm_df['F_Score'] = pd.cut(rfm_df['Frequency'], bins=4, labels=[1, 2, 3, 4], duplicates='drop')
    rfm_df['M_Score'] = pd.qcut(rfm_df['Monetary'], q=4, labels=[1, 2, 3, 4])

    rfm_df['rfm_Segment'] = rfm_df['R_Score'].astype(str) + rfm_df['F_Score'].astype(str) + rfm_df['M_Score'].astype(
        str)
    rfm_df['rfm_Score'] = rfm_df[['R_Score', 'F_Score', 'M_Score']].sum(axis=1)

    segments = {
        (4, 4, 4): 'Peak Days',
        (4, 4, 3): 'High Usage Days',
        (3, 4, 4): 'Growing Usage',
        (2, 4, 4): 'Stable Usage',
        (1, 3, 3): 'Declining Usage',
        (1, 1, 1): 'Low Usage Days'
    }
    rfm_df['Segment'] = rfm_df[['R_Score', 'F_Score', 'M_Score']].apply(
        lambda row: segments.get(tuple(row), 'Others'), axis=1
    )
    return rfm_df

# Menyiapkan Data Frame
main_df = pd.read_csv("main_data.csv")

# Memastikan dteday bertipe data datetime dan mengurutkan untuk filter
main_df.sort_values(by="dteday", inplace=True)
main_df.reset_index(inplace=True)
main_df["dteday"] = pd.to_datetime(main_df["dteday"])

# Membuat komponen filter
min_date = main_df["dteday"].min()
max_date = main_df["dteday"].max()
main_df["Quarter"] = main_df["dteday"].dt.to_period("Q")

with st.sidebar:
    # Menambahkan logo
    st.image("https://bikeshare.metro.net/wp-content/uploads/2016/04/cropped-metro-bike-share-favicon.png")

    # Mengambil start_date dan end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Data Frame untuk ditampilkan dengan filter range waktu
filter_main_df = main_df[(main_df["dteday"] >= str(start_date)) & (main_df["dteday"] <= str(end_date))]
quarterly_df = create_quarterly_df(filter_main_df)
temp_usage_df, most_popular_temp = create_temp_usage(filter_main_df)
rfm_df = create_rfm_df(filter_main_df)

# Melengkapi dashboard dengan berbagai visualisasi data
st.header('Bike Sharing Dashboard :bike:')

# Visualisasi Line Chart
st.subheader('Tren Penyewaan Sepeda per Kuartal')
fig, ax = plt.subplots(figsize=(12, 6))
sns.lineplot(x=quarterly_df["Quarter"].astype(str), y=quarterly_df["cnt_daily"], marker="o", ax=ax)
ax.set_title("Total Penyewaan Sepeda per Kuartal", fontsize=16)
ax.set_xlabel("Kuartal", fontsize=14)
ax.set_ylabel("Total Penyewaan", fontsize=14)
plt.xticks(rotation=45)
st.pyplot(fig)
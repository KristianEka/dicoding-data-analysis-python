# Import Library
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

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

# Pertanyaan 1: Bagaimana tren penggunaan sepeda dari tahun 2011 ke 2012?
st.subheader('Tren Penyewaan Sepeda')

fig, ax = plt.subplots(figsize=(12, 6))
sns.lineplot(
    x=quarterly_df["Quarter"].astype(str),
    y=quarterly_df["cnt_daily"],
    marker="o",
    estimator=sum,
    ax=ax
)
ax.set_title("Total Penyewaan Sepeda per Kuartal", fontsize=16)
ax.set_xlabel("Kuartal", fontsize=14)
ax.set_ylabel("Total Penyewaan", fontsize=14)
plt.xticks(rotation=45, fontsize=14)
st.pyplot(fig)

## Pertanyaan 2: Bagaimana pola pengunaan sepeda berdasarkan musin (spring, summer, fall, winter)?
st.subheader('Pola Penggunaan Sepeda')

col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.barplot(
        x="season_daily",
        y="cnt_daily",
        data=filter_main_df,
        estimator=np.mean,
        palette="coolwarm"
    )
    ax.set_title("Bike Rentals per Season")
    ax.set_xlabel("Season")
    ax.set_ylabel("Average Rentals")
    st.pyplot(fig)

# Pertanyaan 3: Apakah ada pola khusus dalam penggunaan sepeda berdasarkan hari dalam seminggu (weekday vs weekend)?
with col2:
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.barplot(
        x="weekday_hourly",
        y="cnt_hourly",
        data=filter_main_df,
        estimator=np.mean,
        palette="viridis"
    )
    plt.xticks(ticks=[0, 1, 2, 3, 4, 5, 6], labels=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
    ax.set_xlabel("Day of the Week")
    ax.set_ylabel("Average Rentals")
    ax.set_title("Bike Rentals per Week")
    st.pyplot(fig)

# Pertanyaan 4: Faktor apa yang paling berpengaruh dalam meningkatkan jumlah pendafataran pengguna (registered users)?
st.subheader('Faktor yang Mempengaruhi Pendaftaran Pengguna')

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(25, 10))

sns.heatmap(
    filter_main_df[["temp_daily", "hum_daily", "windspeed_daily", "registered_daily"]].corr(),
    annot=True,
    cmap="coolwarm",
    ax=ax[0]
)
ax[0].set_title("Correlation Heatmap for Registered Users")

sns.lineplot(
    x='temp_hourly',
    y='cnt_hourly',
    data=temp_usage_df,
    marker='o',
    color='b'
)
plt.axvline(
    most_popular_temp['temp_hourly'],
    color='r',
    linestyle='--',
    label=f"Peak Usage Temp: {most_popular_temp['temp_hourly']:.2f}"
)
ax[1].set_xlabel("Temperature (Normalized)")
ax[1].set_ylabel("Total Bike Users")
ax[1].set_title("Temperature vs Bike Usage")
plt.legend()

st.pyplot(fig)

# Pertanyaan 5: Seberapa besar korelasi antara kelembaban udara dengan jumlah pinjaman sepeda?
# Pertanyaan 6: Jam berapa penggunaan sepeda paling tinggi?

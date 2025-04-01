# Import Library
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

sns.set_style(style='dark')


# Helper Function
def create_monthly_df(df):
    monthly_data = df.groupby("month")["cnt_daily"].sum().reset_index()
    return monthly_data


def create_temp_usage(df):
    t_min = -8  # Suhu minimum dalam dataset
    t_max = 39  # Suhu maksimum dalam dataset

    # Mengelompokkan data berdasarkan suhu yang telah dinormalisasi
    temp_usage = df.groupby('temp_hourly')['cnt_hourly'].sum().reset_index()

    # Konversi suhu dari skala normalisasi ke skala asli
    temp_usage['temp_original'] = temp_usage['temp_hourly'] * (t_max - t_min) + t_min

    # Mencari suhu dengan jumlah penggunaan sepeda tertinggi
    popular_temp = temp_usage.loc[temp_usage['cnt_hourly'].idxmax()]

    return temp_usage, popular_temp


def create_rfm_df(df):
    _rfm_df = df.groupby('dteday').agg(
        Recency=('dteday', lambda x: (df['dteday'].max() - x.max()).days),
        Frequency=('dteday', 'count'),
        Monetary=('cnt_daily', 'sum')
    )

    _rfm_df['R_Score'] = pd.qcut(_rfm_df['Recency'], q=4, labels=[4, 3, 2, 1])
    _rfm_df['F_Score'] = pd.cut(_rfm_df['Frequency'], bins=4, labels=[1, 2, 3, 4], duplicates='drop')
    _rfm_df['M_Score'] = pd.qcut(_rfm_df['Monetary'], q=4, labels=[1, 2, 3, 4])

    _rfm_df['rfm_Segment'] = _rfm_df['R_Score'].astype(str) + _rfm_df['F_Score'].astype(str) + _rfm_df[
        'M_Score'].astype(
        str)
    _rfm_df['rfm_Score'] = _rfm_df[['R_Score', 'F_Score', 'M_Score']].sum(axis=1)

    segments = {
        (4, 4, 4): 'Peak Days',
        (4, 4, 3): 'High Usage Days',
        (3, 4, 4): 'Growing Usage',
        (2, 4, 4): 'Stable Usage',
        (1, 3, 3): 'Declining Usage',
        (1, 1, 1): 'Low Usage Days'
    }
    _rfm_df['Segment'] = _rfm_df[['R_Score', 'F_Score', 'M_Score']].apply(
        lambda row: segments.get(tuple(row), 'Others'), axis=1
    )
    return _rfm_df


# Menyiapkan Data Frame
main_df = pd.read_csv("main_data.csv")

# Memastikan dteday bertipe data datetime dan mengurutkan untuk filter
main_df.sort_values(by="dteday", inplace=True)
main_df.reset_index(inplace=True)
main_df["dteday"] = pd.to_datetime(main_df["dteday"])

# Membuat komponen filter
min_date = main_df["dteday"].min()
max_date = main_df["dteday"].max()
main_df["month"] = main_df["dteday"].dt.month

with st.sidebar:
    # Menambahkan logo
    st.image("https://bikeshare.metro.net/wp-content/uploads/2016/04/cropped-metro-bike-share-favicon.png")

    st.title('Bike Sharing Data Analysis')

    # Mengambil start_date dan end_date dari date_input
    start_date, end_date = st.date_input(
        label='Time Span',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Data Frame untuk ditampilkan dengan filter range waktu
filter_main_df = main_df[(main_df["dteday"] >= str(start_date)) & (main_df["dteday"] <= str(end_date))]
monthly_df = create_monthly_df(filter_main_df)
temp_usage_df, most_popular_temp = create_temp_usage(filter_main_df)
rfm_df = create_rfm_df(filter_main_df)

# Melengkapi dashboard dengan berbagai visualisasi data
st.header('Bike Sharing Dashboard :bike:')

# Pertanyaan 1: Bagaimana tren penggunaan sepeda dari tahun 2011 ke 2012?
st.subheader('Bike Rental Trend')

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Rentals", value=filter_main_df["cnt_daily"].sum())

with col2:
    st.metric("Total Rentals (Registered Users)", value=filter_main_df["registered_daily"].sum())

with col3:
    st.metric("Total Rentals (Casual Users)", value=filter_main_df["casual_daily"].sum())

fig, ax = plt.subplots(figsize=(12, 6))
sns.lineplot(
    x=monthly_df["month"].astype(str),
    y=monthly_df["cnt_daily"],
    marker="o",
    estimator=sum,
    ax=ax
)
ax.set_title("Total Bike Rentals per Month", fontsize=16)
ax.set_xlabel("Month", fontsize=14)
ax.set_ylabel("Total Rentals", fontsize=14)
plt.xticks(
    fontsize=14,
    ticks=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
    labels=["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
)
st.pyplot(fig)

## Pertanyaan 2: Bagaimana pola pengunaan sepeda berdasarkan musin (spring, summer, fall, winter)?
st.subheader('Bike Rentals Pattern by Season and Week')

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
st.subheader('Factors Influencing Registered Users')

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(25, 10))
sns.heatmap(
    filter_main_df[["temp_daily", "hum_daily", "windspeed_daily", "registered_daily"]].corr(),
    annot=True,
    cmap="coolwarm",
    ax=ax[0]
)
ax[0].set_title("Correlation Heatmap for Registered Users")

sns.lineplot(
    x='temp_original',
    y='cnt_hourly',
    data=temp_usage_df,
    marker='o',
    color='b',
    ax=ax[1]
)

# Menambahkan garis vertikal untuk suhu dengan penggunaan tertinggi
plt.axvline(
    most_popular_temp['temp_original'],
    color='r',
    linestyle='--',
    label=f"Peak Usage Temp: {most_popular_temp['temp_original']:.2f}°C"
)
ax[1].set_xlabel("Temperature (°C)")
ax[1].set_ylabel("Total Bike Users")
ax[1].set_title("Temperature vs Bike Usage")
plt.legend()

st.pyplot(fig)

# Pertanyaan 5: Seberapa besar korelasi antara kelembaban udara dengan jumlah pinjaman sepeda?
st.subheader('Correlation between Humidity and Bike Rentals')

fig, ax = plt.subplots(figsize=(8, 5))
sns.scatterplot(
    x="hum_daily",
    y="cnt_daily",
    data=filter_main_df,
    alpha=0.5
)
ax.set_title("Humidity vs Bike Rentals")
ax.set_xlabel("Humidity")
ax.set_ylabel("Total Rentals")
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
st.pyplot(fig)

# Pertanyaan 6: Jam berapa penggunaan sepeda paling tinggi?
st.subheader('Bike Rentals by Hour of the Day')

col1, col2 = st.columns(2)
with col1:
    st.metric("Peak Hour", value=filter_main_df["hr"].mode()[0])

with col2:
    st.metric("Total Rentals at Peak Hour",
              value=filter_main_df[filter_main_df["hr"] == filter_main_df["hr"].mode()[0]]["cnt_hourly"].sum())

col1, col2 = st.columns(2)
with col1:
    st.metric("Lowest Hour", value=filter_main_df["hr"].min())

with col2:
    st.metric("Total Rentals at Lowest Hour",
              value=filter_main_df[filter_main_df["hr"] == filter_main_df["hr"].min()]["cnt_hourly"].sum())

fig, ax = plt.subplots(figsize=(12, 8))
sns.lineplot(
    x="hr",
    y="cnt_hourly",
    data=filter_main_df,
    estimator=np.mean,
    marker="o",
    color="b"
)
ax.set_title("Bike Rentals per Hour")
ax.set_xlabel("Hour of the Day")
ax.set_ylabel("Total Rentals")
plt.xticks(range(0, 24), fontsize=12)
plt.yticks(fontsize=12)
plt.grid()
st.pyplot(fig)

# RFM Analysis
st.subheader("Best Customer Based on RFM Parameters")

col1, col2, col3 = st.columns(3)

with col1:
    avg_recency = round(rfm_df["Recency"].mean(), 2)
    st.metric("Average Rencency", value=avg_recency)

with col2:
    avg_frequency = round(rfm_df["Frequency"].mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)

with col3:
    avg_monetary = round(rfm_df["Monetary"].mean(), 2)
    st.metric("Average Monetary", value=avg_monetary)

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]
sns.barplot(
    y="Recency",
    x="dteday",
    data=rfm_df.sort_values(by="Recency", ascending=True).head(5),
    palette=colors,
    ax=ax[0]
)
ax[0].set_ylabel(None)
ax[0].set_xlabel("dteday", fontsize=30)
ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=35)
ax[0].set_xticklabels(ax[0].get_xticklabels(), rotation=45, ha='right')
sns.barplot(
    y="Frequency",
    x="dteday",
    data=rfm_df.sort_values(by="Frequency", ascending=False).head(5),
    palette=colors,
    ax=ax[1]
)
ax[1].set_ylabel(None)
ax[1].set_xlabel("dteday", fontsize=30)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=35)
ax[1].set_xticklabels(ax[1].get_xticklabels(), rotation=45, ha='right')
sns.barplot(
    y="Monetary",
    x="dteday",
    data=rfm_df.sort_values(by="Monetary", ascending=False).head(5),
    palette=colors,
    ax=ax[2]
)
ax[2].set_ylabel(None)
ax[2].set_xlabel("dteday", fontsize=30)
ax[2].set_title("By Monetary", loc="center", fontsize=50)
ax[2].tick_params(axis='y', labelsize=30)
ax[2].tick_params(axis='x', labelsize=35)
ax[2].set_xticklabels(ax[2].get_xticklabels(), rotation=45, ha='right')

st.pyplot(fig)

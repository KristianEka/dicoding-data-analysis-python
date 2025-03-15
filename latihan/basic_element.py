import streamlit as st
import pandas as pd

## Basic Element
# Write
st.write(
    """
    # My first app
    Hallo, para calon praktisi data masa depan!
    Ini adalah write
    """
)

st.write(pd.DataFrame({
    'ct1': [1, 2, 3, 4],
    'c2': [10, 20, 30, 40],
}))

# Text
st.markdown(
    """
    # My first app
    Hallo, para calon praktisi data masa depan!
    Ini adalah Markdown
    """
)

st.title('Ini adalah Title')

st.header('Ini adalah Header')

st.subheader('Ini adalah subHeader')

st.caption('Copyright (c) 2023')

code = """def(hello):
    print("Hello, Streamlit!")"""
st.code(code, language='python')

st.text('Ini adalah text')

st.latex(r"""
    \sum_{k=0}^{n-1} ar^k =
    a \left(\frac{1-r^{n}}{1-r}\right)
""")


# Data Display
df = pd.DataFrame({
    'c1': [1, 2, 3, 4],
    'c2': [10, 20, 30, 40],
})

st.dataframe(data=df, width=500, height=150)

st.table(data=df)

st.metric(label="Temperature", value="28 °C", delta="1.2 °C")

st.json({
    'c1': [1, 2, 3, 4],
    'c2': [10, 20, 30, 40]
})

# Chart

import numpy as np
import matplotlib.pyplot as plt

x = np.random.normal(15, 5, 250)

fig, ax = plt.subplots()
ax.hist(x=x, bins=15)
st.pyplot(fig)

## Basic Widgets

# Text input
name = st.text_input(label='Nama Lengkap', value='',)
st.write('Nama: ', name)

# Text-area
text = st.text_area('Feedback')
st.write('Feedback: ', text)

# Number input
number = st.number_input(label='Umur')
st.write('Umur: ', int(number), ' tahun')

# Date input
import datetime
date = st.date_input(label='Tanggal lahir', min_value=datetime.date(1900, 1, 1))
st.write('Tanggil lahie: ', date)

# File uploader
uploaded_file = st.file_uploader('Choose a CSV file')

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.dataframe(df)

# Camera input
enable = st.checkbox("Enable camera")
picture = st.camera_input('Take a picture', disabled=not enable)
if picture:
    st.image(picture)
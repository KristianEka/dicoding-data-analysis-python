import streamlit as st
## Button Widgets

# Button
if st.button('Say hello'):
    st.write('Hello there')

# Checkbox
agree = st.checkbox('I agree')

if agree:
    st.write('Welcome to MyApp')

# Radio button
genre = st.radio(
    label="What's your favorite movie genre",
    options=('Comedy', 'Drama', 'Documentary'),
    horizontal=False
)

# Select Box
genreS = st.selectbox(
    label="What's your favorite movie genre",
    options=('Comedy', 'Drama', 'Documentary'),
)

# Multiselect
genreM = st.multiselect(
    label="What's your favorite movie genre",
    options=('Comedy', 'Drama', 'Documentary'),
)

# Slider
values = st.slider(
    label='Select a range of values',
    min_value=0, max_value=100, value=(0, 100)
)
st.write('Values', values)
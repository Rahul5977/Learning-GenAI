import streamlit as st
import datetime

st.title("Chai maker app")

if st.button("Make chai"):
    st.success("Chai reddy")
    
add_masala=st.checkbox("Add masala")
if add_masala:
    st.write("Masala added")
    
tea_type=st.radio("Tea type",["Milk","Water","Almond Milk"])\

st.write(f"Selected base: {tea_type}")

flavour=st.selectbox("Choose flavour:",["Adrak tea","Kesar tea","Lemon tea"])
st.write(f"Selected flavour: {flavour}")

sugar=st.slider("Sugar level: ",0,5,2)

cups=st.number_input("How many cups: ",min_value=1,max_value=10)

st.write(f"Selected cups: {cups}")

dob=dob=st.date_input("Enter dob :",min_value=datetime.date(2000, 1, 1))
st.write(f"Your date of birth :{dob}")

year=dob.year - datetime.datetime.now().year 

st.write(f"Your age :{year} years")

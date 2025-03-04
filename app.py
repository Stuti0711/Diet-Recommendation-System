import streamlit as st
import pandas as pd
import numpy as np
from helper_functions import calculate_bmi_category, recommend_foods

# Streamlit UI
st.title("🥗 Diet Recommendation System")

# User Inputs
weight = st.number_input("Weight (kg):", min_value=30.0, max_value=200.0, value=70.0)
height = st.number_input("Height (cm):", min_value=100.0, max_value=250.0, value=170.0)

if st.button("Get Recommendation"):
    # BMI Calculation
    bmi_category = calculate_bmi_category(weight, height)  # Expecting a single return value

    st.write(f"### Your BMI: {weight / ((height / 100) ** 2):.2f} ({bmi_category})")

    # Recommend Food and Display Nutritional Info
    recommended_foods = recommend_foods(bmi_category)

    st.subheader("Recommended Foods 🍽️")

    if recommended_foods.empty:
        st.warning("No food recommendations available for this category.")
    else:
        for _, row in recommended_foods.iterrows():
            st.write(f"**{row['Food_items']}** (Type: {row['Food_Type']})")
            st.write(f"- **Calories**: {row['Calories']} kcal")
            st.write(f"- **Protein**: {row['Protein']} g")
            st.write(f"- **Carbs**: {row['Carbs']} g")
            st.write(f"- **Fat**: {row['Fat']} g")
            st.write("---")

    st.success("Enjoy your healthy diet! 😊")

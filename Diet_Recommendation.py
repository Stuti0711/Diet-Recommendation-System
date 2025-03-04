import pandas as pd
import numpy as np
import streamlit as st
import google.generativeai as genai

# 🔹 Configure Google Gemini AI
genai.configure(api_key="AIzaSyAF8Rvell5l6qaoTuCwEw1TqqCM_4uxuKs")

# 🔹 Load datasets
food_data = pd.read_csv('food.csv')
nutrition_data = pd.read_csv('nutrition_distriution.csv')

# 🔹 Replace 'null' with NaN
food_data.replace('null', np.nan, inplace=True)
nutrition_data.replace('null', np.nan, inplace=True)

# 🔹 Standardizing column names
food_data.columns = food_data.columns.str.strip().str.replace(' ', '_')
nutrition_data.columns = nutrition_data.columns.str.strip().str.replace(' ', '_')

# 🔹 Merge datasets
columns_to_merge_on = ['Calories', 'Fats', 'Proteins', 'Iron', 'Calcium', 'Sodium', 'Potassium', 'Carbohydrates', 'Fibre', 'VitaminD', 'Sugars']
merged_data = pd.merge(food_data, nutrition_data, on=columns_to_merge_on, how='outer')
merged_data.fillna("Data Not Available", inplace=True)

# 🔹 Assign meal categories
if 'Meal_Type' not in merged_data.columns:
    def assign_meal_type(food_item):
        food_item = food_item.lower()
        if any(word in food_item for word in ['oats', 'pancake', 'toast', 'egg', 'smoothie', 'yogurt', 'fruit', 'cereal']):
            return 'Breakfast'
        elif any(word in food_item for word in ['salad', 'rice', 'chicken', 'fish', 'pasta', 'soup', 'sandwich']):
            return 'Lunch'
        elif any(word in food_item for word in ['dinner', 'grill', 'steak', 'roast', 'lentil', 'stew', 'curry']):
            return 'Dinner'
        else:
            return 'Anytime Snack'
    
    merged_data['Meal_Type'] = merged_data['Food_items'].apply(assign_meal_type)

# 🔹 Assign Veg/Non-Veg category
if 'Category' not in merged_data.columns:
    def assign_veg_nonveg(food_item):
        food_item = food_item.lower()
        if any(word in food_item for word in ['chicken', 'fish', 'beef', 'mutton', 'egg', 'prawn']):
            return 'Non-Veg'
        else:
            return 'Veg'
    
    merged_data['Category'] = merged_data['Food_items'].apply(assign_veg_nonveg)


# 🎨 **Streamlit UI**
st.title("🥗 Diet Recommendation System")


# Gender selection (Default = "Select an option")
gender = st.selectbox("Select Gender:", ["Select gender", "Male", "Female"], index=0, key="gender")


# Weight input (No default value)
weight = st.number_input("Enter Weight (kg):", min_value=25.0, max_value=200.0, value=None, key="weight", placeholder="Enter weight")

# Height input with unit selection
height_unit = st.selectbox("Select Height Unit:", ["Select Unit","Centimeters", "Feet & Inches"], key="height_unit")

if height_unit in ["Centimeters", "Select Unit"]:
    height = st.number_input("Enter Height (cm):", min_value=50.0, max_value=250.0, value=None, key="height_cm", placeholder="Enter height")
else:
    height_feet = st.number_input("Feet:", min_value=1, max_value=8, value=None, key="height_feet", placeholder="Feet")
    height_inches = st.number_input("Inches:", min_value=0, max_value=11, value=None, key="height_inches", placeholder="Inches")
    height = (height_feet * 30.48) + (height_inches * 2.54) if height_feet and height_inches else None
# Food preference selection (Default = "Select an option")
food_pref = st.radio("Food Preference:", [ "Veg", "Non-Veg"], index=0, key="food_pref")


# 🔹 Function to calculate BMI category
def calculate_bmi_category(bmi, gender):
    if gender == "Male":
        if bmi < 17:
            return "Severely Underweight"
        elif 17 <= bmi < 20:
            return "Underweight"
        elif 20 <= bmi < 26:
            return "Healthy"
        elif 26 <= bmi < 31:
            return "Overweight"
        elif 31 <= bmi < 36:
            return "Obese Class I"
        elif 36 <= bmi < 41:
            return "Obese Class II"
        else:
            return "Obese Class III"

    elif gender == "Female":
        if bmi < 16:
            return "Severely Underweight"
        elif 16 <= bmi < 19:
            return "Underweight"
        elif 19 <= bmi < 25:
            return "Healthy"
        elif 25 <= bmi < 30:
            return "Overweight"
        elif 30 <= bmi < 35:
            return "Obese Class I"
        elif 35 <= bmi < 40:
            return "Obese Class II"
        else:
            return "Obese Class III"

# 🟢 **Button to get recommendation**
if st.button("Get Recommendation"):
    if gender == "Select an option" or food_pref == "Select an option":
        st.warning("⚠️ Please select your Gender and Food Preference before proceeding!")
    elif height is None or weight is None:
        st.error("⚠️ Please enter a valid height and weight!")
    else:
        # Calculate BMI
        bmi = weight / ((height / 100) ** 2)
        bmi_category = calculate_bmi_category(bmi, gender)

        # 🟢 Display BMI Category with color-coding
        if bmi_category in ["Severely Underweight", "Obese Class III"]:
            st.error(f"### Your BMI: {bmi:.2f} ({bmi_category}) ⚠️ Consult a nutritionist.")
        elif bmi_category == "Healthy":
            st.success(f"### Your BMI: {bmi:.2f} ({bmi_category}) ✅ Keep up the good work!")
        else:
            st.warning(f"### Your BMI: {bmi:.2f} ({bmi_category}) ⚠️ Consider adjustments.")

        # 🔹 Filter Food Recommendations
        for meal in ["Breakfast", "Lunch", "Dinner"]:
            st.subheader(f"🍽 {meal} Recommendations")
            meal_data = merged_data[(merged_data['Meal_Type'] == meal) & (merged_data['Category'] == food_pref)]
            if not meal_data.empty:
                st.table(meal_data.sample(n=min(3, len(meal_data))).reset_index(drop=True)[['Food_items', 'Calories', 'Fats', 'Proteins', 'Carbohydrates']])
            else:
                st.warning(f"No recommendations found for {meal} with your selected preference.")



# 🔮 **Gemini AI-Generated Meal Plan**
def get_gemini_recommendation(prompt):
    model = genai.GenerativeModel("gemini-1.5-pro")  # Load Gemini model
    response = model.generate_content(prompt)
    return response.text if hasattr(response, "text") else response.candidates[0]['content']

# 🟢 AI-Powered Meal Plan Button

import streamlit as st

# Center AI Avatar and Make it Clickable
st.markdown(
    """
    <style>
    .centered-container {
        display: flex;
        justify-content: center;
        align-items: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="centered-container">', unsafe_allow_html=True)

# Load AI Avatar Image (Replace 'ai_avatar.png' with your image path)
ai_avatar_path = "ai_avatar.png"  # Ensure this image is in the same directory

if st.button("🔮 Generate AI Meal Plan"):  # Hidden text-based trigger
    st.subheader("🤖 Your AI Diet Planner is Generating...")

st.markdown(
    f'<a href="#" onclick="document.querySelector(\'button\').click();">'
    f'<img src="{ai_avatar_path}" width="120"></a>',
    unsafe_allow_html=True
)

st.markdown("</div>", unsafe_allow_html=True)




if st.button("Click here"):
    if gender == "Select an option" or food_pref == "Select an option":
        st.warning("⚠️ Please select your Gender and Food Preference before proceeding!")
    else:
        st.subheader("🥗 Your AI-Generated Meal Plan")

        prompt = f"""
        I am a {gender} with a weight of {weight} kg and height of {height} cm.
        My BMI is {weight / ((height / 100) ** 2):.2f}, and I am categorized as {calculate_bmi_category(weight / ((height / 100) ** 2), gender)}.
        I prefer {food_pref} food.
        Suggest a meal plan with breakfast, lunch, and dinner that matches my dietary needs.
        """

        gemini_meal_plan = get_gemini_recommendation(prompt)
        st.write(gemini_meal_plan)


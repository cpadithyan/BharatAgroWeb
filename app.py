import streamlit as st
import pickle 
import numpy as np 
from sklearn.ensemble import RandomForestClassifier  # Import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import os 

# Load machine learning models
models_dir = 'Models'
Model_crop_path = os.path.join(models_dir, 'NBClassifier.pkl')
Model_fertilizer_path = os.path.join(models_dir, 'RandomForest.pkl')
Model_location_path = os.path.join(models_dir , 'DecisionTree.pkl')

Model_crop = pickle.load(open(Model_crop_path, 'rb'))
Model_fertilizer = pickle.load(open(Model_fertilizer_path, 'rb'))  # Load as RandomForestClassifier
Model_location =  pickle.load(open(Model_location_path , 'rb'))

# Define encoding functions
def encode_soil_types(original_soil_types, new_soil_type):
    soil_type_label_encoder = LabelEncoder().fit(original_soil_types)
    encoded_soil_type = soil_type_label_encoder.transform([new_soil_type])
    return encoded_soil_type[0]

def encode_crop_types(original_crop_types, new_crop_type):
    crop_type_label_encoder = LabelEncoder().fit(original_crop_types)
    encoded_crop_type = crop_type_label_encoder.transform([new_crop_type])
    return encoded_crop_type[0]

encoded_fertilizers = {
    0: '10-26-26', 1: '14-35-14', 2: '17-17-17', 3: '20-20', 4: '28-28', 5: 'DAP', 6: 'Urea'
}
def get_fertilizer_name(encoded_value):
    return encoded_fertilizers.get(encoded_value, 'Unknown')

def get_main_crop(state_name):
    crops_mapping = {
        "Andhra Pradesh": "Rice",
        "Arunachal Pradesh": "Oranges",
        "Assam": "Tea",
        "Bihar": "Rice",
        "Chhattisgarh": "Rice",
        "Goa": "Coconut",
        "Gujarat": "Cotton",
        "Haryana": "Wheat",
        "Himachal Pradesh": "Apple",
        "Jharkhand": "Rice",
        "Karnataka": "Sugarcane",
        "Kerala": "Rubber",
        "Madhya Pradesh": "Wheat",
        "Maharashtra": "Sugarcane",
        "Manipur": "Rice",
        "Meghalaya": "Maize",
        "Mizoram": "Maize",
        "Nagaland": "Maize",
        "Odisha": "Rice",
        "Punjab": "Wheat",
        "Rajasthan": "Wheat",
        "Sikkim": "Maize",
        "Tamil Nadu": "Rice",
        "Telangana": "Rice",
        "Tripura": "Rice",
        "Uttar Pradesh": "Sugarcane",
        "Uttarakhand": "Rice",
        "West Bengal": "Rice"
    }
    
    state_name = state_name.title()
    
    if state_name in crops_mapping:
        return crops_mapping[state_name]
    else:
        return "Crop data not available for this state."

def main():
    # Set background color
    st.set_page_config(layout="wide", page_title="Crop Prediction App", page_icon=":seedling:", initial_sidebar_state="expanded")

    # Define background color
    st.markdown(
        """
        <style>
        .reportview-container {
            background: url("static/image.png");
            background-size: cover;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title('Barat Agro App')
    page = st.sidebar.radio('Navigation', ['Home', 'Crop Prediction', 'Fertilizer Prediction', 'Crop Location'])

    if page == 'Home':
        st.write('Welcome to the BharatAgro App. Use the sidebar to navigate.')
        st.image("static/image.png", use_column_width=True)

    elif page == 'Crop Prediction':
        st.subheader('Crop Prediction Based on your soil reports')
        st.write('Fill in the details below to predict the best crop to be cultivated.')
        

        with st.form(key='crop_prediction_form'):
            N = st.slider('Nitrogen', min_value=0.0, max_value=100.0, step=1.0)
            P = st.slider('Phosporus', min_value=0.0, max_value=100.0, step=1.0)
            K = st.slider('Potassium', min_value=0.0, max_value=100.0, step=1.0)
            temp = st.slider('Temperature', min_value=0.0, max_value=100.0, step=1.0)
            humidity = st.slider('Humidity', min_value=0.0, max_value=100.0, step=1.0)
            ph = st.slider('Ph', min_value=0.0, max_value=14.0, step=0.1)
            rainfall = st.slider('Rainfall', min_value=0.0, max_value=100.0, step=1.0)

            submitted = st.form_submit_button('Predict Crop')

            if submitted:
                features = np.array([[N, P, K, temp, humidity, ph, rainfall]])
                prediction = Model_crop.predict(features)
                crop = prediction[0]
                st.success(f"The best crop to be cultivated there is {crop}.")

    elif page == 'Fertilizer Prediction':
        st.subheader('Fertilizer Prediction Based on your soil reports')
        st.write('Fill in the details below to predict the best fertilizer to use in the field.')

        with st.form(key='fertilizer_prediction_form'):
            Temperature = st.slider('Temperature', min_value=0.0, max_value=100.0, step=1.0)
            Humidity = st.slider('Humidity', min_value=0.0, max_value=100.0, step=1.0)
            Soil_Moisture = st.slider('Soil Moisture', min_value=0.0, max_value=100.0, step=1.0)
            SoilType = st.selectbox('Soil Type', ['Sandy', 'Loamy', 'Black', 'Red', 'Clayey'])
            Crop_type = st.selectbox('Crop Type', ['Maize', 'Sugarcane', 'Cotton', 'Tobacco', 'Paddy', 'Barley',
                                                    'Wheat', 'Millets', 'Oil seeds', 'Pulses', 'Ground Nuts'])
            N = st.slider('Nitrogen', min_value=0.0, max_value=100.0, step=1.0)
            P = st.slider('Phosphorous', min_value=0.0, max_value=100.0, step=1.0)
            K = st.slider('Potassium', min_value=0.0, max_value=100.0, step=1.0)

            submitted = st.form_submit_button('Predict Fertilizer')

            if submitted:
                encoded_soil_type = encode_soil_types(['Sandy', 'Loamy', 'Black', 'Red', 'Clayey'], SoilType)
                encoded_crop_type = encode_crop_types(['Maize', 'Sugarcane', 'Cotton', 'Tobacco', 'Paddy', 'Barley',
                                                        'Wheat', 'Millets', 'Oil seeds', 'Pulses', 'Ground Nuts'], Crop_type)

                features = np.array([[Temperature, Humidity, Soil_Moisture, encoded_soil_type, encoded_crop_type, N, P, K]])
                prediction = Model_fertilizer.predict(features)
                P_fertilizer = get_fertilizer_name(prediction[0])
                st.success(f"The best fertilizer to use in the field is {P_fertilizer}.")

    elif page == 'Crop Location':
        st.subheader('Based on your Location you are able to predict the Crop name')
        st.write('Enter the details below to find the best crop to be cultivated in that location.')

        with st.form(key='crop_location_form'):
            state_name = st.text_input('State Name')
            district_name = st.text_input('District Name')
            season = st.text_input('Season')

            submitted = st.form_submit_button('Find Crop')

            if submitted:
                production = get_main_crop(state_name)
                st.success(f"The best crop to be cultivated there is {production}.")

if __name__ == '__main__':
    main()

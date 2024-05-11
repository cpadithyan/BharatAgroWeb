from flask import Flask, render_template, redirect, url_for, request , session
import pickle 
import numpy as np 
from sklearn.preprocessing import LabelEncoder
import os 
import secrets

app = Flask(__name__)

if 'SECRET_KEY' in os.environ:
    app.secret_key = os.environ['SECRET_KEY']
else:
    app.secret_key = secrets.token_hex(16)
# Define the path to the models directory
models_dir = os.path.join(app.root_path, 'Models')

# Load machine learning models
Model_crop_path = os.path.join(models_dir, 'NBClassifier.pkl')
Model_fertilizer_path = os.path.join(models_dir, 'RandomForest.pkl')
Model_location_path = os.path.join(models_dir , 'DecisionTree.pkl')

# Load machine learning models
Model_crop = pickle.load(open(Model_crop_path, 'rb'))
Model_fertilizer = pickle.load(open(Model_fertilizer_path, 'rb'))
Model_location =  pickle.load(open(Model_location_path , 'rb'))


# Define routes
@app.route('/')
def index():
    return render_template('test.html')

@app.route('/redirect_to_page1')
def redirect_to_page1():
    return redirect(url_for('page1'))
@app.route('/redirect_to_page2')
def redirect_to_page2():

    return redirect(url_for('page2'))

@app.route('/redirect_to_page3')
def redirect_to_page3():
    return redirect(url_for('fertilize'))



@app.route('/predictcrop', methods=['POST'])
def predictcrop():
    if request.method == 'POST':
        # Get form data
        N = float(request.form['Nitrogen'])
        P = float(request.form['Phosporus'])
        K = float(request.form['Potassium'])
        temp = float(request.form['Temperature'])
        humidity = float(request.form['Humidity'])
        ph = float(request.form['Ph'])
        rainfall = float(request.form['Rainfall'])

        # Perform prediction
        features = np.array([[N, P, K, temp, humidity, ph, rainfall]])
        prediction = Model_crop.predict(features)
        crop = prediction[0]

        # Format the result message
        result = "{} is the best crop to be cultivated there.".format(crop)

        # Store the result in session
        session['result'] = result

        # Redirect to page1
        return redirect(url_for('page1'))
    
@app.route('/page1')
def page1():
    # Get the result from session
    result = session.get('result', None)
    # Clear the result from session to avoid showing it again
    session.pop('result', None)
    return render_template('soil.html', result=result)

## Encode the values 
# Define encoding functions outside the route function
def encode_soil_types(original_soil_types, new_soil_type):
    soil_type_label_encoder = LabelEncoder().fit(original_soil_types)
    encoded_soil_type = soil_type_label_encoder.transform([new_soil_type])
    return encoded_soil_type[0]

def encode_crop_types(original_crop_types, new_crop_type):
    crop_type_label_encoder = LabelEncoder().fit(original_crop_types)
    encoded_crop_type = crop_type_label_encoder.transform([new_crop_type])
    return encoded_crop_type[0]

## Encoder Fertilizer name 
encoded_fertilizers = {
    0: '10-26-26', 1: '14-35-14', 2: '17-17-17', 3: '20-20', 4: '28-28', 5: 'DAP', 6: 'Urea'
}
def get_fertilizer_name(encoded_value):
    return encoded_fertilizers.get(encoded_value, 'Unknown')
# Define routes
@app.route('/predictfertilizer', methods=['POST'])
def predictfertilizer():
    try:
        # Get form data
        Temperature = float(request.form['Temperature'])
        Humidity = float(request.form['Humidity'])
        Soil_Moisture = float(request.form['SoilMoisture'])
        SoilType = request.form['soil_type']
        Crop_type = request.form['crop_type']
        N = float(request.form['Nitrogen'])
        P = float(request.form['Phosphorous'])
        K = float(request.form['Potassium'])
        
        # Encode Soil Type and Crop Type
        encoded_soil_type = encode_soil_types(['Sandy', 'Loamy', 'Black', 'Red', 'Clayey'], SoilType)
        encoded_crop_type = encode_crop_types(['Maize', 'Sugarcane', 'Cotton', 'Tobacco', 'Paddy', 'Barley',
                                               'Wheat', 'Millets', 'Oil seeds', 'Pulses', 'Ground Nuts'], Crop_type)

        # Perform prediction
        features = np.array([[Temperature, Humidity, Soil_Moisture, encoded_soil_type, encoded_crop_type, N, P, K]])
        prediction = Model_fertilizer.predict(features)



        P_fertilizer = get_fertilizer_name(prediction[0])

        result = "{} is the best fertilizer to use in the field.".format(P_fertilizer)

        # Store the result in session
        session['result'] = result

        return redirect(url_for('fertilize'))
    except KeyError as e:
        # Handle missing form fields
        return "Error: Missing form field - {}".format(e)
    except ValueError as e:
        # Handle invalid form data
        return "Error: Invalid form data - {}".format(e)
    except Exception as e:
        # Handle other unexpected errors
        return "Error: {}".format(e)


@app.route('/fertilize')
def fertilize():
    # Get the result from session
    result = session.get('result', None)
    # Clear the result from session to avoid showing it again
    session.pop('result', None)
    return render_template('fertilize.html', result=result)

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
    
    # Convert state name to title case for consistency
    state_name = state_name.title()
    
    if state_name in crops_mapping:
        return crops_mapping[state_name]
    else:
        return "Crop data not available for this state."

@app.route('/cropLocation' , methods = ['POST'])
def find_crop_production():
    if request.method == 'POST':
        state_name = request.form['StateName']
        district_name = request.form['DistrictName']
        season = request.form['Season']

        #perform prediction 
       # features = np.array([[state_name , district_name , season]])
        
        #prediction = Model_Location.predict(features)
        prodution = get_main_crop(state_name)

        # Format the result message
        result = "{} is the best crop to be cultivated there.".format(prodution)

        # Store the result in session
        session['result'] = result

        # Redirect to page1
        return redirect(url_for('page2'))

    

@app.route('/page2')
def page2():
     # Get the result from session
    result = session.get('result', None)
    # Clear the result from session to avoid showing it again
    session.pop('result', None)
    return render_template('location.html' , result = result)



if __name__ == '__main__':
    app.run(debug=True)










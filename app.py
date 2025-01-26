from flask import Flask, request, render_template, jsonify, send_from_directory
import pandas as pd
import cv2
import easyocr
import os
import re
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Basic setup
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize OCR
reader = easyocr.Reader(['en'])

# Load and prepare dataset
DATASET_PATH = '/Users/varunsingh/Desktop/Projects/Hackathon MCIT 2025/Python OCR test/NutS/Varun/Final Dataset.csv'
NUTRITION_COLUMNS = ['carbohydrates_100g', 'final_fat', 'fiber_100g', 'proteins_100g', 
                    'Total Vitamin A, C, E', 'sugars_100g']

# Load dataset and clean numeric columns
def load_dataset():
    df = pd.read_csv(DATASET_PATH)
    for col in NUTRITION_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].astype(str).str.split().str[0].replace('-', None), errors='coerce')
    return df

# Load dataset once when app starts
nutrition_data = load_dataset()


def read_receipt(image_path):
    """Get items and quantities from receipt using OCR"""
    text_results = reader.readtext(image_path)
    items = {}
    
    # Look for item names and their quantities
    for i in range(1, len(text_results)):
        current = text_results[i][1]
        previous = text_results[i-1][1]
        
        # If current text is an item name (not a number) and previous text is a quantity
        if not current.replace(".", "").isdigit() and previous.replace(".", "", 1).isdigit():
            items[current.lower()] = int(float(previous))
    
    return items

# Main routes
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Handle receipt upload
        if 'image' in request.files:
            return handle_receipt_upload(request.files['image'])
        # Handle manual entry
        elif 'manual_items' in request.json:
            return handle_manual_entry(request.json['manual_items'])
    return render_template('index.html')

def handle_receipt_upload(file):
    """Process uploaded receipt image"""
    if not file or not allowed_file(file.filename):
        return jsonify({'success': False, 'error': 'Please upload a valid image file'})
    
    try:
        # Save and process the image
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process image and extract items
        #processed_path = process_receipt_image(filepath)
        items = read_receipt(filepath)
        
        # Calculate nutrition
        result = calculate_nutrition(items)
        
        # Clean up files
        os.remove(filepath)
        #os.remove(processed_path)
        
        return result
        
    except Exception as e:
        print(f"Error processing receipt: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to process receipt'})

def handle_manual_entry(items):
    """Process manually entered items"""
    try:
        # Convert all item names to lowercase for case-insensitive matching
        items_dict = {item['name'].lower(): int(item['quantity']) for item in items}
        
        # Print for debugging
        print("Manual items received:", items_dict)
        print("Available products in dataset:", nutrition_data['product_name'].tolist()[:10])  # Show first 10 items
        
        return calculate_nutrition(items_dict)
    except Exception as e:
        print(f"Error processing manual entry: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to process items'})

def calculate_nutrition(items):
    """Calculate nutrition values from items"""
    try:
        # Convert product names in dataset to lowercase for matching
        nutrition_data['product_name_lower'] = nutrition_data['product_name'].str.lower()
        
        # Find matching items in database
        matching_items = nutrition_data[nutrition_data['product_name_lower'].isin(items.keys())].copy()
        
        print("Matching items found:", len(matching_items))  # Debug print
        
        if matching_items.empty:
            print("No matches found in database")  # Debug print
            return jsonify({'success': False, 'error': 'No matching items found'})
        
        # Add quantities and calculate totals
        matching_items['quantity'] = matching_items['product_name_lower'].map(items)
        
        # Calculate nutrition values
        for col in NUTRITION_COLUMNS:
            if col in matching_items.columns:
                matching_items[col] = matching_items[col] * matching_items['quantity']
        
        # Get weekly totals
        totals = matching_items[NUTRITION_COLUMNS].sum()
        weekly_totals = {col: int(val * 4.54) for col, val in totals.items()}
        
        print("Calculated totals:", weekly_totals)  # Debug print
        
        return jsonify({'success': True, 'summary': weekly_totals})
        
    except Exception as e:
        print(f"Error in calculate_nutrition: {str(e)}")
        return jsonify({'success': False, 'error': f'Error calculating nutrition: {str(e)}'})

@app.route('/calculate_goals', methods=['POST'])
def calculate_goals():
    """Calculate weekly nutrition goals based on user info"""
    try:
        data = request.json
        
        # Convert height and weight to metric
        height_cm = ((data['height_feet'] * 12) + data['height_inches']) * 2.54
        weight_kg = data['weight'] * 0.453592
        
        # Calculate BMR (Mifflin-St Jeor Equation)
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * data['age'])
        bmr = bmr + 5 if data['sex'] == 'M' else bmr - 161
        
        # Adjust for activity level
        activity_factors = {
            'sedentary': 1.2,
            'low': 1.375,
            'active': 1.55,
            'very': 1.725
        }
        daily_calories = bmr * activity_factors[data['activity_level']]
        weekly_calories = round(daily_calories * 7)        
        
        # Calculate macronutrients
        daily_protein = weight_kg * 1.2  # 1.2g per kg bodyweight
        weekly_protein = round(daily_protein * 7)
        
        weekly_fat = round((weekly_calories * 0.25) / 9)  # 25% of calories from fat
        weekly_carbs = round((weekly_calories - (weekly_protein * 4) - (weekly_fat * 9)) / 4)
        
        # Calculate fiber goals based on sex
        daily_fiber = 38 if data['sex'] == 'M' else 25  # Men: 38g/day, Women: 25g/day
        weekly_fiber = daily_fiber * 7
        
        results = {
            'calories': weekly_calories,
            'protein': weekly_protein,
            'carbohydrates': weekly_carbs,
            'fat': weekly_fat,
            'fiber': weekly_fiber,
            'daily_calories': daily_calories,
            'daily_protein': daily_protein,
            'daily_carbohydrates': weekly_carbs / 7,
            'daily_fat': weekly_fat / 7,
            'daily_fiber': daily_fiber
        }
        
        return jsonify({'success': True, 'results': results})
        
    except Exception as e:
        print(f"Error calculating goals: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to calculate goals'})

def allowed_file(filename):
    """Check if file type is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(debug=True)
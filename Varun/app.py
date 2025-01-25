
import os
import cv2
import numpy as np
from flask import Flask, request, render_template, redirect, url_for
import easyocr
import pandas as pd

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'])

# Read the filtered dataset outside of the routes, this ensures it's available for use when required
filteredds = pd.read_csv('/Users/varunsingh/Desktop/Projects/Hackathon MCIT 2025/Python OCR test/NutS/Varun/Final Dataset.csv')

# Define columns for summing up
listy = ['fat_100g', 'fiber_100g', 'proteins_100g', 'vitamin-c_100g', 'sugars_100g']

def preprocess_image(image_path):
    """
    Preprocess the image for better OCR results:
    - Convert to grayscale
    - Apply thresholding
    """
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    _, thresh = cv2.threshold(image, 150, 255, cv2.THRESH_BINARY)
    preprocessed_path = image_path.replace(".jpg", "_processed.jpg")
    cv2.imwrite(preprocessed_path, thresh)
    return preprocessed_path

def extract_items_from_receipt(image_path):
    """
    Extract items and quantities from the receipt using OCR.
    """
    # Perform OCR on the receipt image
    results = reader.readtext(image_path)
    
    # Dictionary to store food items and quantities
    item_quantity = {}

    # Loop through the OCR results to find items and quantities
    for i in range(1, len(results)):
        current_text = results[i][1]  # Current detected text
        previous_text = results[i - 1][1]  # Previous detected text

        # Check if the current text looks like a food item (non-numeric)
        if not current_text.replace(".", "").isdigit():
            # Check if the previous text is a numeric quantity
            if previous_text.replace(".", "", 1).isdigit():
                item_quantity[current_text] = int(float(previous_text))  # Add to dictionary

    return item_quantity

@app.route('/', methods=['GET', 'POST'])
def index():
    item_quantity = None
    newds = None
    totallist = []

    if request.method == 'POST':
        # Check if an image file was uploaded
        if 'image' not in request.files:
            return redirect(request.url)
        file = request.files['image']
        if file.filename == '':
            return redirect(request.url)
        if file:
            # Save the uploaded image
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(image_path)

            # Process the image to extract items and quantities
            item_quantity = extract_items_from_receipt(image_path)

            # Filter dataset using the extracted items
            lst = list(item_quantity.keys())
            newds = pd.DataFrame(filteredds[filteredds['product_name'].isin(lst)])

            # Summing up the columns for the items
            if not newds.empty:
                columns_total = newds[listy].sum()
                totallist = list(columns_total)

    return render_template('index.html', item_quantity=item_quantity, newds=newds.to_html(classes='table table-striped', index=False) if newds is not None else None, totallist=totallist)

if __name__ == '__main__':
    app.run(debug=True)
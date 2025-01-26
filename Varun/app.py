
# import os
# import cv2
# import numpy as np
# from flask import Flask, request, render_template, redirect, url_for
# import easyocr
# import pandas as pd

# app = Flask(__name__)
# app.config['UPLOAD_FOLDER'] = 'uploads'

# # Ensure the upload folder exists
# os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# # Initialize EasyOCR reader
# reader = easyocr.Reader(['en'])

# # Read the filtered dataset outside of the routes, this ensures it's available for use when required
# filteredds = pd.read_csv('/Users/varunsingh/Desktop/Projects/Hackathon MCIT 2025/Python OCR test/NutS/Varun/Final Dataset.csv')

# # Define columns for summing up
# listy = ['fat_100g', 'fiber_100g', 'proteins_100g', 'vitamin-c_100g', 'sugars_100g']

# def preprocess_image(image_path):
#     """
#     Preprocess the image for better OCR results:
#     - Convert to grayscale
#     - Apply thresholding
#     """
#     image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
#     _, thresh = cv2.threshold(image, 150, 255, cv2.THRESH_BINARY)
#     preprocessed_path = image_path.replace(".jpg", "_processed.jpg")
#     cv2.imwrite(preprocessed_path, thresh)
#     return preprocessed_path

# def extract_items_from_receipt(image_path):
#     """
#     Extract items and quantities from the receipt using OCR.
#     """
#     # Perform OCR on the receipt image
#     results = reader.readtext(image_path)
    
#     # Dictionary to store food items and quantities
#     item_quantity = {}

#     # Loop through the OCR results to find items and quantities
#     for i in range(1, len(results)):
#         current_text = results[i][1]  # Current detected text
#         previous_text = results[i - 1][1]  # Previous detected text

#         # Check if the current text looks like a food item (non-numeric)
#         if not current_text.replace(".", "").isdigit():
#             # Check if the previous text is a numeric quantity
#             if previous_text.replace(".", "", 1).isdigit():
#                 item_quantity[current_text] = int(float(previous_text))  # Add to dictionary

#     return item_quantity

# @app.route('/', methods=['GET', 'POST'])
# def index():
#     item_quantity = None
#     newds = None
#     totallist = []

#     if request.method == 'POST':
#         # Check if an image file was uploaded
#         if 'image' not in request.files:
#             return redirect(request.url)
#         file = request.files['image']
#         if file.filename == '':
#             return redirect(request.url)
#         if file:
#             # Save the uploaded image
#             image_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
#             file.save(image_path)

#             # Process the image to extract items and quantities
#             item_quantity = extract_items_from_receipt(image_path)

#             # Filter dataset using the extracted items
#             lst = list(item_quantity.keys())
#             newds = pd.DataFrame(filteredds[filteredds['product_name'].isin(lst)])

#             # Summing up the columns for the items
#             if not newds.empty:
#                 columns_total = newds[listy].sum()
#                 totallist = list(columns_total)

#     return render_template('index.html', item_quantity=item_quantity, newds=newds.to_html(classes='table table-striped', index=False) if newds is not None else None, totallist=totallist)

# if __name__ == '__main__':
#     app.run(debug=True)


import os
import cv2
import re
import numpy as np
import pandas as pd
import easyocr
from flask import Flask, request, render_template, redirect, url_for

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'])

# Load the dataset once
filteredds = pd.read_csv('/Users/varunsingh/Desktop/Projects/Hackathon MCIT 2025/Python OCR test/NutS/Varun/Final Dataset.csv')

# Define required columns
required_columns = ['carbohydrates_100g', 'final_fat', 'fiber_100g', 'proteins_100g', 'Total Vitamin A, C, E', 'sugars_100g']

# Clean and preprocess the dataset
for col in required_columns:
    if col in filteredds.columns:
        filteredds[col] = (
            filteredds[col]
            .astype(str)
            .str.split().str[0]  # Handle repeated values
            .replace('-', None)  # Replace '-' with None
            .astype(float)  # Convert to float
        )

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
                item_quantity[current_text.lower()] = int(float(previous_text))  # Add to dictionary

    return item_quantity

@app.route('/', methods=['GET', 'POST'])
def index():
    item_quantity = None
    summary = None
    int_dict = None

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

            # Preprocess the image
            

            # Extract items and quantities from the receipt
            item_quantity = extract_items_from_receipt(image_path)

            # If items were extracted, process the dataset
            if item_quantity:
                lst = list(item_quantity.keys())
                lstqty = list(item_quantity.values())

                # Filter the dataset for items in the receipt
                filtered_ds = filteredds[filteredds['product_name'].isin(lst)].copy()

                # Add the quantity (number of portions) from the receipt
                filtered_ds['quantity'] = filtered_ds['product_name'].map(item_quantity)

                # Scale nutritional values by quantity
                for col in required_columns:
                    if col in filtered_ds.columns:  # Ensure the column exists
                        filtered_ds[col] = filtered_ds[col] * filtered_ds['quantity']

                # Summarize nutritional values
                summary = filtered_ds[required_columns].sum()

                # Convert the summary to integers
                int_dict = {key: int(value) for key, value in summary.to_dict().items()}

    return render_template(
        'index.html',
        item_quantity=item_quantity,
        summary=int_dict,
        table=filtered_ds.to_html(classes='table table-striped', index=False) if summary is not None else None
    )

if __name__ == '__main__':
    app.run(debug=True)
import os
from flask import Flask, request, render_template, redirect, url_for
import easyocr
import pandas as pd

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'])

def process_image(image_path):
    # Read text from the image
    results = reader.readtext(image_path)

    # Extract detected text into a DataFrame
    data = [{'Detected Text': text} for _, text, _ in results]
    df = pd.DataFrame(data)

    # Initialize a dictionary to store items and their quantities
    item_quantity = {}

    # Iterate through the DataFrame to find items and their quantities
    for i in range(1, len(df)):
        current_text = df.loc[i, 'Detected Text']
        previous_text = df.loc[i - 1, 'Detected Text']

        # Check if the current text is alphabetic (indicating an item)
        if current_text.isalpha():
            # Check if the previous text is numeric (indicating a quantity)
            if previous_text.isdigit():
                item_quantity[current_text] = int(previous_text)

    return item_quantity

@app.route('/', methods=['GET', 'POST'])
def index():
    item_quantity = None
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
            item_quantity = process_image(image_path)

    return render_template('index.html', item_quantity=item_quantity)

if __name__ == '__main__':
    app.run(debug=True)
With a simple yet powerful goal in mind—helping you make healthier food choices and promoting overall well-being—we present NutS, a web application designed to track and analyze your nutritional intake.

Project Overview
NutS is built to assist users in keeping track of their weekly nutrition intake. The application uses OCR technology to extract data from grocery receipts, allowing users to quickly log purchased items. Alternatively, users can manually input their grocery details if preferred.

Once the items are recorded, NutS analyzes the nutritional content of each item and calculates the overall nutritional profile based on the quantities purchased. It then compares this data with the user’s personal dietary needs, which are determined by the body metrics and activity level provided by the user.

How It Works
User Inputs:
The user provides basic personal information, including:

Sex
Age (in years)
Height
Weight (in pounds)
Activity Level
Using this information, the backend calculates the user’s Basal Metabolic Rate (BMR) and daily recommended nutritional goals (Carbohydrates, Proteins, Fats, and Fiber) based on the Mifflin-St Jeor Equation and Dietary Guidelines. These goals are then converted into weekly targets, as we assume the groceries purchased are intended for a week.

Grocery Input:
Users can upload their grocery receipts, which are scanned using OCR to extract item names and quantities (in lbs). Alternatively, users can manually input the grocery details along with the quantities purchased.

Nutritional Analysis:
The app fetches nutritional data for the items from a dataset using Pandas and calculates the total nutritional intake from the groceries. This data is then compared with the user’s personalized weekly goals.

Results
NutS provides users with a comprehensive overview of how their nutritional intake aligns with their recommended goals. It offers a clear comparison of current intake versus ideal targets, helping users stay on track with their health objectives.

This bird’s-eye view of your nutritional habits makes it easier to identify gaps and make informed decisions about your diet, empowering you to live a healthier life!

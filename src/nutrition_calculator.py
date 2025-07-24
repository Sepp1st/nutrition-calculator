from sys import exit
import csv
import pandas as pd
from re import split
from pathlib import Path


# Declaring mesurements
Lb_list = ["lb", "lbs", "pound", "pounds"]
Kg_list = ["kg", "kgs", "kilos", "kilo", "kilogram", "kilograms"]


def Food_macros(weight, name, data):
    # Return nutritional value per 100g serving
    serving = weight/100
    food = name.upper()
    try:
        protein = round(serving*float(data[food]["Protein"]))
        carb = round(serving*float(data[food]["Carbohydrate"]))
        fat = round(serving*float(data[food]["TotalFat"]))
        return [protein, carb, fat]
    # Handle exception if name given was not in the data
    except:
        print(f"Oops, i can't process {name}. Let's skip that one")
        return [0, 0, 0]


def Macros_deficit(protein, carb, fat):
    warnings = []
    food_list = []
    if protein > 50:
        warnings.append(
            "High Protein Deficit: Lack of protein can lead to muscle loss, weakness, and a compromised immune system.")
        food_list.extend(["fish", "dairy", "lean meats"])
    if carb > 50:
        warnings.append(
            "High Carb Deficit: A low-carb diet can lead to low energy and fiber. Lack of fiber is correlated to poor health biomarkers.")
        food_list.extend(["fruits", "veggies", "whole grains"])
    if fat > 30:
        warnings.append(
            "High Fat Deficit: Insufficient fat intake can cause hormonal imbalances and impair cognitive functions.")
        food_list.extend(["olive oil", "avocado", "nuts"])
    return warnings, food_list

def process_food_data(input_file, key_column="Description"):
    """
    Reads the raw USDA CSV, processes it in memory, and returns a summarized DataFrame.
    This replaces the file-based Data_handling function.
    """
    print("Processing food database for this session...")
    try:
        # Define the columns we need to speed up loading
        cols_to_use = [key_column, 'Protein', 'Carbohydrate', 'TotalFat']
        # Read the raw CSV directly into a DataFrame
        data = pd.read_csv(input_file, usecols=cols_to_use, on_bad_lines='skip', low_memory=False)

    except ValueError:
        # Some USDA files use a different name for the 'TotalFat' column.
        # This handles that common case gracefully.
        print("Could not find 'TotalFat' column, trying 'Total Fat (g)'...")
        cols_to_use = [key_column, 'Protein', 'Carbohydrate', 'Total Fat (g)']
        data = pd.read_csv(input_file, usecols=cols_to_use, on_bad_lines='skip', low_memory=False)
        # Standardize the column name for the rest of the script
        data.rename(columns={'Total Fat (g)': 'TotalFat'}, inplace=True)

    # The core logic from your original script, now applied to a DataFrame
    # Create a new column 'Group_Key' with just the first word of the description
    data['Group_Key'] = data[key_column].astype(str).str.split(r'[, ]').str[0].str.upper()

    # Group by this new key and calculate the mean for the nutritional values
    summarized_data = data.groupby('Group_Key')[['Protein', 'Carbohydrate', 'TotalFat']].mean().reset_index()

    # Rename 'Group_Key' back to the original key_column name for consistency
    summarized_data.rename(columns={'Group_Key': key_column}, inplace=True)
    summarized_data = summarized_data.round(2)

    print("Food database processed successfully.")
    return summarized_data


def Maintainance_calories(weight, unit, use_bf, bf_perc, gender, age, height_cm, height_ft, height_in):
    body_weight = float(weight)
    if unit.lower() in Lb_list:
        body_weight /= 2.2

    # 1st way: Katch-McArdle Formula (using body fat)
    if use_bf:
        if not (0 < bf_perc < 100):
            raise ValueError("Body fat percentage must be between 0 and 100.")
        lean_mass = (body_weight * (100 - bf_perc)) / 100
        calories = 370 + (21.6 * lean_mass)
    # 2nd way: Mifflin-St Jeor Equation
    else:
        if unit == "imperial":
            height = round(30.48 * int(height_ft) + 2.54 * int(height_in))
        else: # metric
            height = int(height_cm)

        # The Equation
        calories = (10 * body_weight) + (6.25 * height) - (5 * age) + 5
        if gender.lower() == "female":
            calories -= 161 # Corrected value for female calculation
    return round(calories)


def Macros_goal(Calories, P=25, C=40, F=35):
    if (P + C + F) != 100:
        raise ValueError("Macro percentages must add up to 100.")
    # 1g of protein/carb is 4 calories; 1g of fat is 9 calories
    protein = int(Calories * P * 0.01 / 4)
    carb = int(Calories * C * 0.01 / 4)
    fat = int(Calories * F * 0.01 / 9)
    return protein, carb, fat


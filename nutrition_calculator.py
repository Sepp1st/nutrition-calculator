from sys import exit
import csv
import pandas as pd
from re import split


def main():
    Intro()
    # Exceptions for Error handling
    try:
        # Determine Nutrient goal
        calories = round(Maintainance_calories())
        # Set macro proportion
        if input("I personally recommend a 25p/40c/35f diet.\nWould you like to customise your Macronutrient proportions? (y/n) ").lower() == "y":
            P, C, F = input("Enter desired protein-carb-fat ratio (XX/XX/XX): ").split("/", 2)
            P = int(P)
            C = int(C)
            F = int(F)
            if (P+C+F) != 100:
                exit("Not equal 100%. Let's try again next time! ")
            protein_goal, carb_goal, fat_goal = Macros_goal(calories, P, C, F)
        protein_goal, carb_goal, fat_goal = Macros_goal(calories)
        # Print out recommended daily macros and calories
        print(
            f"\nYou need {calories} calories daily coming from {protein_goal}g protein, {carb_goal}g carbohydrates, {fat_goal}g fat.")

        # Process food data
        Data_handling("USDA.csv", "Food.csv", "Description")

        # Instruction
        print("\nLet's talk about foods you ate today!\nTell me what you ate each meal in grams, using the general one-word name of the food and no plural.\nExample (XXg A): 50g egg or 100g chicken or 250g spinach.")
        print("You can also check the file \"Food.csv\" to search for the food items in the Description column.")
        print("If you are finished with one meal, just type \"full\".\nIf you have had enough for the day, type \"end\".")

        # Start meals query
        # Initialize variables
        meal_count = 1
        item_count = 1
        current_protein, current_fat, current_carb = [0, 0, 0]

        # Meal Loop
        with open("Food.csv", "r") as file:
            # Create a dict containing processed data
            reader = csv.DictReader(file)
            food_data_by_name = {row["Description"]: row for row in reader}
           # Food query loop
            while True:
                # Initializing flag
                food = "init"
                print(f"\nMeal No.{meal_count} consists of: ")
                food = input(f"Meal No.{meal_count} Item No.{item_count} (XXg AA): ")
                if food == "end":
                    print()
                    break
                if food == "full":
                    meal_count += 1
                    item_count = 1
                else:
                    food_weight, food_name = food.split("g ", 1)
                    food_protein, food_carb, food_fat = Food_macros(int(food_weight), food_name, food_data_by_name)
                    current_protein += food_protein
                    current_carb += food_carb
                    current_fat += food_fat
                    item_count += 1
        # Get the recommendation list if eating too little compared to recommended amount
        recommend_list = Macros_deficit(protein_goal - current_protein, carb_goal - current_carb, fat_goal - current_fat)
        # Print out accumulated macros and calories
        print(f"\nYou have consumed {current_protein}g protein, {current_carb}g carbohydrates, {current_fat}g fat so far.")
        print(f"That is around {round(current_protein*4+current_carb*4+current_fat*9)} calories.\n")
        if not recommend_list:
            print("Not bad, you are meeting the nutrition requirements.")
        else:
            print("I suggest including ", end="")
            for item in recommend_list:
                print(f"{item}", end=", ")
        print("\nIt was great working with you! Until next time!\n")
    # Handle exceptions assuming user typed in something wrong
    except Exception:
        exit("Looks like something went wrong, i need you to type in input as i instructed next time.")


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
    # Initialize food list. Add to recommended and print warnings if large deficit
    food_list = []
    if protein > 50:
        print("Lack of Protein leads to Muscle loss, Weakness as well as compromised Immune system and Recovery.\n")
        food_list.extend(["fish", "dairy", "lean meats"])
    if carb > 50:
        print("Lack of carbs generally comes with lack of Fiber.\nYou may adapt to low-carb but consuming carbs has advantages for Performance, Muscle degredation prevention.\nAnd not to mention too little Fiber consumption is correlated to bad health biomarkers.\n")
        food_list.extend(["fruits", "veggies", "whole grains"])
    if fat > 30:
        print("Lack of fat is the cause of Hormonal Imbalance and Impaired Cognitive functions.\n")
        food_list.extend(["olive oil", "avocado", "dark chocolate"])
    return food_list


def Intro():
    # Introduction
    name = input("What should I call you? (Enter your first name) ").title()
    print(f"\nHello, {name}. This is your nutritionist for the day. Free of charge!\n")

    # Instruction for input
    print("When typing input to the program, notice that there are parentheses with the purpose of guiding you.\nPlease do enter as I have instructed.\nBy the way, A stands for letters and words while X stands for numbers, specifically integers.\n")
    print("For example. When \"Age(XX):\" pops up, enter 50 or your age as a number.Let's get started!")


def Data_handling(input, output, key):
    # Read input file and write only first 5 rows to output file
    with open(input, "r") as source:
        reader = csv.reader(source)
        with open(output, "w") as result:
            writer = csv.writer(result)
            for r in reader:
                # Use CSV Index to remove a column from CSV
                # Only keep name and macros, calories
                writer.writerow((r[1], r[2], r[3], r[4], r[5]))

    # Read from shortened data
    data = pd.read_csv(output)
    # Group by mean with first substring splitted from regex
    summarized_data = data.groupby(data[key].apply(lambda x: split(r"(\,| )", x)[0])).mean(
        numeric_only=True).reset_index().round(2)
    # Overwrite the output file
    summarized_data.to_csv(output, index=False)


def Maintainance_calories():
    body_weight, metric = input("First and foremost, type in your bodyweight in lbs or kg. (XX kg or XXX lb)\nYour bodyweight: ").split(" ", maxsplit=1)
    body_weight = int(body_weight)
    # Check valid metrics
    if metric not in Lb_list and metric not in Kg_list:
        raise Exception

    # Convert to kg if needed
    if metric.lower() in Lb_list:
        body_weight /= 2.2

    # 1st way to calculate Daily calories intake is through lean mass
    if input("Can you estimate your body fat percentage? (y/n) ").lower() == "y":
        body_fat = float(input("Great! Type it in (XX): "))
        lean_mass = (body_weight*(100-body_fat))/100
        calories = 370+(21.6*lean_mass)

    # 2nd way is through gender, age, height
    else:
        gender = input("Then enter your gender (specifically biological gender) (m/f): ").lower()
        age = int(input("Then your age (XX): "))
        if input("Your preferrence, metric (meters) or imperial (inches) ? (m/i) ").lower() == "m":
            height = int(input("Then enter your height in cm (XXX): "))
        else:
            feet, inch = input("Enter your height in feet (X'XX): ").split("'", 1)
            if int(inch) > 11:
                exit("Over 12 inches? Let's try again next time! ")
            height = round(30.48*int(feet)+2.54*int(inch))
        # The Equation
        calories = (10*body_weight)+(6.25*height)-(5*age)+5
        # Gender differences
        calories = calories-166 if gender == "f" else calories
    return calories


def Macros_goal(Calories, P=25, C=40, F=35):
    # 1g of protein/carb is 4 calories while 1g of fat is 9 calories
    protein = int(Calories*P*0.01*(1/4))
    carb = int(Calories*C*0.01*(1/4))
    fat = int(Calories*F*0.01*(1/9))
    return [protein, carb, fat]


if __name__ == "__main__":
    main()

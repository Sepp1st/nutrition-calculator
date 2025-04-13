# Nutrition Calculator
## Video Demo:  <https://youtu.be/wrcSv2t546A>
## Data Source: <https://www.kaggle.com/datasets/econdata/usda-food-composition-databases>
## Description:
```
I find it useful in todays developed and developing societies, where Food Supply is no longer a problem but Obesity instead, to monitor how you eat and how it may affect your health. Utilizing a dataset from USDA, downloaded from Kaggle, comprising of various foods and their nutritional content with the aid of pandas for pre processing, I created a small terminal based program to calculate Energy Expenditure and the Nutritional Values of Foods.
```



## README: Step by Step Walkthrough
### Intro()
A welcoming Hello and Input Instruction. This program handles input with Exceptions.

### Maintainance_calories()
- It's a set of questions in order to calculate the estimated amount of calories you burn daily.
- Using Mifflin-St Jeor and Kath-McArdle Equations.
> I decided not to create a reusable, adjustable function since it is rather complex.

> [!NOTE]
> - No function parameters since everything is input from terminal.
> - Returns a float, the Maintainance Calories calculated.

### Macros_goal(Calories, P=25, C=40, F=35)
> Nutrition can be generalized as 3 Macronutrients: Protein, Carbohydrate and Fat.
First function with 4 parameters:
1. Calories: This parameter is *meant* for the calories calculated from **Maintainance_calories()** on top.
2. (And 3&4) Your Macronutrient proportion of choice.
 The default amount I recommended represents my biased view of a balanced diet to support health.
> [!NOTE]
> - Adjust the proportions to your preferrence.
> - Returns a list of 3 *rounded* integers which are number of protein, carbohydrate and fat respectively in grams recommended for daily consumption.

### Data_handling(input, output, key)
> **Handles** my dataset by processing from one csv file to make another. In my case, **group by mean** on food name.
- Input is the parameter for the "raw" data CSV file.
- Output is the name of the "processed" data CSV file to create.
- Key is the value which you want to "group" the data by. In my case, the "Description" column which contains food name.
> [!WARNING]
> - This function have a possibility of messing up the data due to its rather simple methodologies. Indeed, the table *groups* foods by the first substring, splitted by regex.
> - I used to get *out of the charts* nutritional values during the testing phase of this program. 
> - I believe it may still give a reliable glance overall for most of the food composition.

### Food_macros(weight, name, data)
- Weight is the quantity of food in grams. *Provided that your data is food per 100g*.
- Name is the name of the food you wanted to calculate its nutritional value. Foods must be **general** enough to be processed since there are way too many types of food. You may check the Output File to see what it contains.
- Data is the parameter, the Dict variable (containing key-value pairs) plugged in, that holds the data. This may seem tricky but it only takes one line of code to turn the file_reader to the data I used.
- Also includes the Exception in which the food *name* value was not inside the data.
```
Turn file_reader to data demo:
food_data_by_name={row[name]:row for row in reader}
This turn each row of food to a Dict of rows in which keys are the names and values are the data itself.
```
> [!NOTE]
> Returns a 3-integer list of the protein, carb and fat content respectively.

### Macros_left(protein, carb, fat)
- Each parameter is the number of macronutrients away from the intended goal.
- Gives practical food recommendations and warnings when your diet is not _balanced_.
- Returns a list of foods if lack of nutrition.

> [!NOTE]
> - Returns a list of recommended foods if Malnutrition, or an empty list otherwise.
> - **Automatically** prints out Nutrition warnings if Malnutrition.
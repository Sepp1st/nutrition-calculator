# Nutrition Calculator
## Video Demo:  <https://youtu.be/wrcSv2t546A>
## Description:
```
I find it useful in todays developed and developing societies, where Food Supply is no longer a problem but Obesity instead, to monitor how you eat and how it may affect your health. Utilizing a dataset from USDA, downloaded from Kaggle, comprising of various foods and their nutritional content with the aid of pandas for pre processing, I created a small program to calculate Energy Expenditure and the Nutritional Values of Foods.
```



## README: Step by Step Explaination
### Intro()
A welcoming Hello and Input Instruction.
> [!NOTE]
> - No function parameters.
> - No return value.

### Maintainance_calories()
- It's a set of questions in order to calculate the estimated amount of calories you burn daily.
- Using Mifflin-St Jeor and Kath-McArdle Equations.
> I decided not to create a reusable, adjustable function since it is rather complex.

> [!NOTE]
> - No function parameters.
> - Returns a float.

### Macros_goal(Calories, P=25, C=40, F=35)
> Nutrition can be generalized as 3 Macronutrients: Protein, Carbohydrate and Fat.
First function with 4 parameters:
1. Calories: Uses the calories calculated from __Maintainance_calories()__ on top.
2. (And 3&4) Your Macronutrient proportion of choice.
 The amount I recommended represents a balanced diet to support health.
> [!NOTE]
> - Adjust the proportions to your preferrence.
> - Returns a list of 3 rounded integers.

### Data_handling(input, output, key)
> This can be adjusted for other files, with a caveat I'll mention at the end.
- Input is the parameter for the "raw" data CSV file.
- Output is the name of the "summarized" data CSV file to create.
- Key is the value which you want to "group" the data by. In my case, the "Description" column.
> [!WARNING]
> - The function only "process" data from column 1-5.
> - You may need to get the source code in order to adjust this.
> - No return value.

### Food_macros(weight, name, data)
- Weight is the quantity of food in grams. _Provided that your data is food per 100g_.
- Name is the food you wanted to calculate its nutritional value. Foods must be general enough to be processed since there are way too many types of food. You may check the Output File to see what it contains.
- Data is the parameter, the Dict variable plugged in, that holds the data. This may seem tricky but it only takes one line of code to turn the file_reader to the data I used.
- The function returns a 3-element list comprises of the protein, carb and fat content respectively.
- Also includes the Exception in which the "food" was not inside the data.
```
Turn file_reader to data demo:
food_data_by_name={row[name]:row for row in reader}
This turn each row of food to a Dict of rows in which keys are the names and values are the data itself.
```
> [!NOTE]
> Returns a 3-integer list.

### Macros_left(protein, carb, fat)
- Each parameter is the number of macronutrients away from the intended goal.
- Gives practical food recommendations and warnings when your diet is not _balanced_.
- Returns a list of foods if lack of nutrition.

> [!NOTE]
> - Returns a list of recommended foods if Malnutrition, or an empty list otherwise.
> - Automatically prints out Nutrition warnings if Malnutrition.
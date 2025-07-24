import gradio as gr
import pandas as pd
import sys

# Import the logic functions from your original script
import nutrition_calculator as nc

# --- Initial Setup ---
INPUT_CSV = "../data/USDA.csv"

# Load and process food data directly into a DataFrame in memory
try:
    # This single function call replaces the file creation and reading
    food_df = nc.process_food_data(INPUT_CSV, "Description")

    # Create a dictionary for fast lookups: { "EGG": {"Protein": 12.6, ...}, ... }
    food_df_upper = food_df.copy()
    food_df_upper["Description"] = food_df_upper["Description"].str.upper()
    food_data_by_name = food_df_upper.set_index("Description").to_dict("index")

    # Get a list of food names for the dropdown
    food_choices = sorted(food_df["Description"].dropna().unique().tolist())

except FileNotFoundError:
    print(f"CRITICAL ERROR: The food database '{INPUT_CSV}' was not found.")
    print("Please make sure 'USDA.csv' is in the same directory as this script.")
    # If the data isn't loaded, we can't run the app.
    # We provide empty fallbacks so Gradio can at least render an error message.
    food_choices = [f"ERROR: {INPUT_CSV} not found"]
    food_data_by_name = {}
    food_df = pd.DataFrame()  # empty dataframe
except Exception as e:
    print(f"An error occurred during data processing: {e}")
    food_choices = ["ERROR: Data processing failed"]
    food_data_by_name = {}
    food_df = pd.DataFrame()


# --- Gradio UI Functions (These remain unchanged from the previous answer) ---

def calculate_goals(weight, unit, use_bf, bf_perc, gender, age, height_cm, height_ft, height_in, p_perc, c_perc,
                    f_perc):
    """Calculates calorie and macro goals based on user input."""
    try:
        # 1. Calculate maintenance calories
        calories = nc.Maintainance_calories(weight, unit, use_bf, bf_perc, gender, age, height_cm, height_ft, height_in)

        # 2. Calculate macro goals
        protein, carb, fat = nc.Macros_goal(calories, p_perc, c_perc, f_perc)

        # 3. Format the output string
        goal_summary = f"""
        ### Your Daily Goals
        | Nutrient      | Goal        |
        |---------------|-------------|
        | **Calories**  | **{calories} kcal** |
        | Protein       | {protein} g     |
        | Carbohydrates | {carb} g        |
        | Fat           | {fat} g         |
        """

        # Return the summary, goals for state, and make the next section visible
        return goal_summary, [calories, protein, carb, fat], gr.update(visible=True)
    except ValueError as e:
        # Handle errors gracefully
        gr.Warning(str(e))
        return None, [0, 0, 0, 0], gr.update(visible=False)


def add_food(food_name, weight, current_log, current_totals):
    """Adds a food item to the daily log and updates totals."""
    if not food_name or not weight or weight <= 0:
        gr.Warning("Please select a food and enter a valid weight.")
        return current_log, current_totals, f"Current Totals: P: {current_totals[1]}g, C: {current_totals[2]}g, F: {current_totals[3]}g"

    # Get macros for the selected food
    p, c, f = nc.Food_macros(weight, food_name, food_data_by_name)

    # Update totals [calories, protein, carb, fat]
    current_totals[1] += p
    current_totals[2] += c
    current_totals[3] += f
    current_totals[0] = round(current_totals[1] * 4 + current_totals[2] * 4 + current_totals[3] * 9)

    # Update log DataFrame
    new_entry = pd.DataFrame(
        [{"Food": food_name, "Weight (g)": weight, "Protein (g)": p, "Carbs (g)": c, "Fat (g)": f}])
    updated_log = pd.concat([current_log, new_entry], ignore_index=True)

    totals_str = f"**Current Totals** -> Calories: **{current_totals[0]} kcal** | Protein: **{current_totals[1]}g** | Carbs: **{current_totals[2]}g** | Fat: **{current_totals[3]}g**"

    return updated_log, current_totals, totals_str


def generate_summary(goal_state, current_totals):
    """Generates the final summary and recommendations."""
    goal_cals, goal_p, goal_c, goal_f = goal_state
    current_cals, current_p, current_c, current_f = current_totals

    p_deficit = goal_p - current_p
    c_deficit = goal_c - current_c
    f_deficit = goal_f - current_f

    warnings, recommendations = nc.Macros_deficit(p_deficit, c_deficit, f_deficit)

    summary_text = "### Final Summary\n"
    summary_text += "| Nutrient | Goal | Consumed | Deficit |\n"
    summary_text += "|:---|---:|---:|---:|\n"
    summary_text += f"| Protein (g) | {goal_p} | {current_p} | **{p_deficit}** |\n"
    summary_text += f"| Carbs (g) | {goal_c} | {current_c} | **{c_deficit}** |\n"
    summary_text += f"| Fat (g) | {goal_f} | {current_f} | **{f_deficit}** |\n"

    if warnings:
        summary_text += "\n**Alerts based on your deficits:**\n"
        for warning in warnings:
            summary_text += f"- *{warning}*\n"

    if recommendations:
        summary_text += f"\nTo help meet your goals, I suggest including: **{', '.join(recommendations)}**."
    else:
        summary_text += "\n**Great job! You are meeting your general nutrition requirements.**"

    return summary_text


# --- Gradio Interface Layout (Unchanged) ---
with gr.Blocks(theme=gr.themes.Soft(), title="Nutrition Calculator") as demo:
    if not food_df.empty:
        # State variables to hold data between interactions
        goal_state = gr.State([0, 0, 0, 0])  # [calories, protein, carb, fat]
        current_totals_state = gr.State([0, 0, 0, 0])  # [calories, protein, carb, fat]
        log_df_state = gr.State(pd.DataFrame(columns=["Food", "Weight (g)", "Protein (g)", "Carbs (g)", "Fat (g)"]))

        gr.Markdown("# Nutrition Calculator & Meal Logger")
        gr.Markdown("Follow the steps below to calculate your nutritional goals and track your daily intake.")

        with gr.Tabs():
            with gr.TabItem("Step 1: Calculate Your Goals"):
                with gr.Row():
                    with gr.Column(scale=2):
                        gr.Markdown("### Your Profile")
                        weight = gr.Number(label="Weight", value=70)
                        unit = gr.Radio(choices=["kg", "lbs"], label="Unit", value="kg")
                        age = gr.Number(label="Age", value=30, minimum=1)
                        gender = gr.Radio(choices=["male", "female"], label="Biological Gender", value="male")

                        use_bf = gr.Checkbox(label="I know my body fat % (more accurate)", value=False)
                        with gr.Group(visible=False) as bf_group:
                            bf_perc = gr.Slider(minimum=3, maximum=50, label="Body Fat %", value=15)

                        with gr.Group(visible=True) as height_group:
                            height_unit = gr.Radio(["metric", "imperial"], label="Height Unit", value="metric")
                            with gr.Row(visible=True) as metric_height_group:
                                height_cm = gr.Number(label="Height (cm)", value=175)
                            with gr.Row(visible=False) as imperial_height_group:
                                height_ft = gr.Number(label="Feet", value=5)
                                height_in = gr.Number(label="Inches", value=9)

                    with gr.Column(scale=1):
                        gr.Markdown("### Macro Split (%)")
                        p_perc = gr.Slider(20, 50, value=25, label="Protein %", step=1)
                        c_perc = gr.Slider(20, 60, value=40, label="Carbs %", step=1)
                        f_perc = gr.Slider(15, 40, value=35, label="Fat %", step=1)

                use_bf.change(lambda x: (gr.update(visible=x), gr.update(visible=not x)), use_bf,
                              [bf_group, height_group])
                height_unit.change(lambda x: (gr.update(visible=x == "metric"), gr.update(visible=x == "imperial")),
                                   height_unit, [metric_height_group, imperial_height_group])

                calculate_btn = gr.Button("Calculate My Goals", variant="primary")
                goal_summary_output = gr.Markdown()

            with gr.TabItem("Step 2: Log Your Food"):
                with gr.Group(visible=False) as logging_group:
                    with gr.Row():
                        food_dropdown = gr.Dropdown(choices=food_choices, label="Select Food", filterable=True)
                        food_weight = gr.Number(label="Weight (g)", value=100)
                        add_food_btn = gr.Button("Add to Log", variant="secondary")

                    current_totals_output = gr.Markdown(
                        "**Current Totals** -> Calories: **0 kcal** | Protein: **0g** | Carbs: **0g** | Fat: **0g**")
                    log_df_output = gr.DataFrame(value=log_df_state.value, interactive=False)
                    final_summary_btn = gr.Button("Show Final Summary", variant="primary")
                    final_summary_output = gr.Markdown()

        calculate_btn.click(fn=calculate_goals,
                            inputs=[weight, unit, use_bf, bf_perc, gender, age, height_cm, height_ft, height_in, p_perc,
                                    c_perc, f_perc], outputs=[goal_summary_output, goal_state, logging_group])
        add_food_btn.click(fn=add_food, inputs=[food_dropdown, food_weight, log_df_state, current_totals_state],
                           outputs=[log_df_output, current_totals_state, current_totals_output])
        final_summary_btn.click(fn=generate_summary, inputs=[goal_state, current_totals_state],
                                outputs=[final_summary_output])
    else:
        gr.Error(
            f"Application could not start. Please check the console for errors, likely a missing '{INPUT_CSV}' file.")

if __name__ == "__main__":
    demo.launch()
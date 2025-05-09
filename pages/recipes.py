import streamlit as st
import pandas as pd
import os

# Title of the page
st.title("Recipes")

# Load the intolerances data
intolerances_csv = "Intoleranssit & Ruokavaliot.csv"
intolerances_data = pd.read_csv(intolerances_csv)

# Load the ingredients data
ingredients_csv = "Ingredients.csv"
ingredients_data = pd.read_csv(ingredients_csv)

# Extract the list of valid ingredients
valid_ingredients = ingredients_data["Aineosat"].tolist()

# Extract the list of authors (IDs from intolerances data)
authors = intolerances_data["ID"].tolist()
authors.append("guest")  # Add "guest" as an option

# Recipe storage file
recipes_csv = "Recipes.csv"

# Check if the recipes file exists, if not, create it
if not os.path.exists(recipes_csv):
    pd.DataFrame(columns=["Name", "Ingredients", "Steps", "Notes", "Author", "Label"]).to_csv(recipes_csv, index=False)

# Load existing recipes
recipes_data = pd.read_csv(recipes_csv)

# Option to display stored recipes
if st.checkbox("Show Stored Recipes"):
    st.subheader("Stored Recipes")
    if not recipes_data.empty:
        for _, recipe in recipes_data.iterrows():
            st.markdown(f"### {recipe['Name']}")
            st.markdown(f"**Author**: {recipe['Author']}")
            st.markdown(f"**Label**: {recipe['Label']}")
            st.markdown(f"**Ingredients**: {recipe['Ingredients']}")
            st.markdown(f"**Steps**: {recipe['Steps']}")
            if pd.notna(recipe['Notes']):  # Only display notes if they exist
                st.markdown(f"**Notes**: {recipe['Notes']}")
            st.markdown("---")
    else:
        st.write("No recipes stored yet.")

# Option to edit a recipe
if st.checkbox("Edit a Recipe"):
    st.subheader("Edit a Recipe")
    
    # Select a recipe to edit
    recipe_to_edit = st.selectbox(
        "Select a Recipe to Edit",
        options=recipes_data["Name"].tolist(),
        help="Choose a recipe to edit",
    )
    
    if recipe_to_edit:
        # Load the selected recipe's details
        recipe_details = recipes_data[recipes_data["Name"] == recipe_to_edit].iloc[0]
        
        # Pre-fill the fields with the recipe's details
        recipe_name = st.text_input("Recipe Name", value=recipe_details["Name"])
        selected_ingredients = st.multiselect(
            "Select Ingredients for the Recipe",
            options=valid_ingredients,
            default=[ingredient.split(" (")[0] for ingredient in recipe_details["Ingredients"].split(", ")],
        )
        ingredient_quantities = {}
        for ingredient in selected_ingredients:
            quantity = st.number_input(
                f"Quantity of {ingredient} per person",
                min_value=0.0,
                step=0.1,
                value=float(
                    next(
                        (ingredient.split(" (")[1].split(" ")[0] for ingredient in recipe_details["Ingredients"].split(", ") if ingredient.startswith(ingredient)),
                        0.0,
                    )
                ),
            )
            ingredient_quantities[ingredient] = quantity
        
        # Steps
        st.markdown("### Steps")
        steps = []
        if "steps" not in st.session_state:
            st.session_state["steps"] = [
                {
                    "process": step.split(" ")[0],
                    "ingredients": step.split(" ")[1].split(",") if " (" in step else [],
                    "description": step.split("(")[1].strip(")") if " (" in step else "",
                }
                for step in recipe_details["Steps"].split("; ")
            ]
        
        # Add a new step
        with st.form("edit_step_form"):
            process = st.selectbox(
                "Process",
                ["Add", "Bake", "Fry", "Saltee", "Cut (and shape)", "Boil", "Mix", "Grill", "Steam", "Custom"],
                help="Select the process for this step",
            )
            step_ingredients = st.multiselect(
                "Ingredients (optional)", options=selected_ingredients, help="Select one or more ingredients for this step"
            )
            step_description = st.text_input(
                "Description (optional)", placeholder="E.g., put the dough in the cake mould"
            )
            add_step = st.form_submit_button("Add Step")
            if add_step:
                if process == "Custom" and not step_description:
                    st.warning("Please provide a description for the custom step.")
                else:
                    st.session_state["steps"].append(
                        {"process": process, "ingredients": step_ingredients, "description": step_description}
                    )
        
        # Display added steps
        for i, step in enumerate(st.session_state["steps"]):
            ingredients_list = ", ".join(step["ingredients"]) if step["ingredients"] else "No ingredients"
            st.write(f"{i + 1}. {step['process']} {ingredients_list} - {step['description']}")
        
        # Notes
        notes = st.text_area("Notes", value=recipe_details["Notes"] if pd.notna(recipe_details["Notes"]) else "")
        
        # Author
        author = st.selectbox("Author", options=authors, index=authors.index(recipe_details["Author"]))
        
        # Label
        label = st.selectbox(
            "Label",
            ["Main Dish", "Side Dish", "Dessert", "Drink", "Dressing", "Appetizer"],
            index=["Main Dish", "Side Dish", "Dessert", "Drink", "Dressing", "Appetizer"].index(recipe_details["Label"]),
        )
        
        # Save the updated recipe
        if st.button("Save Changes"):
            if recipe_name and selected_ingredients and st.session_state["steps"]:
                # Format ingredients and steps for storage
                formatted_ingredients = ", ".join(
                    [f"{ingredient} ({quantity} per person)" for ingredient, quantity in ingredient_quantities.items()]
                )
                formatted_steps = "; ".join(
                    [
                        f"{step['process']} {', '.join(step['ingredients'])} ({step['description']})"
                        for step in st.session_state["steps"]
                    ]
                )
                
                # Update the recipe in the DataFrame
                recipes_data.loc[recipes_data["Name"] == recipe_to_edit, :] = [
                    recipe_name,
                    formatted_ingredients,
                    formatted_steps,
                    notes,
                    author,
                    label,
                ]
                
                # Save the updated DataFrame to the CSV file
                recipes_data.to_csv(recipes_csv, index=False)
                
                # Clear session state for steps
                st.session_state["steps"] = []
                
                st.success("Recipe updated successfully!")
            else:
                st.error("Please fill in all required fields (name, ingredients, and steps).")

# Input for new recipe
st.subheader("Create a New Recipe")

# Recipe name
recipe_name = st.text_input("Recipe Name", placeholder="Enter the name of the recipe")

# Multiselect for ingredients
selected_ingredients = st.multiselect(
    "Select Ingredients for the Recipe",
    options=valid_ingredients,
    help="Choose ingredients from the list",
)

# Input quantities for each ingredient
ingredient_quantities = {}
for ingredient in selected_ingredients:
    quantity = st.number_input(f"Quantity of {ingredient} per person", min_value=0.0, step=0.1)
    ingredient_quantities[ingredient] = quantity

# Steps for the recipe
st.markdown("### Steps")
steps = []
if "steps" not in st.session_state:
    st.session_state["steps"] = []

# Add a new step
with st.form("add_step_form"):
    process = st.selectbox(
        "Process",
        ["Add", "Bake", "Fry", "Saltee", "Cut (and shape)", "Boil", "Mix", "Grill", "Steam", "Custom"],
        help="Select the process for this step",
    )
    step_ingredients = st.multiselect(
        "Ingredients (optional)", options=selected_ingredients, help="Select one or more ingredients for this step"
    )
    step_description = st.text_input(
        "Description (optional)", placeholder="E.g., put the dough in the cake mould"
    )
    add_step = st.form_submit_button("Add Step")
    if add_step:
        if process == "Custom" and not step_description:
            st.warning("Please provide a description for the custom step.")
        else:
            st.session_state["steps"].append(
                {"process": process, "ingredients": step_ingredients, "description": step_description}
            )

# Display added steps
for i, step in enumerate(st.session_state["steps"]):
    ingredients_list = ", ".join(step["ingredients"]) if step["ingredients"] else "No ingredients"
    st.write(f"{i + 1}. {step['process']} {ingredients_list} - {step['description']}")

# Notes
notes = st.text_area("Notes", placeholder="Add any additional notes about the recipe")

# Author
author = st.selectbox("Author", options=authors)

# Label
label = st.selectbox(
    "Label",
    ["Main Dish", "Side Dish", "Dessert", "Drink", "Dressing", "Appetizer"],
    help="Select a label for the recipe",
)

# Save the recipe
if st.button("Save Recipe"):
    if recipe_name and selected_ingredients and st.session_state["steps"]:
        # Format ingredients and steps for storage
        formatted_ingredients = ", ".join([f"{ingredient} ({quantity} per person)" for ingredient, quantity in ingredient_quantities.items()])
        formatted_steps = "; ".join([f"{step['process']} {', '.join(step['ingredients'])} ({step['description']})" for step in st.session_state["steps"]])

        # Append the new recipe to the CSV file
        new_recipe = pd.DataFrame(
            [[recipe_name, formatted_ingredients, formatted_steps, notes, author, label]],
            columns=["Name", "Ingredients", "Steps", "Notes", "Author", "Label"],
        )
        new_recipe.to_csv(recipes_csv, mode="a", header=False, index=False)

        # Clear session state for steps
        st.session_state["steps"] = []

        st.success("Recipe saved successfully!")
    else:
        st.error("Please fill in all required fields (name, ingredients, and steps).")

# Check for intolerances
if st.button("Check Intolerances"):
    if selected_ingredients:
        # Columns to check for intolerances
        intolerance_columns = intolerances_data.columns[4:]  # Intolerance columns start from the 5th column

        # Guests with intolerances
        conflicting_guests = []

        for _, row in intolerances_data.iterrows():
            guest_name = row["Name"]
            conflicts = []
            for ingredient in selected_ingredients:
                # Check if the ingredient matches any intolerance column
                ingredient_row = ingredients_data[ingredients_data["Aineosat"] == ingredient]
                if not ingredient_row.empty:
                    for col in intolerance_columns:
                        # Skip columns that do not exist in ingredients_data
                        if col not in ingredient_row.columns:
                            continue
                        if ingredient_row.iloc[0][col] == 1 and row[col] == 1:
                            conflicts.append(col)
            if conflicts:
                conflicting_guests.append((guest_name, conflicts))

        # Display results
        if conflicting_guests:
            st.error("Some guests have intolerances to the ingredients in this recipe:")
            for guest, conflicts in conflicting_guests:
                st.write(f"- **{guest}**: Intolerances to {', '.join(conflicts)}")
        else:
            st.success("No conflicts! All guests can enjoy this recipe.")
    else:
        st.warning("Please select ingredients to check for intolerances.")
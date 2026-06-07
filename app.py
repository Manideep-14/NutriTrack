"""NutriTrack - A simple Flask web application to track daily nutritional intake.
This module initializes the Flask app, configures basic settings, and defines
the routing logic for viewing the landing page and adding new meal records."""

from flask import Flask, render_template, request, redirect,flash

# Initialize the Flask application

app = Flask(__name__)

# Secret key required for signing session cookies and using Flask's flash messages
app.secret_key = "nutritrack123"

# In-memory database simulation to store submitted meal dictionaries
# Store meals
meals = []

# Home Page
@app.route("/")
def home():
    """Render the main home page/landing page.

    Returns:
        str_: _The rendered HTML content of index.html._
    """
    return render_template("index.html")


# Add Meal
@app.route("/add-meal", methods=["GET", "POST"])
def add_meal():
    """
    Handle the viewing and submission of the meal addition form.

    GET request: Displays the empty add meal form.
    POST request: Extracts meal data from the form, validates/casts inputs,
                  appends the meal to the global store, and redirects.

    Returns:
        Response: A redirect to another page (e.g., dashboard) on successful POST,
                  or the rendered add_meal.html template on GET.
    """

    if request.method == "POST":
        # Extract and format the meal data from the submitted form

        meal = {
            "food": request.form["food"],
            "protein": int(request.form["protein"]),# Convert nutritional data to integers
            "calories": int(request.form["calories"]),# Convert nutritional data to integers
            "meal_type": request.form["meal_type"]
        }

       # Append the new meal data to our temporary storage list
        meals.append(meal)

        # Display a success message to the user on their next page load
        flash("Meal added successfully!", "success")

        # Redirect the user back to a main page (like a dashboard or home)
        return redirect("/dashboard")
    
    # If the user is just visiting the URL via GET, show them the form page
    return render_template("add_meal.html")


# Dashboard
@app.route("/dashboard")
def dashboard():
    """
    Render the user dashboard displaying personal nutritional metrics.

    Calculates total protein consumed from the tracked meals list, evaluates
    the progress percentage against a daily static target, and caps the progress
    bar metrics at 100%.

    Returns:
        str: Rendered HTML template ('dashboard.html') injected with meals data,
             calculated total protein, and progress metrics.
    """
    # Sum the 'protein' value from every meal dictionary in the meals list
    total_protein = sum(meal["protein"] for meal in meals)
    
    # Define a static daily goal for protein intake (in grams)
    protein_goal = 120

    # Calculate progress percentage and cap it at 100% using min() so UI bars don't overflow
    progress = min((total_protein / protein_goal) * 100, 100)


    # Pass the calculated data into the dashboard template context
    return render_template(
        "dashboard.html",
        meals=meals,
        total_protein=total_protein,
        progress=progress
    )


# Summary
@app.route("/summary")
def summary():
    """
    Render a nutritional summary report of all logged meals.

    Aggregates overall nutritional metrics to provide an alternative,
    comprehensive breakdown of the user's daily data.

    Returns:
        str: Rendered HTML template ('summary.html') containing the aggregated metrics.
    """
    
    # Aggregate total protein consumed across all items in the temporary database list
    total_protein = sum(
        meal["protein"]
        for meal in meals
    )
    
    # Aggregate total calories consumed across all items in the temporary database list
    total_calories = sum(
        meal["calories"]
        for meal in meals
    )
    
    # Define a static daily goal for protein intake (in grams)
    protein_goal = 120
    

    # Determine if the daily protein intake target has been reached or exceeded
    if total_protein >= protein_goal:
        goal_status = "Goal Achieved"
    else:
        goal_status = f"{protein_goal-total_protein}g Remaining"
    
    # Render the summary page template, injecting all calculated metrics
    return render_template(
        "summary.html",
        total_protein=total_protein,
        total_calories=total_calories,
        goal_status=goal_status,
        meal_count=len(meals)
    )
@app.route("/delete/<int:index>")
def delete_meal(index):
    """
    Remove a specific meal record from the tracking list based on its index.

    Validates that the provided index exists within the boundaries of the list
    to prevent IndexError exceptions before attempting removal.

    Args:
        index (int): The zero-based positional index of the meal item to delete.

    Returns:
        Response: A redirect command sending the user back to the dashboard page.
    """

    # Defensive check: Ensure the index falls within the valid range of the list
    if 0 <= index < len(meals):
        
        
    # Remove and discard the item at the specified index position    
        meals.pop(index)

    # Always return back to the main dashboard to show updated changes
    return redirect("/dashboard")

# Standard Python boilerplate to ensure the server only boots when run directly
if __name__ == "__main__":

    # Start the Flask development server on a custom port with hot-reloading enabled
    app.run(debug=True, port=5050) 
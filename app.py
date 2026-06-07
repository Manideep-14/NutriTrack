from flask import Flask, render_template, request, redirect, flash  # type: ignore

app = Flask(__name__)
app.secret_key = "nutritrack123"
# Store meals
meals = []

# Home Page
@app.route("/")
def home():
    return render_template("index.html")


# Add Meal
@app.route("/add-meal", methods=["GET", "POST"])
def add_meal():

    if request.method == "POST":

        meal = {
            "food": request.form["food"],
            "protein": int(request.form["protein"]),
            "calories": int(request.form["calories"]),
            "meal_type": request.form["meal_type"]
        }

        meals.append(meal)

        flash("Meal added successfully!", "success")
        return redirect("/dashboard")

    return render_template("add_meal.html")


# Dashboard
@app.route("/dashboard")
def dashboard():
    total_protein = sum(meal["protein"] for meal in meals)

    protein_goal = 120
    progress = min((total_protein / protein_goal) * 100, 100)

    return render_template(
        "dashboard.html",
        meals=meals,
        total_protein=total_protein,
        progress=progress
    )


# Summary
@app.route("/summary")
def summary():

    total_protein = sum(
        meal["protein"]
        for meal in meals
    )

    total_calories = sum(
        meal["calories"]
        for meal in meals
    )

    protein_goal = 120

    if total_protein >= protein_goal:
        goal_status = "Goal Achieved"
    else:
        goal_status = f"{protein_goal-total_protein}g Remaining"

    return render_template(
        "summary.html",
        total_protein=total_protein,
        total_calories=total_calories,
        goal_status=goal_status,
        meal_count=len(meals)
    )
@app.route("/delete/<int:index>")
def delete_meal(index):
    if 0 <= index < len(meals):
        meals.pop(index)
    return redirect("/dashboard")

if __name__ == "__main__":
    app.run(debug=True, port=5050)
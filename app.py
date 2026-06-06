from flask import Flask, render_template, request, redirect

app = Flask(__name__)

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

        return redirect("/dashboard")

    return render_template("add_meal.html")


# Dashboard
@app.route("/dashboard")
def dashboard():

    return render_template(
        "dashboard.html",
        meals=meals
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
        goal_status=goal_status
    )


if __name__ == "__main__":
    app.run(debug=True)
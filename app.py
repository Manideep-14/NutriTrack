"""
Personal Nutrition & Daily Protein Tracker
Flask Web Application - Main Entry Point
"""

import os
from datetime import date, datetime
from typing import Optional

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# ─── Configuration ────────────────────────────────────────────────────────────

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///nutrition.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ─── Models (Database) ────────────────────────────────────────────────────────

class FoodEntry(db.Model):
    """Represents a single food log entry for a given day."""

    __tablename__ = "food_entries"

    id: int = db.Column(db.Integer, primary_key=True)
    food_name: str = db.Column(db.String(120), nullable=False)
    calories: float = db.Column(db.Float, nullable=False)
    protein_g: float = db.Column(db.Float, nullable=False, default=0.0)
    carbs_g: float = db.Column(db.Float, nullable=False, default=0.0)
    fat_g: float = db.Column(db.Float, nullable=False, default=0.0)
    entry_date: date = db.Column(db.Date, nullable=False, default=date.today)
    created_at: datetime = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self) -> dict:
        """Serialize model instance to a JSON-safe dictionary."""
        return {
            "id": self.id,
            "food_name": self.food_name,
            "calories": self.calories,
            "protein_g": self.protein_g,
            "carbs_g": self.carbs_g,
            "fat_g": self.fat_g,
            "entry_date": self.entry_date.isoformat(),
            "created_at": self.created_at.isoformat(),
        }


class UserGoal(db.Model):
    """Stores the user's daily nutrition targets."""

    __tablename__ = "user_goals"

    id: int = db.Column(db.Integer, primary_key=True)
    daily_calories: float = db.Column(db.Float, nullable=False, default=2000.0)
    daily_protein_g: float = db.Column(db.Float, nullable=False, default=150.0)
    daily_carbs_g: float = db.Column(db.Float, nullable=False, default=250.0)
    daily_fat_g: float = db.Column(db.Float, nullable=False, default=65.0)
    updated_at: datetime = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "daily_calories": self.daily_calories,
            "daily_protein_g": self.daily_protein_g,
            "daily_carbs_g": self.daily_carbs_g,
            "daily_fat_g": self.daily_fat_g,
        }


# ─── Helper Functions ─────────────────────────────────────────────────────────

def get_daily_totals(target_date: date) -> dict:
    """Aggregate nutrition totals for a given date."""
    entries = FoodEntry.query.filter_by(entry_date=target_date).all()
    totals = {
        "calories": sum(e.calories for e in entries),
        "protein_g": sum(e.protein_g for e in entries),
        "carbs_g": sum(e.carbs_g for e in entries),
        "fat_g": sum(e.fat_g for e in entries),
        "entry_count": len(entries),
    }
    return totals


def get_or_create_goal() -> UserGoal:
    """Return existing goal row or create defaults."""
    goal = UserGoal.query.first()
    if not goal:
        goal = UserGoal()
        db.session.add(goal)
        db.session.commit()
    return goal


# ─── Frontend Routes ──────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Render the main dashboard page."""
    today = date.today()
    totals = get_daily_totals(today)
    goal = get_or_create_goal()
    return render_template("index.html", totals=totals, goal=goal, today=today.isoformat())


@app.route("/log")
def log_page():
    """Render the food logging page."""
    return render_template("log.html")


@app.route("/history")
def history_page():
    """Render the history/analytics page."""
    return render_template("history.html")


# ─── API Routes ───────────────────────────────────────────────────────────────

@app.route("/api/entries", methods=["GET"])
def get_entries():
    """
    GET /api/entries
    Query params:
        date (str, optional): ISO date string YYYY-MM-DD. Defaults to today.
    Returns list of food entries for the given date.
    """
    date_str: Optional[str] = request.args.get("date")
    try:
        target_date = date.fromisoformat(date_str) if date_str else date.today()
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

    entries = FoodEntry.query.filter_by(entry_date=target_date).order_by(FoodEntry.created_at).all()
    totals = get_daily_totals(target_date)

    return jsonify({
        "date": target_date.isoformat(),
        "entries": [e.to_dict() for e in entries],
        "totals": totals,
    })


@app.route("/api/entries", methods=["POST"])
def add_entry():
    """
    POST /api/entries
    Body (JSON):
        food_name (str): Name of the food.
        calories (float): Total calories.
        protein_g (float): Protein in grams.
        carbs_g (float): Carbohydrates in grams.
        fat_g (float): Fat in grams.
        entry_date (str, optional): ISO date. Defaults to today.
    """
    data: dict = request.get_json(silent=True) or {}

    # Validate required fields
    required = ["food_name", "calories", "protein_g"]
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    try:
        entry_date = date.fromisoformat(data["entry_date"]) if "entry_date" in data else date.today()
    except ValueError:
        return jsonify({"error": "Invalid entry_date format. Use YYYY-MM-DD."}), 400

    entry = FoodEntry(
        food_name=str(data["food_name"]).strip(),
        calories=float(data["calories"]),
        protein_g=float(data["protein_g"]),
        carbs_g=float(data.get("carbs_g", 0)),
        fat_g=float(data.get("fat_g", 0)),
        entry_date=entry_date,
    )
    db.session.add(entry)
    db.session.commit()

    return jsonify({"message": "Entry added successfully.", "entry": entry.to_dict()}), 201


@app.route("/api/entries/<int:entry_id>", methods=["DELETE"])
def delete_entry(entry_id: int):
    """
    DELETE /api/entries/<entry_id>
    Removes a food log entry by ID.
    """
    entry = db.session.get(FoodEntry, entry_id)
    if not entry:
        return jsonify({"error": "Entry not found."}), 404

    db.session.delete(entry)
    db.session.commit()
    return jsonify({"message": f"Entry {entry_id} deleted."})


@app.route("/api/goals", methods=["GET"])
def get_goals():
    """GET /api/goals — Returns the user's current nutrition goals."""
    goal = get_or_create_goal()
    return jsonify(goal.to_dict())


@app.route("/api/goals", methods=["PUT"])
def update_goals():
    """
    PUT /api/goals
    Body (JSON): daily_calories, daily_protein_g, daily_carbs_g, daily_fat_g
    Updates the user's nutrition targets.
    """
    data: dict = request.get_json(silent=True) or {}
    goal = get_or_create_goal()

    if "daily_calories" in data:
        goal.daily_calories = float(data["daily_calories"])
    if "daily_protein_g" in data:
        goal.daily_protein_g = float(data["daily_protein_g"])
    if "daily_carbs_g" in data:
        goal.daily_carbs_g = float(data["daily_carbs_g"])
    if "daily_fat_g" in data:
        goal.daily_fat_g = float(data["daily_fat_g"])

    db.session.commit()
    return jsonify({"message": "Goals updated.", "goals": goal.to_dict()})


@app.route("/api/summary", methods=["GET"])
def get_summary():
    """
    GET /api/summary
    Query params:
        days (int, optional): Number of past days to include. Defaults to 7.
    Returns per-day nutrition totals for the given range.
    """
    try:
        days = int(request.args.get("days", 7))
        if days < 1 or days > 90:
            raise ValueError
    except ValueError:
        return jsonify({"error": "days must be an integer between 1 and 90."}), 400

    from datetime import timedelta
    today = date.today()
    summary = []
    for i in range(days - 1, -1, -1):
        target = today - timedelta(days=i)
        totals = get_daily_totals(target)
        summary.append({"date": target.isoformat(), **totals})

    return jsonify({"days": days, "summary": summary})


# ─── App Bootstrap ────────────────────────────────────────────────────────────

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)

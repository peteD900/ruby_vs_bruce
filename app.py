from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import os
import plotly.express as px
from datetime import datetime

app = Flask(__name__)

# Configuration
DATA_DIR = "data"
ALLOWED_FILES = ["bruce.csv", "dad.csv", "ruby.csv"]


# Load data
def load_data(file_name):
    file_path = os.path.join(DATA_DIR, file_name)
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        # Process data
        df["date"] = pd.to_datetime(df["date"], format="%d/%m/%Y", errors="coerce")
        df["birth_date"] = df.groupby("name")["date"].transform("first")
        df["age_days"] = (df["date"] - df["birth_date"]).dt.days
        df["weight_kg"] = df["weight_grams"] / 1000
        return df
    return None


# Save data
def save_data(df, file_name):
    file_path = os.path.join(DATA_DIR, file_name)
    df.to_csv(file_path, index=False)


@app.route("/")
def index():
    # Get the first available file
    for file_name in ALLOWED_FILES:
        df = load_data(file_name)
        if df is not None:
            return render_template(
                "index.html", data=df.to_dict(orient="records"), file_name=file_name
            )
    return "No data found", 404


@app.route("/update/<file_name>", methods=["GET", "POST"])
def update(file_name):
    if file_name not in ALLOWED_FILES:
        return "Invalid file", 404

    df = load_data(file_name)
    if df is None:
        return "File not found", 404

    if request.method == "POST":
        # Get form data
        name = request.form["name"]
        date = request.form["date"]
        height = request.form["height"]
        weight = request.form["weight"]
        head_circ = request.form["head_circ"]

        # Find the row to update
        row_index = df.index[(df["name"] == name) & (df["date"] == date)].tolist()
        if row_index:
            # Update existing row
            df.at[row_index[0], "height_cm"] = (
                height if height else df.at[row_index[0], "height_cm"]
            )
            df.at[row_index[0], "weight_grams"] = (
                weight if weight else df.at[row_index[0], "weight_grams"]
            )
            df.at[row_index[0], "head_circ_cm"] = (
                head_circ if head_circ else df.at[row_index[0], "head_circ_cm"]
            )

            # Save updated data
            save_data(df, file_name)

            return redirect(url_for("index"))
        else:
            # Add new row
            new_row = {
                "name": name,
                "date": date,
                "height_cm": height,
                "weight_grams": weight,
                "head_circ_cm": head_circ,
            }
            df = df.append(new_row, ignore_index=True)
            save_data(df, file_name)

            return redirect(url_for("index"))

    # Render update form
    return render_template(
        "update.html", data=df.to_dict(orient="records"), file_name=file_name
    )


@app.route("/plot/<file_name>")
def plot(file_name):
    if file_name not in ALLOWED_FILES:
        return "Invalid file", 404

    df = load_data(file_name)
    if df is None:
        return "File not found", 404

    # Create weight vs age plot
    fig = px.line(
        data_frame=df,
        x="age_days",
        y="weight_kg",
        color="name",
        markers=True,
        title="Weight vs. Age (days)",
        labels={"weight_kg": "Weight (kg)", "age_days": "Age (days)"},
    )

    # Convert plot to HTML
    plot_html = fig.to_html(full_html=False)

    return render_template("plot.html", plot=plot_html, file_name=file_name)


if __name__ == "__main__":
    app.run(debug=True)

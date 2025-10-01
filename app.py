from flask import Flask, render_template, request, redirect, url_for
import csv
from pathlib import Path
from datetime import datetime

app = Flask(__name__)

CSV_PATH = Path("survey_responses.csv")
FIELDNAMES = ["timestamp", "name", "age", "q_control"]

def init_csv():
	"""Create CSV with header if it doesn't exist."""
	if not CSV_PATH.exists():
		with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
			writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
			writer.writeheader()

@app.route("/")
def home():
	return "Welcome"

@app.route("/survey", methods=["GET", "POST"])
def survey():
	init_csv()
	if request.method == "POST":
		name = (request.form.get("name") or "").strip()
		age = (request.form.get("age") or "").strip()
		q_control = request.form.get("q_control") or ""

		# small validation
		if not name or not age.isdigit():
			return render_template("survey.html", error="Enter a name and age (numbers only).")

		row = {
			"timestamp": datetime.utcnow().isoformat(timespec="seconds"),
			"name": name,
			"age": age,
			"q_control": q_control,
		}
		with CSV_PATH.open("a", newline="", encoding="utf-8") as f:
			writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
			writer.writerow(row)
		return redirect(url_for("filled"))

	return render_template("survey.html")

@app.route("/filled")
def filled():
	return render_template("filled.html")

if __name__ == "__main__":
	app.run(debug=True)

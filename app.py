from flask import Flask, render_template, request
from datetime import date
from scheduler import Scheduler

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/plan", methods=["POST"])
def plan():
    start_date = request.form.get("fecha")
    apertura_fija = request.form.get("apertura_fija")

    advisors = ["A1", "A2", "A3"]

    scheduler = Scheduler(
        advisors=advisors,
        start_date=date.fromisoformat(start_date),
        holidays=[],
        fixed_opening_worker=apertura_fija if apertura_fija else None
    )

    result = scheduler.solve()
    html_table = result["pivot"].to_html(classes="table", index=False)

    return render_template("resultado.html", tabla=html_table)


if __name__ == "__main__":
    app.run(debug=True)


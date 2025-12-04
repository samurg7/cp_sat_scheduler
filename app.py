from flask import Flask, render_template, request, send_file
from scheduler import Scheduler
import pandas as pd

app = Flask(__name__)

df_global = None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/planear", methods=["POST"])
def planear():
    global df_global

    try:
        asesor_fijo = request.form.get("asesor_fijo")
        semanas = int(request.form.get("semanas"))

        scheduler = Scheduler(2025, 12, asesor_fijo, semanas)
        df_global = scheduler.planear()

        tabla = df_global.to_html(classes="table table-bordered", index=False)
        return render_template("resultado.html", tabla=tabla)

    except Exception as e:
        return render_template("resultado.html", tabla=f"<h3>Error: {e}</h3>")


@app.route("/descargar_csv")
def descargar_csv():
    global df_global
    if df_global is None:
        return "No hay planeación generada."

    ruta = "planeacion.csv"
    df_global.to_csv(ruta, index=False)
    return send_file(ruta, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)


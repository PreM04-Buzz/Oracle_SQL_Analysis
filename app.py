from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
from db_config import get_oracle_connection

app = Flask(__name__)

uploaded_df = None
query_result_df = None

@app.route("/", methods=["GET", "POST"])
def index():
    global uploaded_df

    if request.method == "POST":
        file = request.files["file"]
        if not file:
            return render_template("index.html")

        if file.filename.endswith(".csv"):
            uploaded_df = pd.read_csv(file)
        elif file.filename.endswith(".xlsx"):
            uploaded_df = pd.read_excel(file)
        else:
            return "Only CSV and XLSX files are supported."

        return render_template("index.html", dataset_uploaded=True)

    return render_template("index.html", dataset_uploaded=False)

@app.route("/run_query", methods=["POST"])
def run_query():
    global query_result_df
    query = request.form["query"]

    conn = get_oracle_connection()
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    columns = [c[0] for c in cursor.description]

    query_result_df = pd.DataFrame(rows, columns=columns)

    cursor.close()
    conn.close()

    return render_template("result.html", table=query_result_df.to_html(classes="data-table"))

@app.route("/charts")
def charts():
    global query_result_df
    if query_result_df is None:
        return redirect(url_for("index"))

    labels = query_result_df.iloc[:, 0].tolist()
    values = query_result_df.iloc[:, 1].tolist()

    return render_template("charts.html", labels=labels, values=values)

@app.route("/table")
def table_view():
    global query_result_df
    if query_result_df is None:
        return redirect(url_for("index"))

    return render_template("table.html", table=query_result_df.to_html(classes="data-table"))

if __name__ == "__main__":
    app.run(debug=True)


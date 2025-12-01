from flask import Flask, render_template, request, redirect
import pandas as pd
import sqlite3

app = Flask(__name__)

uploaded_df = None
sql_result_df = None


@app.route("/", methods=["GET", "POST"])
def index():
    global uploaded_df
    file_uploaded = False

    if request.method == "POST":
        file = request.files.get("file")
        if file:
            name = file.filename.lower()
            if name.endswith(".csv"):
                uploaded_df = pd.read_csv(file)
            elif name.endswith(".xlsx"):
                uploaded_df = pd.read_excel(file)
            else:
                return "Unsupported file format"
            file_uploaded = True

    return render_template("index.html", file_uploaded=file_uploaded)


@app.route("/run_sql", methods=["POST"])
def run_sql():
    global uploaded_df, sql_result_df

    if uploaded_df is None:
        return redirect("/")

    query = request.form.get("sql_command")

    try:
        conn = sqlite3.connect(":memory:")
        uploaded_df.to_sql("DATASET", conn, index=False, if_exists="replace")
        sql_result_df = pd.read_sql_query(query, conn)
        conn.close()

        columns = list(sql_result_df.columns)
        rows = sql_result_df.values.tolist()
        return render_template("results.html", columns=columns, rows=rows)

    except Exception as e:
        return render_template("results.html", error=str(e), columns=[], rows=[])


@app.route("/charts")
def charts():
    global sql_result_df

    if sql_result_df is None or sql_result_df.empty:
        return "No data available."

    try:
        labels = sql_result_df.iloc[:, 0].astype(str).tolist()
        values = sql_result_df.iloc[:, 1].astype(float).tolist()
    except:
        return "First column must be labels and second column must be numeric."

    return render_template(
        "charts.html",
        columns=list(sql_result_df.columns),
        rows=sql_result_df.values.tolist(),
        labels=labels,
        values=values
    )


@app.route("/table_view")
def table_view():
    global sql_result_df

    if sql_result_df is None:
        return "No table available."

    columns = list(sql_result_df.columns)
    rows = sql_result_df.values.tolist()

    return render_template("tables.html", columns=columns, rows=rows)


if __name__ == "__main__":
    app.run(debug=True)


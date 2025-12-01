from flask import Flask, render_template, request, redirect
import pandas as pd
from db_config import get_oracle_connection

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
                return "Unsupported file format."
            file_uploaded = True

    return render_template("index.html", file_uploaded=file_uploaded)


@app.route("/run_sql", methods=["POST"])
def run_sql():
    global uploaded_df, sql_result_df

    if uploaded_df is None:
        return redirect("/")

    query = request.form.get("sql_command")

    try:
        conn = get_oracle_connection()
        if conn is None:
            return "Database connection failed."

        cursor = conn.cursor()

        try:
            cursor.execute("DROP TABLE DATASET PURGE")
        except:
            pass

        column_defs = ", ".join([f'"{col}" VARCHAR2(200)' for col in uploaded_df.columns])
        cursor.execute(f"CREATE TABLE DATASET ({column_defs})")

        for _, row in uploaded_df.iterrows():
            placeholders = ", ".join([":"+str(i+1) for i in range(len(row))])
            cursor.execute(
                f"INSERT INTO DATASET VALUES ({placeholders})",
                row.tolist()
            )

        conn.commit()

        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]

        sql_result_df = pd.DataFrame(rows, columns=columns)

        cursor.close()
        conn.close()

        return render_template("results.html", columns=columns, rows=rows, errorstr=None)

    except Exception as e:
        return render_template("results.html", columns=[], rows=[], errorstr=str(e))


@app.route("/charts")
def charts():
    global sql_result_df

    if sql_result_df is None or sql_result_df.empty:
        return "No data available."

    try:
        labels = sql_result_df.iloc[:, 0].astype(str).tolist()
        values = sql_result_df.iloc[:, 1].astype(float).tolist()
    except:
        return "First column must be labels and second numeric."

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

    return render_template(
        "tables.html",
        columns=list(sql_result_df.columns),
        rows=sql_result_df.values.tolist()
    )


if __name__ == "__main__":
    app.run(debug=True)


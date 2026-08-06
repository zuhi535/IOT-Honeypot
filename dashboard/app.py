import time

from flask import Flask, render_template, Response, jsonify

from honeypot.database import (
    count_logs,
    get_last_logs,
    get_top_topic,
    count_today_logs,
    get_latest_log,
    get_topic_counts,
)

from dashboard.charts import (
    bar_chart_topics,
    pie_chart_topics,
    line_chart_events,
)


app = Flask(__name__)


def _build_data():
    """Összegyűjti a dashboardhoz szükséges friss adatokat egy dict-be.
    Ezt használja mind az első betöltés (index), mind az 5 mp-enkénti
    JSON lekérdezés (/api/data)."""

    return {
        "total_logs": count_logs(),
        "today_logs": count_today_logs(),
        "top_topic": get_top_topic(),
        "latest_log": get_latest_log(),
        "logs": get_last_logs(),
        # a chart képek URL-jeihez egyedi verziószám, hogy a böngésző
        # mindig a friss (nem gyorsítótárazott) képet töltse be
        "chart_version": int(time.time()),
    }


@app.route("/")
def index():
    return render_template("index.html", **_build_data())


@app.route("/api/data")
def api_data():
    return jsonify(_build_data())


@app.route("/chart/topics-bar.png")
def chart_topics_bar():
    png_bytes = bar_chart_topics()
    return Response(png_bytes.getvalue(), mimetype="image/png")


@app.route("/chart/topics-pie.png")
def chart_topics_pie():
    png_bytes = pie_chart_topics()
    return Response(png_bytes.getvalue(), mimetype="image/png")


@app.route("/chart/events-line.png")
def chart_events_line():
    png_bytes = line_chart_events()
    return Response(png_bytes.getvalue(), mimetype="image/png")


if __name__ == "__main__":
    app.run(debug=True)
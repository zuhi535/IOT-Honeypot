from flask import Flask, render_template

from honeypot.database import (
    count_logs,
    get_last_logs,
    get_top_topic,
    count_today_logs,
    get_latest_log
)


app = Flask(__name__)


@app.route("/")
def index():

    total_logs = count_logs()
    logs = get_last_logs()
    top_topic = get_top_topic()
    today_logs = count_today_logs()
    latest_log = get_latest_log()

    return render_template(
    "index.html",

    total_logs=total_logs,
    today_logs=today_logs,
    latest_log=latest_log,
    top_topic=top_topic,
    logs=logs
)


if __name__ == "__main__":
    app.run(debug=True)
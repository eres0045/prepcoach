import os

from flask import Flask

from prepcoach.routes import register

app = Flask(__name__, static_folder="docs", static_url_path="")
register(app)

if __name__ == "__main__":
    app.run(host="0.0.0.0",
            port=int(os.environ.get("PORT", "5000")), debug=True)

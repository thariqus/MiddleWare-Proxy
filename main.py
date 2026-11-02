from flask import Flask
from flask_cors import CORS
from api import api
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.json.sort_keys = False

CORS(app, origins=[os.getenv("FRONTEND_ORIGIN")])
app.register_blueprint(api)

if __name__ == "__main__":
    app.run(host=os.getenv("HOST"), port=int(os.getenv("PORT")), debug=True)
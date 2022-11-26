from flask import *
from flask_cors import *
import models
import routes

app = Flask(__name__)
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})
models.init_app(app)
routes.init_app(app)

if __name__ == '__main__':
    # load_model()
    app.run(host='0.0.0.0', port='5000')

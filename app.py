from flask import Flask, request, jsonify
import models
import routes

app = Flask(__name__)
models.init_app(app)
routes.init_app(app)

if __name__ == '__main__':
    # load_model()

    app.run(host='0.0.0.0', port='5000')

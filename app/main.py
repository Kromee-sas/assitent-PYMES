from flask import Flask
from flask_cors import CORS
from routes import main_blueprint

# Initialize Flask app
app = Flask(__name__)

# Enable Cross-Origin Resource Sharing (CORS)
CORS(app)

# Register API routes
app.register_blueprint(main_blueprint)

if __name__ == "__main__":
    app.run(debug=True)

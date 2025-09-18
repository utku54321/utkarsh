import os
from flask import Flask, render_template
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET', 'dev')
    app.config['DATA_DIR'] = os.getenv('DATA_DIR', './data')
    app.config['UPLOAD_DIR'] = os.getenv('UPLOAD_DIR', './uploads')

    os.makedirs(app.config['DATA_DIR'], exist_ok=True)
    os.makedirs(app.config['UPLOAD_DIR'], exist_ok=True)

    from routes.data_routes import bp as data_bp
    from routes.statements_routes import bp as statements_bp
    from routes.analysis_routes import bp as analysis_bp
    from routes.valuation_routes import bp as valuation_bp
    from routes.sports_routes import bp as sports_bp

    app.register_blueprint(data_bp, url_prefix='/data')
    app.register_blueprint(statements_bp, url_prefix='/statements')
    app.register_blueprint(analysis_bp, url_prefix='/analysis')
    app.register_blueprint(valuation_bp, url_prefix='/valuation')
    app.register_blueprint(sports_bp, url_prefix='/sports')

    @app.route('/')
    def index():
        return render_template('index.html')

    return app


if __name__ == '__main__':
    create_app().run(debug=True)

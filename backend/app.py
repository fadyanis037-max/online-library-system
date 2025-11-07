from flask import Flask
from flask_cors import CORS

from backend.config import config
from backend.models import db
from backend.routes import api_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    CORS(app)

    db.init_app(app)

    # Register blueprints (lazy import to prevent circular deps)
    from backend.routes.books import books_bp
    app.register_blueprint(books_bp, url_prefix=f"{api_bp.url_prefix}/books")

    @app.route('/health')
    def health():
        return {"status": "ok"}

    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)



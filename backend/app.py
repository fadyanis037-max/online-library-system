from flask import Flask
from flask_cors import CORS
import threading
import logging
from backend.config import config
from backend.models import db
from backend.ai_engine.summarizer import preload_summarizer
from backend.ai_engine.recommender import preload_recommender
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
        # Keep recommender relatively light; load at startup
        preload_recommender()

    # Start summarizer preload in the background to avoid blocking startup
    def _preload_summarizer_bg(flask_app: Flask):
        try:
            with flask_app.app_context():
                preload_summarizer()
                logging.info("Summarizer preloaded in background")
        except Exception:
            logging.exception("Background summarizer preload failed")

    threading.Thread(
        target=_preload_summarizer_bg,
        args=(app,),
        name="summarizer-preload",
        daemon=True,
    ).start()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=False)



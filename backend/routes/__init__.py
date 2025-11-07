from flask import Blueprint

# Placeholder root blueprint if needed
api_bp = Blueprint("api", __name__, url_prefix="/api")


def register_blueprints(app):
    """Register all API blueprints on the app."""
    from .books import bp as books_bp
    from .users import bp as users_bp
    from .bookings import bp as bookings_bp

    app.register_blueprint(books_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(bookings_bp)


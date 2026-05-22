"""Route registration for library application"""

from .public import init_public_routes
from .auth import init_auth_routes
from .reader import init_reader_routes
from .librarian import init_librarian_routes
from .admin import init_admin_routes


def init_routes(app):
    """Initialize all application routes"""
    init_public_routes(app)
    init_auth_routes(app)
    init_reader_routes(app)
    init_librarian_routes(app)
    init_admin_routes(app)
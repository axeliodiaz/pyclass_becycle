"""Settings package for the application."""

from .base import *
try:
    from .local import *
except ImportError:
    pass 
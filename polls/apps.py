"""App config for KU Polls."""
from django.apps import AppConfig


class PollsConfig(AppConfig):
    """Set up configurations for polls app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'polls'

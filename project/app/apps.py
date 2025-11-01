from django.apps import AppConfig


class AppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app"

    def ready(self) -> None:
        """Подключение сигналов при готовности приложения"""
        import app.signals  # noqa: F401

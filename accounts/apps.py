from django.apps import AppConfig


# Configuration class for the 'accounts' app.
class AccountsConfig(AppConfig):
    # Defines the type of primary key to use for models in this app.
    default_auto_field = "django.db.models.BigAutoField"

    # The name of the app. Django uses this to locate app files.
    name = "accounts"

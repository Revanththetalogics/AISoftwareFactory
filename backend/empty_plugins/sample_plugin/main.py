"""Sample Plugin Main Module"""


def initialize(config):
    """Initialize the plugin with configuration."""
    print(f"Sample plugin initialized with config: {config}")
    return True


def on_startup():
    """Called when the application starts."""
    print("Sample plugin startup hook executed")


def on_user_action(action_data):
    """Called when user performs an action."""
    print(f"Sample plugin received user action: {action_data}")
    return {"processed": True, "plugin_response": "Action handled by sample plugin"}


def cleanup():
    """Clean up plugin resources."""
    print("Sample plugin cleaned up")

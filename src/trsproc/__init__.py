from importlib import resources
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

# Read URL of the Real Python feed from config file
_cfg = tomllib.loads(resources.read_text("trsproc", "config.toml"))
FLAGS = _cfg["flags"]
CORRECTIONS = _cfg["corrections"]

__version__ = "1.4.3"
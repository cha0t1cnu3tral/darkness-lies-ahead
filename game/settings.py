import json
from .paths import USER

DEFAULTS = {
    "master": 80,
    "music": 30,
    "ambience": 45,
    "effects": 75,
    "speech": True,
    "duck": True,
    "high_contrast": False,
}


def load():
    try:
        values = json.loads((USER / "settings.json").read_text(encoding="utf-8"))
        if not isinstance(values, dict):
            return dict(DEFAULTS)
        result = dict(DEFAULTS)
        for key, default in DEFAULTS.items():
            value = values.get(key, default)
            if isinstance(default, bool):
                result[key] = value if isinstance(value, bool) else default
            else:
                result[key] = max(0, min(100, value)) if type(value) is int else default
        return result
    except OSError, ValueError:
        return dict(DEFAULTS)


def save(values):
    USER.mkdir(parents=True, exist_ok=True)
    path = USER / "settings.tmp"
    path.write_text(json.dumps(values, indent=2), encoding="utf-8")
    path.replace(USER / "settings.json")

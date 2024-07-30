import os
from typing import Optional

def get_bool(name: str, default_value: Optional[bool] = None) -> bool:
    if default_value is None:
        default_value = False
    true_ = ('true', '1', 't')  # Add more entries if you want, like: `y`, `yes`, `on`, ...
    false_ = ('false', '0', 'f')  # Add more entries if you want, like: `n`, `no`, `off`, ...
    value = os.getenv(name, None)
    if value is None:
        return default_value
    if value.lower() in true_:
        return True
    if value.lower() in false_:
        return False
    raise ValueError(f'Invalid value `{value}` for variable `{name}`')


def get_int(name: str, default_value: Optional[int] = None) -> int:
    if default_value is None:
        default_value = 0
    value = os.getenv(name, None)
    if value is None:
        return default_value
    try:
        value = int(value)
    except ValueError as e:
        return default_value
    return value
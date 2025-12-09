# common/validators.py

def validate_int(value, min_value=None, max_value=None):
    """
    Validates and converts an input to integer within an optional range.

    :param value: Input value (usually from UI entry)
    :param min_value: Minimum allowed value
    :param max_value: Maximum allowed value
    :return: Integer value if valid
    :raises ValueError: If validation fails
    """
    if value is None or str(value).strip() == "":
        raise ValueError("Input cannot be empty")

    if not str(value).isdigit():
        raise ValueError("Input must be a valid integer")

    value = int(value)

    if min_value is not None and value < min_value:
        raise ValueError(f"Value must be ≥ {min_value}")

    if max_value is not None and value > max_value:
        raise ValueError(f"Value must be ≤ {max_value}")

    return value


def validate_choice(value, allowed_values):
    """
    Validates whether the input is one of the allowed choices.

    :param value: User input
    :param allowed_values: Iterable of valid values
    :return: Value if valid
    :raises ValueError: If invalid
    """
    if value not in allowed_values:
        raise ValueError(f"Input must be one of {allowed_values}")
    return value


def validate_non_empty_string(value):
    """
    Validates that input is a non-empty string.

    :param value: User input
    :return: Stripped string
    :raises ValueError: If invalid
    """
    if value is None or str(value).strip() == "":
        raise ValueError("Input cannot be empty")
    return str(value).strip()

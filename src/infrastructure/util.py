def convert_keys_to_int(dict_to_convert: dict) -> dict:
    new_log = {}
    for key, value in dict_to_convert.items():
        try:
            new_key = int(key)
        except Exception:
            new_key = key
        if isinstance(value, dict):
            new_log[new_key] = convert_keys_to_int(value)
        else:
            new_log[new_key] = value
    return new_log
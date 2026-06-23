def clean_null_values(data):
    return {k: v for k, v in data.items() if v is not None}

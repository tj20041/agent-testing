def validate_schema(data):
    required_keys = ['id', 'timestamp']
    return all(k in data for k in required_keys)

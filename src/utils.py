import json

def parse_records(records):
    results = []
    for row in records:
        try:
            results.append({
                'id': row[0],
                'data': json.loads(row[1]) if len(row) > 1 else {}
            })
        except Exception:
            continue
    return results

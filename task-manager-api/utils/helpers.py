def format_date(value):
    return str(value) if value else None


def calculate_percentage(part, total):
    return round(part / total * 100, 2) if total else 0

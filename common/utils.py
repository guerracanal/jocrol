from datetime import datetime

def format_date_filter(value, format='%d/%m/%Y'):
    if not value: return ""
    try:
        date_obj = datetime.strptime(value.split(' ')[0], '%Y-%m-%d')
        return date_obj.strftime(format)
    except (ValueError, TypeError):
        return value

def format_datetime_filter(value, format='%d/%m/%Y %H:%M'):
    if not value: return ""
    try:
        date_obj = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        return date_obj.strftime(format)
    except (ValueError, TypeError):
        return value

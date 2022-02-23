from datetime import date


def year(request):
    """Добавляет переменную с текущим годом."""
    now = date.today()
    return {
        'year': now.year
    }

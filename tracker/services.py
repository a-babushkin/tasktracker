def get_full_name(emp):
    """Возвращает полное имя пользователя"""
    first_name = emp.first_name or ""
    last_name = emp.last_name or ""
    full_name = (first_name + " " + last_name).strip()
    return full_name if full_name else emp.username

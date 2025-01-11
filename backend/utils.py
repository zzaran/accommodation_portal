from datetime import datetime

def calculate_age_group(date_of_birth):
    """Calculate age group from date of birth."""
    today = datetime.today()
    age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
    if age < 18:
        return "Under 18"
    elif 18 <= age <= 25:
        return "18-25"
    elif 26 <= age <= 35:
        return "26-35"
    elif 36 <= age <= 50:
        return "36-50"
    else:
        return "51+"

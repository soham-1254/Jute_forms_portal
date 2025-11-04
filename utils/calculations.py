def calculate_actual_converted(weight, mr_percent):
    """
    Calculate actual weight and converted weight based on MR%.
    Formula:
      actual = weight * (1 - MR% / 100)
      converted = actual * 0.04409
    """
    try:
        actual = weight * (1 - (mr_percent / 100))
        converted = actual * 0.04409
        return round(actual, 2), round(converted, 2)
    except Exception:
        return 0.0, 0.0

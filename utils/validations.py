def validate_inputs(machine_no, w1, mr1, w2, mr2):
    """
    Validates machine number and weight/MR% values.
    Returns: (is_valid: bool, message: str)
    """
    if machine_no <= 0:
        return False, "Machine number must be greater than 0."
    if any(w < 0 for w in [w1, w2]):
        return False, "Weight values cannot be negative."
    if any(mr < 0 or mr > 100 for mr in [mr1, mr2]):
        return False, "MR% must be between 0 and 100."
    return True, "OK"

def find_errors(code):
    errors = []
    if 'print' in code:
        errors.append("Use of print statement found.")
    return errors

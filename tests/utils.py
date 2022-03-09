import os


def load_data(filepath):
    if not os.path.exists(filepath):
        return None

    with open(filepath, 'r') as f:
        return f.read()

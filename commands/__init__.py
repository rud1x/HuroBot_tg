COMMANDS = []

def register(func):
    COMMANDS.append(func)
    return func

def get_all():
    return list(COMMANDS)
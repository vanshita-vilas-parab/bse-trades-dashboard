pull_status = "idle"


def set_status(status):
    global pull_status
    pull_status = status


def get_status():
    return pull_status
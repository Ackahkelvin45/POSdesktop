import socket

def check_internet_connection():
    """
    Check internet connectivity by attempting to resolve a DNS
    """
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except (socket.error, socket.timeout):
        return False
import queue

clients = []


def add_client():
    client_queue = queue.Queue()
    clients.append(client_queue)
    return client_queue


def remove_client(client_queue):
    if client_queue in clients:
        clients.remove(client_queue)


def notify_clients(event):
    for client_queue in clients:
        client_queue.put(event)
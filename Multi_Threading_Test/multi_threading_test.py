import threading

def print_count():
    msg = "Hello World"
    return msg

if __name__ == '__main__':
    t1 = threading.Thread(target = print_count)
    t1.start()
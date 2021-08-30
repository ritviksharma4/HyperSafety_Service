import threading

count = 1

def print_count():

    global count
    while(count < 10):
        print("Task assigned to thread: {}".format(threading.current_thread().name))
        print(count)
        count += 1

if __name__ == '__main__':
    t1 = threading.Thread(target = print_count)
    t2 = threading.Thread(target = print_count)
    t1.start()
    t2.start()
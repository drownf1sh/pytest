from multiprocessing import Process,Lock,Queue

def save_to_queue(index, my_queue):
    my_queue.put(index)


if __name__ == "__main__":
    process_array = []
    my_queue = Queue()
    for i in range(10):
        p = Process(target=save_to_queue, args=(i, my_queue))
        process_array.append(p)
        p.start()
    for p in process_array:
        p.join()

    while True:
        print(my_queue.get())



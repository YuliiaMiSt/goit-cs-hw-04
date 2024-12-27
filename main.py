import os
import time
import threading
import multiprocessing
from queue import Queue

# Створюємо функцію для пошуку ключових слів у файлі
def search_keywords_in_file(file_path, keywords):
    results = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            for keyword in keywords:
                if keyword in content:
                    results.setdefault(keyword, []).append(file_path)
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
    return results

# Об'єднаннуємо результати з декількох процесів
def merge_results(global_results, local_results):
    for keyword, files in local_results.items():
        if keyword not in global_results:
            global_results[keyword] = []
        global_results[keyword].extend(files)

# Версія з threading
def threading_search(files, keywords):
    def worker(file_subset, output_queue):
        local_results = {}
        for file in file_subset:
            local_results.update(search_keywords_in_file(file, keywords))
        output_queue.put(local_results)

    output_queue = Queue()
    threads = []
    n_threads = min(4, len(files)) 
    chunk_size = len(files) // n_threads

    for i in range(n_threads):
        start = i * chunk_size
        end = None if i == n_threads - 1 else (i + 1) * chunk_size
        thread = threading.Thread(target=worker, args=(files[start:end], output_queue))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    global_results = {}
    while not output_queue.empty():
        merge_results(global_results, output_queue.get())

    return global_results

# Версія з multiprocessing
def multiprocessing_search(files, keywords):
    def worker(file_subset, output_queue):
        local_results = {}
        for file in file_subset:
            local_results.update(search_keywords_in_file(file, keywords))
        output_queue.put(local_results)

    output_queue = multiprocessing.Queue()
    processes = []
    n_processes = min(4, len(files))
    chunk_size = len(files) // n_processes

    for i in range(n_processes):
        start = i * chunk_size
        end = None if i == n_processes - 1 else (i + 1) * chunk_size
        process = multiprocessing.Process(target=worker, args=(files[start:end], output_queue))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    global_results = {}
    while not output_queue.empty():
        merge_results(global_results, output_queue.get())

    return global_results

# Основна функція для тестування
def main():
    keywords = ["error", "warning", "critical"]
    directory = "./test_files" 

    # Отримання списку всіх текстових файлів
    files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.txt')]

    print("Starting threading version...")
    start_time = time.time()
    threading_results = threading_search(files, keywords)
    threading_time = time.time() - start_time

    print("Starting multiprocessing version...")
    start_time = time.time()
    multiprocessing_results = multiprocessing_search(files, keywords)
    multiprocessing_time = time.time() - start_time

    print("\nResults (Threading):")
    print(threading_results)
    print(f"Execution time: {threading_time:.2f} seconds")

    print("\nResults (Multiprocessing):")
    print(multiprocessing_results)
    print(f"Execution time: {multiprocessing_time:.2f} seconds")

if __name__ == "__main__":
    main()

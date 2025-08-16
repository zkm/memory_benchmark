import time
import numpy as np
import psutil

RESULTS_FILE = "memory_benchmark_results.txt"


def memory_read_write_test(size_mb=1024):
    print(f"Allocating {size_mb}MB array...")
    arr = np.random.rand(size_mb * 1024 * 1024 // 8)  # float64 = 8 bytes
    print("Starting write test...")
    start = time.time()
    arr[:] = 1.2345
    write_time = time.time() - start
    print(f"Write time: {write_time:.3f}s")

    print("Starting read test...")
    start = time.time()
    _ = arr.sum()
    read_time = time.time() - start
    print(f"Read time: {read_time:.3f}s")

    return write_time, read_time


def log_results(write_time, read_time, size_mb):
    with open(RESULTS_FILE, "a") as f:
        f.write(f"Test size: {size_mb}MB\n")
        f.write(f"Write time: {write_time:.3f}s\n")
        f.write(f"Read time: {read_time:.3f}s\n")
        f.write(f"RAM total: {psutil.virtual_memory().total / (1024**3):.2f} GB\n")
        f.write(f"RAM available: {psutil.virtual_memory().available / (1024**3):.2f} GB\n")
        f.write(f"Timestamp: {time.ctime()}\n")
        f.write("-"*40 + "\n")


def main():
    size_mb = 8192  # 8GB test
    write_time, read_time = memory_read_write_test(size_mb)
    log_results(write_time, read_time, size_mb)
    print(f"Results logged to {RESULTS_FILE}")


if __name__ == "__main__":
    main()

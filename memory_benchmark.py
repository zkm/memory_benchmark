import time
import numpy as np
import psutil
from colorama import Fore, Style, init
import argparse
import platform
import os
import csv

init(autoreset=True)

RESULTS_FILE = "memory_benchmark_results.txt"
CSV_FILE = "memory_benchmark_results.csv"


def memory_read_write_test(size_mb=1024):
    print(Fore.CYAN + f"🧠 Allocating {size_mb}MB array...")
    arr = np.random.rand(size_mb * 1024 * 1024 // 8)  # float64 = 8 bytes
    print(Fore.YELLOW + "🟡 Starting write test...")
    start = time.time()
    arr[:] = 1.2345
    write_time = time.time() - start
    print(Fore.GREEN + f"🟢 Write time: {write_time:.3f}s")

    print(Fore.YELLOW + "🟡 Starting read test...")
    start = time.time()
    _ = arr.sum()
    read_time = time.time() - start
    print(Fore.GREEN + f"🟢 Read time: {read_time:.3f}s")

    return write_time, read_time


def log_results(write_time, read_time, size_mb):
    cpu_info = platform.processor()
    with open(RESULTS_FILE, "a") as f:
        f.write(f"Test size: {size_mb}MB\n")
        f.write(f"Write time: {write_time:.3f}s\n")
        f.write(f"Read time: {read_time:.3f}s\n")
        f.write(f"RAM total: {psutil.virtual_memory().total / (1024**3):.2f} GB\n")
        f.write(f"RAM available: {psutil.virtual_memory().available / (1024**3):.2f} GB\n")
        f.write(f"Timestamp: {time.ctime()}\n")
        if cpu_info:
            f.write(f"CPU: {cpu_info}\n")
        f.write(f"Machine: {platform.machine()}\n")
        f.write(f"OS: {platform.system()} {platform.release()}\n")
        f.write("-"*40 + "\n")

    # Write to CSV
    write_header = not os.path.exists(CSV_FILE)
    with open(CSV_FILE, "a", newline='') as csvfile:
        writer = csv.writer(csvfile)
        if write_header:
            headers = [
                "Test Size (MB)", "Write Time (s)", "Read Time (s)",
                "RAM Total (GB)", "RAM Available (GB)", "Timestamp",
                "CPU", "Machine", "OS"
            ]
            writer.writerow(headers)
        writer.writerow([
            size_mb,
            f"{write_time:.3f}",
            f"{read_time:.3f}",
            f"{psutil.virtual_memory().total / (1024**3):.2f}",
            f"{psutil.virtual_memory().available / (1024**3):.2f}",
            time.ctime(),
            platform.processor(),
            platform.machine(),
            f"{platform.system()} {platform.release()}"
        ])


def main():
    parser = argparse.ArgumentParser(description="Memory Benchmark Script")
    parser.add_argument(
        "--sizes",
        nargs="+",
        type=int,
        help="List of test sizes in MB (e.g. --sizes 1024 2048 4096 8192)",
        default=[1024, 2048, 4096, 8192]
    )
    args = parser.parse_args()
    test_sizes = args.sizes

    print(Fore.MAGENTA + Style.BRIGHT + "\n📊 Memory Benchmark Results\n" + "="*30)
    cpu_info = platform.processor()
    machine_info = f"Machine: {platform.machine()}"
    os_info = f"OS: {platform.system()} {platform.release()}"
    sysinfo = f"{machine_info} | {os_info}"
    if cpu_info:
        print(Fore.YELLOW + f"System Info: CPU: {cpu_info} | {sysinfo}")
    else:
        print(Fore.YELLOW + f"System Info: {sysinfo}")

    headers = f"{'Size':<8}{'Write Time':<15}{'Read Time':<15}{'Total RAM':<12}{'Available':<12}"
    print(headers)
    print("-"*62)

    for size_mb in test_sizes:
        print(Fore.BLUE + f"\n🧪 Testing {size_mb // 1024}GB...")
        write_time, read_time = memory_read_write_test(size_mb)
        total_ram = psutil.virtual_memory().total / (1024**3)
        avail_ram = psutil.virtual_memory().available / (1024**3)
        size_str = str(size_mb // 1024) + 'GB'
        result_line = f"{size_str:<8}{write_time:<15.3f}{read_time:<15.3f}{total_ram:<12.2f}{avail_ram:<12.2f} 📝"
        print(result_line)
        log_results(write_time, read_time, size_mb)

    print(Fore.MAGENTA + Style.BRIGHT + f"\n✅ Results logged to {RESULTS_FILE} and {CSV_FILE}\n")


if __name__ == "__main__":
    main()

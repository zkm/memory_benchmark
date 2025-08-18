import argparse
import csv
import os
import platform
import subprocess
import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import psutil
from colorama import Fore, Style, init

init(autoreset=True)

RESULTS_FILE = "memory_benchmark_results.txt"
CSV_FILE = "memory_benchmark_results.csv"


def format_size(size_mb: int) -> str:
    """
    Convert a size in megabytes to a human-friendly string.
    Shows MB for sizes < 1024, otherwise shows GB.
    """
    if size_mb < 1024:
        return f"{size_mb} MB"
    else:
        gb = size_mb / 1024
        return f"{gb:.1f} GB"


def get_cpu_info():
    """
    Try to get a user-friendly CPU name for the current system.
    Falls back to architecture if not available.
    """
    cpu_info = platform.processor()
    if cpu_info:
        return cpu_info

    try:
        if platform.system() == "Linux":
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    if line.startswith("model name"):
                        return line.split(":", 1)[1].strip()
        elif platform.system() == "Darwin":  # macOS
            result = subprocess.run(
                ["sysctl", "-n", "machdep.cpu.brand_string"],
                capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        elif platform.system() == "Windows":
            result = subprocess.run(
                ["wmic", "cpu", "get", "name"],
                capture_output=True, text=True, check=True
            )
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                return lines[1].strip()
    except Exception:
        pass

    return f"{platform.machine()} processor"


def memory_read_write_test(size_mb=1024, quiet=False):
    """
    Allocate a large array and measure how fast we can write to and read from it.
    Returns write and read times in seconds.
    """
    msg = f"Allocating an array of {format_size(size_mb)}..."
    print(msg if quiet else Fore.CYAN + f"🧠 {msg}")

    try:
        arr = np.empty(size_mb * 1024 * 1024 // 8, dtype=np.float64)
    except MemoryError:
        msg = f"Could not allocate {format_size(size_mb)} (not enough memory)"
        print(msg if quiet else Fore.RED + f"❌ {msg}")
        return None, None

    # Write benchmark
    print("Measuring write speed..." if quiet else Fore.YELLOW + "🟡 Measuring write speed...")
    start = time.perf_counter()
    arr[:] = 1.2345
    write_time = time.perf_counter() - start
    print(
        f"Write completed in {write_time:.3f} seconds"
        if quiet else Fore.GREEN + f"🟢 Write completed in {write_time:.3f} seconds"
    )

    # Read benchmark
    print("Measuring read speed..." if quiet else Fore.YELLOW + "🟡 Measuring read speed...")
    start = time.perf_counter()
    total = 0.0
    target_samples = 100_000
    step = max(1, len(arr) // target_samples)
    for i in range(0, len(arr), step):
        total += arr[i]
    read_time = time.perf_counter() - start
    print(
        f"Read completed in {read_time:.3f} seconds"
        if quiet else Fore.GREEN + f"🟢 Read completed in {read_time:.3f} seconds"
    )

    return write_time, read_time


def log_results(write_time, read_time, size_mb, csv_only=False):
    """
    Save the results of a benchmark run to text and CSV files.
    """
    cpu_info = get_cpu_info()
    vmem = psutil.virtual_memory()

    if not csv_only:
        with open(RESULTS_FILE, "a") as f:
            f.write(f"Test size: {format_size(size_mb)}\n")
            f.write(f"Write time: {write_time:.3f} seconds\n")
            f.write(f"Read time: {read_time:.3f} seconds\n")
            f.write(
                f"RAM total: {vmem.total / (1024**3):.2f} GB\n"
            )
            f.write(
                f"RAM available: {vmem.available / (1024**3):.2f} GB\n"
            )
            f.write(f"Timestamp: {time.ctime()}\n")
            f.write(f"CPU: {cpu_info}\n")
            f.write(f"Machine: {platform.machine()}\n")
            f.write(
                f"OS: {platform.system()} {platform.release()}\n"
            )
            f.write("-" * 40 + "\n")

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
            f"{vmem.total / (1024**3):.2f}",
            f"{vmem.available / (1024**3):.2f}",
            time.ctime(),
            cpu_info,
            platform.machine(),
            f"{platform.system()} {platform.release()}"
        ])


def main():
    parser = argparse.ArgumentParser(description="Memory Benchmark: Test your system's memory speed in a friendly way!")
    parser.add_argument("--sizes", nargs="+", type=int,
                        help="List of test sizes in MB (e.g. --sizes 1024 2048 4096 8192)",
                        default=[1024, 2048, 4096, 8192])
    parser.add_argument("--runs", type=int, default=1,
                        help="Number of runs to average for each test size (default: 1)")
    parser.add_argument("--csv-only", action="store_true",
                        help="Only output to CSV file, skip text log file")
    parser.add_argument("--quiet", action="store_true",
                        help="Suppress colorful output and emojis (CI/CD friendly)")
    parser.add_argument("--plot", action="store_true",
                        help="Generate performance plots from CSV results and exit")
    args = parser.parse_args()
    test_sizes = args.sizes

    if args.plot:
        plot_results(CSV_FILE)
        return

    # Friendly header
    print("\nMemory Benchmark Results" if args.quiet
          else Fore.MAGENTA + Style.BRIGHT + "\n📊 Memory Benchmark Results")
    print("=" * 40)

    cpu_info = get_cpu_info()
    sysinfo = f"Machine: {platform.machine()} | OS: {platform.system()} {platform.release()}"
    print(
        f"System Info: CPU: {cpu_info} | {sysinfo}"
        if args.quiet else Fore.YELLOW + f"System Info: CPU: {cpu_info} | {sysinfo}"
    )

    runs_info = f" (average of {args.runs} runs)" if args.runs > 1 else ""
    headers = (
        f"{'Size':<10}{'Write Time':<18}{'Read Time':<18}"
        f"{'Total RAM':<14}{'Available':<14}{runs_info}"
    )
    print(headers)
    print("-" * (74 + len(runs_info)))

    for size_mb in test_sizes:
        label = format_size(size_mb)
        print(
            f"\nTesting {label}..."
            if args.quiet else Fore.BLUE + f"\n🧪 Testing {label}..."
        )

        write_times, read_times = [], []
        for run in range(args.runs):
            if args.runs > 1 and not args.quiet:
                print(f"  Run {run + 1} of {args.runs}")

            write_time, read_time = memory_read_write_test(size_mb, args.quiet)
            if write_time is None or read_time is None:
                msg = f"Skipping {label} (not enough memory)"
                print(
                    msg if args.quiet else Fore.RED + f"⏭️  {msg}"
                )
                break

            write_times.append(write_time)
            read_times.append(read_time)

        if not write_times:
            continue

        avg_write_time = sum(write_times) / len(write_times)
        avg_read_time = sum(read_times) / len(read_times)
        vmem = psutil.virtual_memory()
        total_ram = vmem.total / (1024**3)
        avail_ram = vmem.available / (1024**3)

        result_line = (
            f"{label:<10}{avg_write_time:<18.3f}{avg_read_time:<18.3f}"
            f"{total_ram:<14.2f}{avail_ram:<14.2f}"
        )
        if not args.quiet:
            result_line += " 📝"
        print(result_line)

        log_results(avg_write_time, avg_read_time, size_mb, args.csv_only)

    log_files = [CSV_FILE] if args.csv_only else [RESULTS_FILE, CSV_FILE]
    print(
        f"\nResults saved to {' and '.join(log_files)}"
        if args.quiet else Fore.MAGENTA + Style.BRIGHT +
        f"\n✅ Results saved to {' and '.join(log_files)}\n"
    )


def plot_results(csv_file):
    """Read CSV results and generate read/write performance plots."""
    df = pd.read_csv(csv_file)
    sizes = df["Test Size (MB)"]
    write_times = df["Write Time (s)"]
    read_times = df["Read Time (s)"]

    plt.figure(figsize=(8, 6))
    plt.plot(
        sizes, write_times, marker='o', label='Write Time'
    )
    plt.plot(
        sizes, read_times, marker='o', label='Read Time'
    )
    plt.xlabel('Test Size (MB)')
    plt.ylabel('Time (s)')
    plt.title('Memory Read/Write Performance')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('memory_benchmark_performance.png')
    plt.show()
    print("Plot saved as memory_benchmark_performance.png")


if __name__ == "__main__":
    main()

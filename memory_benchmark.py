import argparse
import csv
import os
import platform
import time

import numpy as np
import psutil
from colorama import Fore, Style, init

init(autoreset=True)

RESULTS_FILE = "memory_benchmark_results.txt"
CSV_FILE = "memory_benchmark_results.csv"


def get_cpu_info():
    """Get CPU information in a portable way across different operating systems."""
    # Try platform.processor() first
    cpu_info = platform.processor()
    if cpu_info:
        return cpu_info

    # Fallback methods for different OSes
    try:
        if platform.system() == "Linux":
            # Try reading from /proc/cpuinfo
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    if line.startswith("model name"):
                        return line.split(":", 1)[1].strip()
        elif platform.system() == "Darwin":  # macOS
            import subprocess
            result = subprocess.run(
                ["sysctl", "-n", "machdep.cpu.brand_string"],
                capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        elif platform.system() == "Windows":
            import subprocess
            result = subprocess.run(
                ["wmic", "cpu", "get", "name"],
                capture_output=True, text=True, check=True
            )
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                return lines[1].strip()
    except (FileNotFoundError, subprocess.SubprocessError, IndexError):
        pass

    # Final fallback
    return f"{platform.machine()} processor"


def memory_read_write_test(size_mb=1024, quiet=False):
    if quiet:
        print(f"Allocating {size_mb}MB array...")
    else:
        print(Fore.CYAN + f"🧠 Allocating {size_mb}MB array...")

    try:
        # Use np.empty for uninitialized memory (faster allocation)
        arr = np.empty(size_mb * 1024 * 1024 // 8, dtype=np.float64)
    except MemoryError:
        if quiet:
            print(f"Failed to allocate {size_mb}MB - insufficient memory")
        else:
            print(Fore.RED + f"❌ Failed to allocate {size_mb}MB - insufficient memory")
        return None, None

    if quiet:
        print("Starting write test...")
    else:
        print(Fore.YELLOW + "🟡 Starting write test...")
    start = time.perf_counter()
    arr[:] = 1.2345
    write_time = time.perf_counter() - start

    if quiet:
        print(f"Write time: {write_time:.3f}s")
    else:
        print(Fore.GREEN + f"🟢 Write time: {write_time:.3f}s")

    if quiet:
        print("Starting read test...")
    else:
        print(Fore.YELLOW + "🟡 Starting read test...")
    start = time.perf_counter()
    # More realistic memory bandwidth test - iterate through memory
    # This tests actual memory access patterns rather than optimized NumPy operations
    total = 0.0
    step = max(1, len(arr) // 100000)  # Sample ~100k elements to avoid too many iterations
    for i in range(0, len(arr), step):
        total += arr[i]
    read_time = time.perf_counter() - start

    if quiet:
        print(f"Read time: {read_time:.3f}s")
    else:
        print(Fore.GREEN + f"🟢 Read time: {read_time:.3f}s")

    return write_time, read_time


def log_results(write_time, read_time, size_mb, csv_only=False):
    cpu_info = get_cpu_info()
    vmem = psutil.virtual_memory()

    # Write to text log file unless csv_only is specified
    if not csv_only:
        with open(RESULTS_FILE, "a") as f:
            f.write(f"Test size: {size_mb}MB\n")
            f.write(f"Write time: {write_time:.3f}s\n")
            f.write(f"Read time: {read_time:.3f}s\n")
            f.write(f"RAM total: {vmem.total / (1024**3):.2f} GB\n")
            f.write(f"RAM available: {vmem.available / (1024**3):.2f} GB\n")
            f.write(f"Timestamp: {time.ctime()}\n")
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
            f"{vmem.total / (1024**3):.2f}",
            f"{vmem.available / (1024**3):.2f}",
            time.ctime(),
            get_cpu_info(),
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
    parser.add_argument(
        "--runs",
        type=int,
        default=1,
        help="Number of runs to average for each test size (default: 1)"
    )
    parser.add_argument(
        "--csv-only",
        action="store_true",
        help="Only output to CSV file, skip text log file"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress colorful output and emojis (CI/CD friendly)"
    )
    args = parser.parse_args()
    test_sizes = args.sizes

    # Handle quiet mode for output formatting
    if args.quiet:
        print("\nMemory Benchmark Results")
        print("=" * 30)
    else:
        print(Fore.MAGENTA + Style.BRIGHT + "\n📊 Memory Benchmark Results\n" + "="*30)

    cpu_info = get_cpu_info()
    machine_info = f"Machine: {platform.machine()}"
    os_info = f"OS: {platform.system()} {platform.release()}"
    sysinfo = f"{machine_info} | {os_info}"

    if args.quiet:
        print(f"System Info: CPU: {cpu_info} | {sysinfo}")
    else:
        print(Fore.YELLOW + f"System Info: CPU: {cpu_info} | {sysinfo}")

    if args.runs > 1:
        runs_info = f" (averaged over {args.runs} runs)"
    else:
        runs_info = ""

    headers = f"{'Size':<8}{'Write Time':<15}{'Read Time':<15}{'Total RAM':<12}{'Available':<12}{runs_info}"
    print(headers)
    print("-" * (62 + len(runs_info)))

    for size_mb in test_sizes:
        if args.quiet:
            print(f"\nTesting {size_mb // 1024}GB...")
        else:
            print(Fore.BLUE + f"\n🧪 Testing {size_mb // 1024}GB...")

        # Run multiple times and average if specified
        write_times = []
        read_times = []

        for run in range(args.runs):
            if args.runs > 1 and not args.quiet:
                print(f"  Run {run + 1}/{args.runs}")

            write_time, read_time = memory_read_write_test(size_mb, args.quiet)

            # Skip if allocation failed
            if write_time is None or read_time is None:
                if args.quiet:
                    print(f"Skipping {size_mb // 1024}GB test due to memory allocation failure")
                else:
                    print(Fore.RED + f"⏭️  Skipping {size_mb // 1024}GB test due to memory allocation failure")
                break

            write_times.append(write_time)
            read_times.append(read_time)

        # Skip to next size if all runs failed
        if not write_times:
            continue

        # Calculate averages
        avg_write_time = sum(write_times) / len(write_times)
        avg_read_time = sum(read_times) / len(read_times)

        vmem = psutil.virtual_memory()
        total_ram = vmem.total / (1024**3)
        avail_ram = vmem.available / (1024**3)
        size_str = str(size_mb // 1024) + 'GB'

        if args.quiet:
            result_line = f"{size_str:<8}{avg_write_time:<15.3f}{avg_read_time:<15.3f}{total_ram:<12.2f}{avail_ram:<12.2f}"
        else:
            result_line = f"{size_str:<8}{avg_write_time:<15.3f}{avg_read_time:<15.3f}{total_ram:<12.2f}{avail_ram:<12.2f} 📝"

        print(result_line)
        log_results(avg_write_time, avg_read_time, size_mb, args.csv_only)

    # Final message
    log_files = []
    if not args.csv_only:
        log_files.append(RESULTS_FILE)
    log_files.append(CSV_FILE)

    if args.quiet:
        print(f"\nResults logged to {' and '.join(log_files)}")
    else:
        print(Fore.MAGENTA + Style.BRIGHT + f"\n✅ Results logged to {' and '.join(log_files)}\n")


if __name__ == "__main__":
    main()

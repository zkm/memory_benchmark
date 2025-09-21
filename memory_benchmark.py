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
BW_CSV_FILE = "memory_benchmark_results_with_bw.csv"


def _bandwidth_gbps(size_mb: int, seconds: float) -> float:
    """Compute throughput in GB/s (GiB/s) from size in MB and elapsed seconds.
    Uses binary units: 1024 MB = 1 GB.
    """
    if seconds <= 0:
        return float("inf")
    return (size_mb / 1024.0) / seconds


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


def memory_read_write_test(size_mb=1024, quiet=False, read_mode="full"):
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
    # Default to touching all bytes for realistic, size-scaled timing.
    # Use numpy's vectorized reduction to ensure every element is read.
    if read_mode == "full":
        total = float(np.sum(arr, dtype=np.float64))
    else:
        # Backward-compatible sampling mode: reads a subset of elements,
        # which yields nearly constant time regardless of array size.
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

    # Also write an extended CSV with bandwidth columns for convenience.
    w_bw = _bandwidth_gbps(size_mb, write_time)
    r_bw = _bandwidth_gbps(size_mb, read_time)
    bw_header = not os.path.exists(BW_CSV_FILE)
    with open(BW_CSV_FILE, "a", newline='') as csvfile:
        writer = csv.writer(csvfile)
        if bw_header:
            bw_headers = [
                "Test Size (MB)", "Write Time (s)", "Read Time (s)",
                "Write Bandwidth (GB/s)", "Read Bandwidth (GB/s)",
                "RAM Total (GB)", "RAM Available (GB)", "Timestamp",
                "CPU", "Machine", "OS"
            ]
            writer.writerow(bw_headers)
        writer.writerow([
            size_mb,
            f"{write_time:.3f}",
            f"{read_time:.3f}",
            f"{w_bw:.2f}",
            f"{r_bw:.2f}",
            f"{vmem.total / (1024**3):.2f}",
            f"{vmem.available / (1024**3):.2f}",
            time.ctime(),
            cpu_info,
            platform.machine(),
            f"{platform.system()} {platform.release()}"
        ])


def compare_csvs(csv_a: str, csv_b: str, out_csv: str = "memory_benchmark_comparison.csv") -> str:
    """Compare two benchmark CSV files and write a summary CSV with deltas.

    The comparison groups by Test Size (MB), averages multiple entries per size,
    computes bandwidths, and reports A vs B with absolute and percentage deltas.

    Returns the output CSV path.
    """
    def load_and_aggregate(path: str) -> pd.DataFrame:
        df = pd.read_csv(path)
        # Handle both classic and bandwidth CSV files.
        # Ensure numeric types.
        df["Test Size (MB)"] = pd.to_numeric(df["Test Size (MB)"], errors="coerce")
        df["Write Time (s)"] = pd.to_numeric(df["Write Time (s)"], errors="coerce")
        df["Read Time (s)"] = pd.to_numeric(df["Read Time (s)"], errors="coerce")
        g = df.groupby("Test Size (MB)", as_index=False).agg({
            "Write Time (s)": "mean",
            "Read Time (s)": "mean",
        })
        g["Write Bandwidth (GB/s)"] = (g["Test Size (MB)"] / 1024.0) / g["Write Time (s)"]
        g["Read Bandwidth (GB/s)"] = (g["Test Size (MB)"] / 1024.0) / g["Read Time (s)"]
        return g

    a = load_and_aggregate(csv_a)
    b = load_and_aggregate(csv_b)
    merged = a.merge(b, on="Test Size (MB)", suffixes=(" A", " B"))

    def delta(col: str):
        merged[f"{col} Δ"] = merged[f"{col} B"] - merged[f"{col} A"]
        merged[f"{col} Δ%"] = (merged[f"{col} Δ"] / merged[f"{col} A"]).replace([np.inf, -np.inf], np.nan) * 100

    for metric in ["Write Time (s)", "Read Time (s)", "Write Bandwidth (GB/s)", "Read Bandwidth (GB/s)"]:
        delta(metric)

    ordered_cols = [
        "Test Size (MB)",
        "Write Time (s) A", "Write Time (s) B", "Write Time (s) Δ", "Write Time (s) Δ%",
        "Read Time (s) A", "Read Time (s) B", "Read Time (s) Δ", "Read Time (s) Δ%",
        "Write Bandwidth (GB/s) A", "Write Bandwidth (GB/s) B", "Write Bandwidth (GB/s) Δ", "Write Bandwidth (GB/s) Δ%",
        "Read Bandwidth (GB/s) A", "Read Bandwidth (GB/s) B", "Read Bandwidth (GB/s) Δ", "Read Bandwidth (GB/s) Δ%",
    ]
    merged[ordered_cols].to_csv(out_csv, index=False)
    return out_csv


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
    parser.add_argument("--read-mode", choices=["full", "sample"], default="full",
                        help="How to measure read timing: 'full' touches all bytes (realistic), 'sample' reads a subset (fast, less accurate)")
    parser.add_argument("--compare-a", type=str, help="Path to baseline CSV to compare (A)")
    parser.add_argument("--compare-b", type=str, help="Path to target CSV to compare (B)")
    args = parser.parse_args()
    test_sizes = args.sizes

    if args.compare_a and args.compare_b:
        missing = [p for p in (args.compare_a, args.compare_b) if not os.path.exists(p)]
        if missing:
            print(
                (f"Error: Could not find the following file(s): {', '.join(missing)}\n"
                 f"Tips:\n"
                 f" - Make sure you ran at least one benchmark to create CSVs.\n"
                 f" - If you meant to compare against your current CSV, use '{CSV_FILE}' or '{BW_CSV_FILE}'.\n"
                 f" - To create a baseline from your current CSV: cp {CSV_FILE} baseline_results.csv\n"
                 f"   then run a new benchmark and compare: --compare-a baseline_results.csv --compare-b {CSV_FILE}")
            )
            return
        out_csv = compare_csvs(args.compare_a, args.compare_b)
        print(f"Comparison saved to {out_csv}")
        return

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
        f"{'Size':<10}{'Write Time':<14}{'Read Time':<14}"
        f"{'W BW (GB/s)':<14}{'R BW (GB/s)':<14}"
        f"{'Total RAM':<12}{'Available':<12}{runs_info}"
    )
    print(headers)
    print("-" * (90 + len(runs_info)))

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

            write_time, read_time = memory_read_write_test(size_mb, args.quiet, args.read_mode)
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

        w_bw = _bandwidth_gbps(size_mb, avg_write_time)
        r_bw = _bandwidth_gbps(size_mb, avg_read_time)

        result_line = (
            f"{label:<10}{avg_write_time:<14.3f}{avg_read_time:<14.3f}"
            f"{w_bw:<14.2f}{r_bw:<14.2f}"
            f"{total_ram:<12.2f}{avail_ram:<12.2f}"
        )
        if not args.quiet:
            result_line += " 📝"
        print(result_line)

        log_results(avg_write_time, avg_read_time, size_mb, args.csv_only)

    log_files = [CSV_FILE, BW_CSV_FILE] if args.csv_only else [RESULTS_FILE, CSV_FILE, BW_CSV_FILE]
    print(
        f"\nResults saved to {' and '.join(log_files)}"
        if args.quiet else Fore.MAGENTA + Style.BRIGHT +
        f"\n✅ Results saved to {' and '.join(log_files)}\n"
    )


def plot_results(csv_file):
    """Read CSV results and generate performance plots.
    Creates two figures:
     1) Time vs Size (write/read)
     2) Bandwidth (GB/s) vs Size (write/read), derived from size and time
    """
    df = pd.read_csv(csv_file)
    sizes = df["Test Size (MB)"].astype(float)
    write_times = df["Write Time (s)"].astype(float)
    read_times = df["Read Time (s)"].astype(float)

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
    print("Plot saved as memory_benchmark_performance.png")

    # Bandwidth plot (derived)
    write_bw = (sizes / 1024.0) / write_times.replace(0, np.nan)
    read_bw = (sizes / 1024.0) / read_times.replace(0, np.nan)

    plt.figure(figsize=(8, 6))
    plt.plot(
        sizes, write_bw, marker='o', label='Write Bandwidth (GB/s)'
    )
    plt.plot(
        sizes, read_bw, marker='o', label='Read Bandwidth (GB/s)'
    )
    plt.xlabel('Test Size (MB)')
    plt.ylabel('Bandwidth (GB/s)')
    plt.title('Memory Read/Write Bandwidth')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('memory_benchmark_performance_bandwidth.png')
    plt.show()
    print("Plot saved as memory_benchmark_performance_bandwidth.png")


if __name__ == "__main__":
    main()

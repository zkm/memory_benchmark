## 📝 Sample Memory Benchmark Results

| System                | Test Size | Write Time (s) | Read Time (s) | RAM Total (GB) | OS         |
|-----------------------|-----------|----------------|---------------|---------------|------------|
| Desktop (DDR5, Ryzen) | 1024MB    | 0.050          | 0.007         | 62.41         | Linux      |
| Desktop (DDR5, Ryzen) | 8192MB    | 0.406          | 0.007         | 62.41         | Linux      |
| Laptop (DDR4, i9)     | 1024MB    | 0.210          | 0.018         | 31.69         | Windows 11 |
| Laptop (DDR4, i9)     | 8192MB    | 2.957          | 0.033         | 31.69         | Windows 11 |

> Lower times indicate better performance.
> Use the `--plot` option to visualize these results.
# 🧠 Memory Benchmark

A powerful Python script to benchmark your system's memory performance with enterprise-grade features. Perfect for comparing RAM configurations before and after hardware upgrades, CI/CD pipelines, and performance monitoring.

---

## Table of Contents
- [Features](#features)
- [Requirements](#requirements)
- [Quick Start](#quick-start)
- [Usage](#usage)
   - [Basic Usage](#basic-usage)
   - [Advanced Options](#advanced-options)
   - [Command Line Options](#command-line-options)
- [Output Files](#output-files)
   - [CSV Columns](#csv-columns)
- [Advanced Usage Examples](#advanced-usage-examples)
   - [Performance Monitoring](#performance-monitoring)
   - [Hardware Comparison](#hardware-comparison)
   - [Stress Testing](#stress-testing)
   - [CI/CD Integration](#cicd-integration)
- [Interpreting Results](#interpreting-results)
- [Development](#development)
   - [VS Code Configuration](#vs-code-configuration)
   - [Testing](#testing)
- [System Compatibility](#system-compatibility)
- [Contributing](#contributing)
- [License](#license)

<a id="features"></a>
## 🚀 Features
- **Accurate Memory Testing**: Uses `time.perf_counter()` for high-precision timing and `np.empty()` for unbiased allocation
- **Real Memory Bandwidth**: Tests actual memory access patterns, not optimized NumPy operations
- **Multiple Test Sizes**: Benchmarks 1GB, 2GB, 4GB, and 8GB by default (customizable)
- **Robust Error Handling**: Gracefully handles memory allocation failures on low-RAM systems
- **Multiple Output Formats**: Results logged to both text files and structured CSV
- **Built-in Graphing**: Instantly visualize memory performance with the `--plot` option
- **Statistical Stability**: Average results over multiple runs to reduce variance
- **CI/CD Ready**: Quiet mode for automated environments
- **Cross-Platform**: Portable CPU detection for Linux, macOS, and Windows
- **System Info Logging**: Captures CPU, OS, and memory configuration details

<a id="requirements"></a>
## 📦 Requirements
- Python 3.7 or newer
- NumPy >= 1.26.4
- psutil
- colorama
- matplotlib
- pandas

<a id="quick-start"></a>
## ⚡️ Quick Start
1. **Clone the repository:**
   ```bash
   # HTTPS (recommended if you don't have SSH keys set up)
   git clone https://github.com/zkm/memory_benchmark.git
   cd memory_benchmark

   # or via SSH
   # git clone git@github.com:zkm/memory_benchmark.git
   ```
2. **(Recommended) Create and activate a virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

<a id="usage"></a>
## 🏃 Usage

<a id="basic-usage"></a>
### Basic Usage
```bash
python memory_benchmark.py
```
Runs default test sizes (1GB, 2GB, 4GB, 8GB) with colorful output.

<a id="advanced-options"></a>
### Advanced Options
```bash
# Custom test sizes
python memory_benchmark.py --sizes 1024 2048 4096

# Average over multiple runs for stability
python memory_benchmark.py --runs 5

# CI/CD friendly (no colors/emojis)
python memory_benchmark.py --quiet

# CSV output only (skip text log)
python memory_benchmark.py --csv-only

# Generate and view performance graph
python memory_benchmark.py --plot

# Production example: stable, quiet, CSV-only
python memory_benchmark.py --quiet --csv-only --runs 3 --sizes 2048 4096 8192
```

<a id="command-line-options"></a>
### Command Line Options
| Option      | Description                                   | Example                       |
|-------------|-----------------------------------------------|-------------------------------|
| `--sizes`   | Test sizes in MB                              | `--sizes 1024 2048 4096`      |
| `--runs`    | Number of runs to average                     | `--runs 5`                    |
| `--csv-only`| Skip text log, CSV output only                | `--csv-only`                  |
| `--quiet`   | No colors/emojis (CI/CD mode)                 | `--quiet`                     |
| `--plot`    | Generate and display performance graphs from CSV | `--plot`                   |

<a id="output-files"></a>
## 📊 Output Files
- **`memory_benchmark_results.txt`**: Human-readable detailed logs (unless `--csv-only`)
- **`memory_benchmark_results.csv`**: Structured data for analysis and graphing
- **`memory_benchmark_performance.png`**: Graphical visualization of your benchmark results (created with `--plot`)

<a id="csv-columns"></a>
### CSV Columns
- Test Size (MB)
- Write Time (s)
- Read Time (s)
- RAM Total (GB)
- RAM Available (GB)
- Timestamp
- CPU
- Machine
- OS

<a id="advanced-usage-examples"></a>
## 🛠 Advanced Usage Examples

<a id="performance-monitoring"></a>
### Performance Monitoring
```bash
# Daily automated benchmark (logs to CSV for analysis)
python memory_benchmark.py --quiet --csv-only --runs 3

# Monitor system over time
crontab -e
```

Add this line to your crontab:

```bash
0 2 * * * cd /path/to/memory_benchmark && python memory_benchmark.py --quiet --csv-only --runs 3
```

Tip: Use absolute paths to both the repository and your Python interpreter when running from cron.

<a id="hardware-comparison"></a>
### Hardware Comparison
```bash
# Before upgrade - save baseline
python memory_benchmark.py --runs 5 --csv-only
cp memory_benchmark_results.csv baseline_results.csv

# After upgrade - compare results
python memory_benchmark.py --runs 5 --csv-only
# Compare the two CSV files using your preferred tool (Excel, pandas, etc.)
```

<a id="stress-testing"></a>
### Stress Testing
```bash
# Test system limits (be careful with large sizes)
python memory_benchmark.py --sizes 1024 2048 4096 8192 16384 --runs 3 --quiet

# Quick system check
python memory_benchmark.py --sizes 512 1024 --runs 2 --quiet --csv-only
```

<a id="cicd-integration"></a>
### CI/CD Integration
```bash
# GitHub Actions / Jenkins
python memory_benchmark.py --quiet --sizes 1024 2048 --runs 2
```

<a id="interpreting-results"></a>
## 📈 Interpreting Results
- **Lower times = better performance**: Faster memory read/write speeds
- **Multiple runs**: Use `--runs 3` or higher for consistent results
- **Test size considerations**:
  - Small tests (< 1GB): May not reflect real-world usage
  - Large tests (> 4GB): Better representation of sustained memory performance
  - Very large tests (> 8GB): May fail on systems with limited RAM

- **Visual graphs**: Use `--plot` to instantly see trends and compare results. The generated PNG can be included in the repo as a sample output for others to see expected results.

<a id="development"></a>
## 🔧 Development

<a id="vs-code-configuration"></a>
### VS Code Configuration
The project includes VS Code settings for consistent formatting:
- 4 spaces for Python indentation
- 120 character line length
- Auto-format on save with flake8 compliance

<a id="testing"></a>
### Testing
```bash
# Syntax check
python -m py_compile memory_benchmark.py

# Lint check
python -m flake8 memory_benchmark.py --max-line-length=120

# Quick test
python memory_benchmark.py --sizes 100 --quiet
```

<a id="system-compatibility"></a>
## 🖥️ System Compatibility
- **Linux**: Full CPU detection via `/proc/cpuinfo`
- **macOS**: CPU detection via `sysctl`
- **Windows**: CPU detection via `wmic`
- **Fallback**: Generic processor identification

<a id="contributing"></a>
## 🤝 Contributing
1. Fork the repository
2. Create a feature branch
3. Follow the VS Code formatting settings
4. Ensure flake8 compliance
5. Test with `--quiet --sizes 100`
6. Submit a pull request

<a id="license"></a>
## 📝 License
[MIT](LICENSE)

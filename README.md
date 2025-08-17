# 🧠 Memory Benchmark

A powerful Python script to benchmark your system's memory performance with enterprise-grade features. Perfect for comparing RAM configurations before and after hardware upgrades, CI/CD pipelines, and performance monitoring.

---

## 🚀 Features
- **Accurate Memory Testing**: Uses `time.perf_counter()` for high-precision timing and `np.empty()` for unbiased allocation
- **Real Memory Bandwidth**: Tests actual memory access patterns, not optimized NumPy operations
- **Multiple Test Sizes**: Benchmarks 1GB, 2GB, 4GB, and 8GB by default (customizable)
- **Robust Error Handling**: Gracefully handles memory allocation failures on low-RAM systems
- **Multiple Output Formats**: Results logged to both text files and structured CSV
- **Statistical Stability**: Average results over multiple runs to reduce variance
- **CI/CD Ready**: Quiet mode for automated environments
- **Cross-Platform**: Portable CPU detection for Linux, macOS, and Windows
- **System Info Logging**: Captures CPU, OS, and memory configuration details

## 📦 Requirements
- Python 3.7 or newer
- numpy >= 1.26.4
- psutil
- colorama

## ⚡️ Quick Start
1. **Clone the repository:**
   ```bash
   git clone git@github.com:zkm/memory_benchmark.git
   cd memory_benchmark
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

## 🏃 Usage

### Basic Usage
```bash
python memory_benchmark.py
```
Runs default test sizes (1GB, 2GB, 4GB, 8GB) with colorful output.

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

# Production example: stable, quiet, CSV-only
python memory_benchmark.py --quiet --csv-only --runs 3 --sizes 2048 4096 8192
```

### Command Line Options
| Option | Description | Example |
|--------|-------------|---------|
| `--sizes` | Test sizes in MB | `--sizes 1024 2048 4096` |
| `--runs` | Number of runs to average | `--runs 5` |
| `--csv-only` | Skip text log, CSV output only | `--csv-only` |
| `--quiet` | No colors/emojis (CI/CD mode) | `--quiet` |

## 📊 Output Files
- **`memory_benchmark_results.txt`**: Human-readable detailed logs (unless `--csv-only`)
- **`memory_benchmark_results.csv`**: Structured data for analysis and graphing

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

## 🛠 Advanced Usage Examples

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

### Hardware Comparison
```bash
# Before upgrade - save baseline
python memory_benchmark.py --runs 5 --csv-only
cp memory_benchmark_results.csv baseline_results.csv

# After upgrade - compare results
python memory_benchmark.py --runs 5 --csv-only
# Compare the two CSV files using your preferred tool (Excel, pandas, etc.)
```

### Stress Testing
```bash
# Test system limits (be careful with large sizes)
python memory_benchmark.py --sizes 1024 2048 4096 8192 16384 --runs 3 --quiet

# Quick system check
python memory_benchmark.py --sizes 512 1024 --runs 2 --quiet --csv-only
```

### CI/CD Integration
```bash
# GitHub Actions / Jenkins
python memory_benchmark.py --quiet --sizes 1024 2048 --runs 2
```

## 📈 Interpreting Results
- **Lower times = better performance**: Faster memory read/write speeds
- **Multiple runs**: Use `--runs 3` or higher for consistent results
- **Test size considerations**:
  - Small tests (< 1GB): May not reflect real-world usage
  - Large tests (> 4GB): Better representation of sustained memory performance
  - Very large tests (> 8GB): May fail on systems with limited RAM

## 🔧 Development

### VS Code Configuration
The project includes VS Code settings for consistent formatting:
- 4 spaces for Python indentation
- 120 character line length
- Auto-format on save with flake8 compliance

### Testing
```bash
# Syntax check
python -m py_compile memory_benchmark.py

# Lint check
python -m flake8 memory_benchmark.py --max-line-length=120

# Quick test
python memory_benchmark.py --sizes 100 --quiet
```

## 🖥️ System Compatibility
- **Linux**: Full CPU detection via `/proc/cpuinfo`
- **macOS**: CPU detection via `sysctl`
- **Windows**: CPU detection via `wmic`
- **Fallback**: Generic processor identification

## 🤝 Contributing
1. Fork the repository
2. Create a feature branch
3. Follow the VS Code formatting settings
4. Ensure flake8 compliance
5. Test with `--quiet --sizes 100`
6. Submit a pull request

## 📝 License
[MIT](LICENSE)

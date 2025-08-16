
# 🧠 Memory Benchmark

A simple Python script to benchmark your system's memory performance. Perfect for comparing RAM configurations before and after hardware upgrades.

---

## 🚀 Features
- Measures memory read/write speed using large arrays
- Benchmarks multiple memory sizes: 1GB, 2GB, 4GB, and 8GB sequentially
- Logs results to a file for easy comparison

## 📦 Requirements
- Python 3.7 or newer
- numpy
- psutil

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
   pip install numpy psutil
   ```

## 🏃 Usage
Run the benchmark script:
```bash
python memory_benchmark.py
```
The script will automatically test 1GB, 2GB, 4GB, and 8GB memory sizes in sequence. Results are saved in `memory_benchmark_results.txt` (excluded from git).

## 🛠 Customizing Test Sizes
To change or add test sizes, edit the `test_sizes` list in `memory_benchmark.py`:
```python
test_sizes = [1024, 2048, 4096, 8192]  # 1GB, 2GB, 4GB, 8GB
```

## 📊 Interpreting Results
Compare read/write times before and after your RAM upgrade. Lower times indicate better memory bandwidth. For best results, run with large test sizes (e.g., 8GB or more).

## �️ System Information Logging
The script logs system architecture, OS, and kernel info for each benchmark run. CPU info is displayed and logged only if available (Linux systems may show this as blank).

## �📝 License
[MIT](LICENSE)

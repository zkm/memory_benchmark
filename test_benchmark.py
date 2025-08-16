import os
import csv
import subprocess

def test_script_runs():
    result = subprocess.run(['python', 'memory_benchmark.py', '--sizes', '128'], capture_output=True)
    assert result.returncode == 0, f"Script failed: {result.stderr.decode()}"

def test_output_files():
    assert os.path.exists('memory_benchmark_results.txt'), "Results txt file not found"
    assert os.path.exists('memory_benchmark_results.csv'), "Results csv file not found"

def test_csv_columns():
    with open('memory_benchmark_results.csv') as f:
        reader = csv.reader(f)
        header = next(reader)
        expected = ["Test Size (MB)", "Write Time (s)", "Read Time (s)", "RAM Total (GB)", "RAM Available (GB)", "Timestamp", "CPU", "Machine", "OS"]
        for col in expected:
            assert col in header, f"Missing column: {col}"

if __name__ == "__main__":
    test_script_runs()
    test_output_files()
    test_csv_columns()
    print("All tests passed!")

import sys
import os

print("Python path:", sys.path)
print("Current directory:", os.getcwd())

try:
    import dodopayments
    print("Successfully imported dodopayments:", dodopayments.__file__)
except ImportError as e:
    print("Failed to import dodopayments:", str(e))
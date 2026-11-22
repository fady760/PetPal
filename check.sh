#!/bin/bash

echo "Running application tests..."

# Run pytest
pytest test_main.py

# Check exit code
if [ $? -eq 0 ]; then
    echo "✅ Tests passed successfully!"
    exit 0
else
    echo "❌ Tests failed. Stopping pipeline."
    exit 1
fi

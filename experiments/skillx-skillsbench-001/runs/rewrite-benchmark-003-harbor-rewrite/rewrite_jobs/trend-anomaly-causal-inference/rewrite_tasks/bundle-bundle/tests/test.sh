#!/bin/bash
set -euo pipefail
python3 /tests/test_outputs.py
echo 1 > /logs/verifier/reward.txt

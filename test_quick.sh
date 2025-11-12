#!/bin/bash
# Quick test script for EDOT Config Explainer

set -e

echo "🧪 Testing EDOT Config Explainer"
echo "================================="
echo ""

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "⚠️  Warning: Ollama doesn't seem to be running."
    echo "   Start it with: ollama serve"
    echo ""
fi

# Test 1: OTLP Receiver
echo "Test 1: OTLP Receiver"
echo "----------------------"
python3 -m explain_config.cli --file test_configs/otlp_receiver.yaml --md-out test_output_1.md
echo "✅ Test 1 passed"
echo ""

# Test 2: Batch Processor
echo "Test 2: Batch Processor"
echo "----------------------"
python3 -m explain_config.cli --file test_configs/batch_processor.yaml --md-out test_output_2.md
echo "✅ Test 2 passed"
echo ""

# Test 3: Combined Config
echo "Test 3: Combined Config (Multiple Components)"
echo "---------------------------------------------"
python3 -m explain_config.cli --file test_configs/combined.yaml --md-out test_output_combined.md
echo "✅ Test 3 passed"
echo ""

# Test 4: Stdin
echo "Test 4: Stdin Input"
echo "-------------------"
cat test_configs/otlp_receiver.yaml | python3 -m explain_config.cli > /dev/null
echo "✅ Test 4 passed"
echo ""

echo "🎉 All tests passed!"
echo ""
echo "Generated markdown files:"
ls -lh test_output_*.md 2>/dev/null || echo "  (No markdown files generated)"


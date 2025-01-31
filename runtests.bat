@echo off

pytest -s --tracing on

playwright show-trace ./test-results/test-integration-py-test-alta-chromium/trace.zip
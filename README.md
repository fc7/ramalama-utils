# ramalama-utils

Utility scripts for ramalama

At the moment, this repo provides a simple Python script `reuse_ollama_for_ramalama.py`. Its sole purpose is to make all local Ollama models available to [ramalama](https://github.com/containers/ramalama) via symlinks.

The script is idempotent.

When executed with the parameter `--reset` the symlinks are removed.

Please note that this is provided as is and has only been tested on macOS for now.

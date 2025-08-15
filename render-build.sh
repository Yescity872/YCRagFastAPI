#!/usr/bin/env bash
# render-build.sh

# Set up writable directories for Rust/Cargo
mkdir -p /tmp/cargo /tmp/pip-cache
export CARGO_HOME=/tmp/cargo
export PIP_CACHE_DIR=/tmp/pip-cache
export PATH="$CARGO_HOME/bin:$PATH"

# Install Rust if needed (silent mode)
if ! command -v cargo &> /dev/null; then
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source "$HOME/.cargo/env"
fi

# Install requirements with pip
pip install --no-cache-dir -r requirements.txt
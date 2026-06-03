#!/bin/bash
# scripts/sim_single.sh
# Run a single named testbench
# Usage: docker-compose run --rm sim-one tb_uart

set -e

TB=$1

if [ -z "$TB" ]; then
    echo "ERROR: No testbench specified"
    echo "Usage: docker-compose run --rm sim-one <testbench_name>"
    echo "Example: docker-compose run --rm sim-one tb_uart"
    exit 1
fi

mkdir -p sim

echo "=== Compiling VHDL sources ==="
ghdl -a --std=08 --work=work \
    src/uart_rx.vhd \
    src/uart_tx.vhd \
    src/input_buffer.vhd \
    src/fir_filter.vhd \
    src/mac_engine.vhd \
    src/control_fsm.vhd \
    src/top_level.vhd

echo "=== Compiling testbench: $TB ==="
ghdl -a --std=08 --work=work tb/$TB.vhd

echo "=== Elaborating ==="
ghdl -e --std=08 --work=work $TB

echo "=== Running $TB ==="
ghdl -r --std=08 --work=work $TB \
    --vcd=sim/$TB.vcd \
    --stop-time=10ms \
    --assert-level=error

echo "=== $TB complete — waveform at sim/$TB.vcd ==="
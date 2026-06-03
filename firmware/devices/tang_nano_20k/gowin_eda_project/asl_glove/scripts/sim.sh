#!/bin/bash
# scripts/sim.sh
# Compiles all VHDL sources and runs every testbench in tb/
# Waveforms saved to sim/ folder (gitignored)

set -e  # stop on any error

mkdir -p sim

echo "=== Cleaning previous sim artifacts ==="
rm -f work-obj08.cf

echo "=== Compiling VHDL sources ==="
ghdl -a --std=08 --work=work \
    src/uart_rx.vhd \
    src/uart_tx.vhd \
    src/input_buffer.vhd \
    src/fir_filter.vhd \
    src/mac_engine.vhd \
    src/control_fsm.vhd \
    src/top_level.vhd

echo "=== Compiling testbenches ==="
ghdl -a --std=08 --work=work \
    tb/tb_uart.vhd \
    tb/tb_mac_engine.vhd \
    tb/tb_top_level.vhd

# ── Run each testbench ─────────────────────────────────────────────────────

echo ""
echo "=== Running tb_uart ==="
ghdl -e --std=08 --work=work tb_uart
ghdl -r --std=08 --work=work tb_uart \
    --vcd=sim/tb_uart.vcd \
    --stop-time=1ms \
    --assert-level=error
echo "tb_uart PASSED"

echo ""
echo "=== Running tb_mac_engine ==="
ghdl -e --std=08 --work=work tb_mac_engine
ghdl -r --std=08 --work=work tb_mac_engine \
    --vcd=sim/tb_mac_engine.vcd \
    --stop-time=5ms \
    --assert-level=error
echo "tb_mac_engine PASSED"

echo ""
echo "=== Running tb_top_level ==="
ghdl -e --std=08 --work=work tb_top_level
ghdl -r --std=08 --work=work tb_top_level \
    --vcd=sim/tb_top_level.vcd \
    --stop-time=10ms \
    --assert-level=error
echo "tb_top_level PASSED"

echo ""
echo "=== All simulations PASSED ==="
echo "Waveforms saved to sim/"
echo "  sim/tb_uart.vcd"
echo "  sim/tb_mac_engine.vcd"
echo "  sim/tb_top_level.vcd"
## Folder Structure

```
asl-glove-fpga/
├── .gitignore
├── README.md
├── asl_glove.gprj              ← Gowin project file
├── src/
│   ├── top.vhd                 ← top entity
│   ├── uart_rx.vhd
│   ├── uart_tx.vhd
│   ├── spi_flash.vhd
│   ├── ml_inference.vhd
│   ├── fir_filter.vhd
│   ├── control_fsm.vhd
│   └── input_buffer.vhd
│   └── ...
├── tb/
│   ├── tb_top.vhd
│   └── tb_ml_inference.vhd
│   └── ...
├── constraints/
│   ├── asl_glove.cst
│   └── asl_glove.sdc
├── weights/
│   ├── layer1.mi
│   ├── layer2.mi
│   └── layer3.mi
├── bitstream/
│   └── asl_glove.fs            ← committed bitstream
└── training/
    ├── train.py
    └── convert_weights.py
```

The `.gprj` file references files by relative path so the structure is portable across machines.

## VS Code Editing

### Full synthesis + PnR + bitstream (most common)
docker-compose run --rm gowin

### Synthesis only (fastest, catches HDL errors)
docker-compose run --rm gowin-synth

### PnR only (after synth passes)
docker-compose run --rm gowin-pnr

### Bitstream only (after PnR passes)
docker-compose run --rm gowin-bitstream

### Run all testbenches
docker-compose run --rm sim

### Run one specific testbench
docker-compose run --rm sim-one tb_uart
docker-compose run --rm sim-one tb_mac_engine
docker-compose run --rm sim-one tb_top_level

### C++ to Verilog via Bambu
docker-compose run --rm bambu

## Simulation From VS Code

Gowin EDA's built-in simulator is weak. Use ModelSim or GHDL externally via VS Code tasks:

```json
{
  "label": "Sim: Run Testbench",
  "type": "shell",
  "command": "vsim",
  "args": ["-c", "-do", "scripts/sim.do"],
  "group": "test"
}
```
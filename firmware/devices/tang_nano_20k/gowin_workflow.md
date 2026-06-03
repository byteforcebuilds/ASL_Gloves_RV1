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

Install extensions:
- **VHDL LS** (VHDL language server) — syntax, completion, navigation
- **TerosHDL** — full HDL IDE features in VS Code
- **WaveTrace** — view simulation waveforms

Edit files in VS Code, save, then Gowin EDA picks up changes automatically when you run synthesis. Both tools can have the same file open simultaneously.

## Automating Gowin From VS Code

Gowin has a TCL command line interface called `gw_sh`. You can drive the entire flow from VS Code via tasks.

Create `.vscode/tasks.json`:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Gowin: Synthesize",
      "type": "shell",
      "command": "gw_sh",
      "args": ["scripts/synth.tcl"],
      "group": "build"
    },
    {
      "label": "Gowin: Place & Route",
      "type": "shell",
      "command": "gw_sh",
      "args": ["scripts/pnr.tcl"],
      "group": "build"
    },
    {
      "label": "Gowin: Generate Bitstream",
      "type": "shell",
      "command": "gw_sh",
      "args": ["scripts/bitstream.tcl"],
      "group": "build"
    },
    {
      "label": "Gowin: Full Flow",
      "type": "shell",
      "command": "gw_sh",
      "args": ["scripts/full_flow.tcl"],
      "group": {"kind": "build", "isDefault": true}
    },
    {
      "label": "Gowin: Program Flash",
      "type": "shell",
      "command": "programmer_cli",
      "args": ["-d", "GW2AR-18", "-r", "5", "-f", "bitstream/asl_glove.fs"],
      "group": "build"
    }
  ]
}
```

Create `scripts/full_flow.tcl`:

```tcl
open_project asl_glove.gprj
run all
close_project
```

`Ctrl+Shift+B` in VS Code runs the entire synthesis through bitstream pipeline. Add `programmer_cli` to your PATH and you can flash from VS Code too.

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
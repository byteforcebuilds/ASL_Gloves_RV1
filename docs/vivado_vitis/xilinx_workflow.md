# AMD Vivado + Vitis Workflow for cmod_s7

## Folder Structure

```
firmware/devices/cmod_s7/
├── src/
│   ├── uart.vhd                    ← UART communication (shared)
│   └── ...
├── vivado_impl/
│   ├── cnn_inference/
│   │   ├── cnn_inference.xpr       ← CNN Vivado project
│   │   ├── src/
│   │   │   ├── top_cnn.vhd         ← CNN top entity
│   │   │   └── ...
│   │   └── ...
│   └── tcn_inference/
│       ├── tcn_inference.xpr       ← TCN Vivado project
│       ├── src/
│       │   ├── top_tcn.vhd         ← TCN top entity
│       │   └── ...
│       └── ...
└── vitis_impl/
    ├── cnn_inference/
    │   ├── .wsdata/
    │   ├── src/
    │   │   ├── top_cnn_hls.cpp     ← CNN HLS kernel
    │   │   └── ...
    │   └── ...
    └── tcn_inference/
        ├── .wsdata/
        ├── src/
        │   ├── top_tcn_hls.cpp     ← TCN HLS kernel
        │   └── ...
        └── ...
```
## Build Workflow

### CNN Implementation (Vivado + Vitis)

#### Vivado Flow
1. Open `vivado_impl/cnn_inference/cnn_inference.xpr` in Vivado
2. Run synthesis, implementation, and generate bitstream
3. Export the bitstream to `firmware/devices/cmod_s7/vivado_impl/cnn_inference/...`

#### Vitis HLS Flow
1. Open `vitis_impl/cnn_inference` workspace in Vitis HLS
2. Synthesize and generate IP for `top_cnn_hls.cpp`
3. Export RTL to `firmware/devices/cmod_s7/vitis_impl/cnn_inference/...`

### TCN Implementation (Vivado + Vitis)

#### Vivado Flow
1. Open `vivado_impl/tcn_inference/tcn_inference.xpr` in Vivado
2. Run synthesis, implementation, and generate bitstream
3. Export the bitstream to `firmware/devices/cmod_s7/vivado_impl/tcn_inference/...`

#### Vitis HLS Flow
1. Open `vitis_impl/tcn_inference` workspace in Vitis HLS
2. Synthesize and generate IP for `top_tcn_hls.cpp`
3. Export RTL to `firmware/devices/cmod_s7/vitis_impl/tcn_inference/...`

## Shared Components

- **uart.vhd**: UART communication module (used by both CNN and TCN)
# AMD Vivado + Vitis Workflow for cmod_s7

## Folder Structure

```
firmware/devices/cmod_s7/

├── vivado_impl/
│   ├── mlp_inference/
│   │   ├── mlp_inference.xpr       ← MLP Vivado project
│   │   ├── src/
│   │   │   ├── top_cnn.vhd         ← MLP top entity
│   │   │   └── ...
│   │   └── ...
│   └── cnn_inference/
│   │   ├── cnn_inference.xpr       ← CNN Vivado project
│   │   ├── src/
│   │   │   ├── top_cnn.vhd         ← CNN top entity
│   │   │   └── ...
│   │   └── ...
│   ├── shared/
│   │   ├── spi_slave.vhd           ← SPI 
\
│   │   └── ...
└── vitis_impl/
    ├── mlp_inference/
    │   ├── .wsdata/
    │   ├── src/
    │   │   ├── top_mlp_hls.cpp     ← MLP HLS kernel
    │   │   └── ...
    │   └── ...
    └── cnn_inference/
        ├── .wsdata/
        ├── src/
        │   ├── top_cnn_hls.cpp     ← cnn HLS kernel
        │   └── ...
        └── ...
```
## Build Workflow

### mlp Implementation (Vivado + Vitis)

#### Vivado Flow
1. Open `vivado_impl/mlp_inference/mlp_inference.xpr` in Vivado
2. Run synthesis, implementation, and generate bitstream
3. Export the bitstream to `firmware/devices/cmod_s7/vivado_impl/mlp_inference/...`

#### Vitis HLS Flow
1. Open `vitis_impl/mlp_inference` workspace in Vitis HLS
2. Synthesize and generate IP for `top_mlp_hls.cpp`
3. Export RTL to `firmware/devices/cmod_s7/vitis_impl/mlp_inference/...`

### cnn Implementation (Vivado + Vitis)

#### Vivado Flow
1. Open `vivado_impl/cnn_inference/cnn_inference.xpr` in Vivado
2. Run synthesis, implementation, and generate bitstream
3. Export the bitstream to `firmware/devices/cmod_s7/vivado_impl/cnn_inference/...`

#### Vitis HLS Flow
1. Open `vitis_impl/cnn_inference` workspace in Vitis HLS
2. Synthesize and generate IP for `top_cnn_hls.cpp`
3. Export RTL to `firmware/devices/cmod_s7/vitis_impl/cnn_inference/...`

## Shared Components

- **uart.vhd**: UART communication module (used by both mlp and cnn)
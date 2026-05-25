# Dataset Landscape & Training Strategy

## ASL Text-to-Speech Gloves

---

## Hardware goal for 4791

A working wrist board prototype demonstrating end-to-end sensor data flow — flex sensors + wrist IMU → ESP32-S3 → BLE → live dashboard. This validates the core sensing architecture before the fingertip IMU and FPGA work begins in 4792.

## Software goal for 4791

A trained baseline PyTorch model on the figshare dataset with preliminary accuracy numbers. This demonstrates the ML approach is viable before our own hardware is ready.

---

## General Consensus

No publicly available ASL sensor-glove dataset captures fingertip-level IMU data. Every existing dataset uses a single wrist IMU or flex sensors only. Our glove — with 6 IMUs across the wrist and all five fingertips — produces a richer feature space than any open dataset currently provides. We are not just building a device. We are producing the first fingertip-IMU ASL dataset, which is itself a research contribution.

---

## Dataset Landscape

### GOOD

#### figshare ASL-Sensor-Dataglove (our baseline)

- **Source:** [https://figshare.com/articles/dataset/ASL-Sensor-Dataglove-Dataset_zip/20031017](https://figshare.com/articles/dataset/ASL-Sensor-Dataglove-Dataset_zip/20031017)
- **Subjects:** 25 (19 male, 6 female)
- **Signs:** 40 — 26 letters + 14 words (bad, deaf, fine, good, goodbye, hello, hungry, me, no, please, sorry, thank you, yes, you)
- **Sign types:** 24 static (finger flexion only), 16 dynamic (motion + flexion)
- **IMUs:** 1 (wrist only) — MPU-6050
- **Flex sensors:** 5 (one per finger)
- **Sampling rate:** ~100Hz
- **Rows per file:** 1,500 (~15 seconds per recording)
- **Features per timestep:** 21 (5 flex + 4 quaternion + 3 gyroscope + 9 accelerometer)
- **Total data:** ~1.5M labeled sensor readings
- **Status:** Downloaded

#### SignSpeak (supplemental)

- **Source:** [https://arxiv.org/abs/2407.12020](https://arxiv.org/abs/2407.12020)
- **Subjects:** multiple
- **Signs:** 36 (A–Z, 1–10)
- **IMUs:** 0 (flex sensors only)
- **Flex sensors:** 5
- **Sampling rate:** 36Hz
- **Samples:** 7,200
- **Best accuracy:** 92% categorical
- **Status:** Open source

### BAD (but worth looking into?)

#### SIGMA-ASL (wrong modality)

- **Source:** [https://arxiv.org/abs/2605.06351](https://arxiv.org/abs/2605.06351)
- **Subjects:** 20
- **Signs:** 160
- **Sensors:** Azure Kinect RGB-D camera + mmWave radar + 2 wrist IMUs
- **Clips:** 93,545
- **Why excluded:** Camera-based modality — not compatible with our sensor pipeline

#### Fingertip IMU ASL Dataset (does not exist)

- No open dataset captures fingertip-level IMU data for ASL
- This is the gap our project fills
- Our data collection is a novel research contribution beyond the device itself

---

## Our Hardware vs. Existing Datasets


|                   | figshare  | SignSpeak | Our Glove                    |
| ----------------- | --------- | --------- | ---------------------------- |
| IMUs              | 1 (wrist) | 0         | **6 (wrist + 5 fingertips)** |
| Flex sensors      | 5         | 5         | 5                            |
| Features/timestep | 21        | 5         | **~65**                      |
| Sampling rate     | ~100Hz    | 36Hz      | ~100Hz                       |
| Fingertip data    | None      | None      | **Full IMU per finger**      |
| Subjects          | 25        | multiple  | 4+ (team + recruits)         |


Our input vector is ~3x richer per timestep. Fingertip IMUs enable finer discrimination between signs that share similar wrist orientation but differ in finger pose (e.g. A vs. S vs. E).

---

## Why We Are Not Searching Further

- **0** publicly available datasets include fingertip IMUs for ASL
- **3x** richer feature vector vs. the best available dataset
- **21 → 65** features per timestep, figshare vs. our glove

---

## Three-Phase Training Strategy

### Phase 1 — Baseline model on figshare dataset

Train a PyTorch classifier on the existing 21-feature input vector. Establish an accuracy floor before hardware exists.

**Deliverable:** Preliminary accuracy numbers ready for the 4791 proposal.

### Phase 2 — Retrain on our glove's data

Collect sensor-native data from our 65-feature glove. Retrain with fingertip IMU channels included. Expect measurable accuracy improvement on ambiguous signs.

**Deliverable:** Fine-tuned model outperforming Phase 1 baseline.

### Phase 3 — Per-user fine-tuning + autocorrect

Calibration recording at session start. Fine-tune model weights per signer. Apply dialect correction layer to handle natural signing variation across users.

**Deliverable:** Robust multi-user system with calibration pipeline.

---

## Gaps in figshare — Our Collection Protocol Addresses All of Them


| Gap                        | Our Fix                                                              |
| -------------------------- | -------------------------------------------------------------------- |
| No fingertip IMUs          | 5 fingertip IMUs — directly addresses primary literature gap         |
| Single-session per subject | Multiple sessions across different days — captures drift and fatigue |
| No rest pose baseline      | Rest pose recorded at every session start for per-user normalization |
| Hardware mismatch          | Fine-tuning on our glove's actual output closes the domain gap       |


### Full Collection Protocol

- Match the same 40 signs as figshare minimum
- Record a neutral rest pose at the start of every session
- Minimum 4 subjects (team) — recruit more from Northeastern community, target 10+
- Multiple sessions per subject across different days
- Maintain ~100Hz sampling rate
- Label format: `{subject_id}/{sign}/{session_id}.csv`

---

## Model Architecture

### Input

- 5 flex sensor readings (normalized per user)
- 6 × IMU (4 quaternion + 3 gyroscope + 3 accelerometer body + 3 accelerometer world) = 60 values
- Total: **65 features per timestep** at ~100Hz

### Sign categories


| Type    | Signs              | Architecture                                              |
| ------- | ------------------ | --------------------------------------------------------- |
| Static  | Most letters       | MLP or 1D CNN — single frame input                        |
| Dynamic | J, Z, common words | LSTM or Temporal CNN — sequence input over ~0.5–1s window |


### Stack


| Phase               | Language     | Tool                     |
| ------------------- | ------------ | ------------------------ |
| Data collection     | Python       | Custom serial/BLE script |
| Preprocessing       | Python       | NumPy, pandas            |
| Model training      | Python       | PyTorch                  |
| Model export        | Python       | ONNX / torch.export      |
| On-device inference | C++          | microTVM or TFLite Micro |
| FPGA integration    | C++ + HDL    | Vivado + soft processor  |
| Companion app       | React Native | TBD                      |



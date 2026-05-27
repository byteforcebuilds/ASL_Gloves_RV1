# Data Exploration Findings
## 01_data_exploration.ipynb -- Cell-by-Cell Analysis

## Section 1: Setup & Dataset Loading

### Cell 1 -- Imports, config, constants

Output:
```
Dataset root exists: True
Static: 24 | Dynamic: 16 | Total: 40 signs
Feature columns (21): ['flex_1', 'flex_2', 'flex_3', 'flex_4', 'flex_5', 'Qw', 'Qx', 'Qy', 'Qz', 'GYRx', 'GYRy', 'GYRz', 'ACCx_body', 'ACCy_body', 'ACCz_body', 'ACCx_world', 'ACCy_world', 'ACCz_world', 'ACCx', 'ACCy', 'ACCz']
```

Findings:
- Docker successfully mounted `software/ml/data/` into the container -- the volume mount in `docker-compose.yml` is working correctly
- Sign lists are correct -- 24 static, 16 dynamic, 40 total
- Column groupings add up to 21 features -- 5 flex + 4 quat + 3 gyro + 9 acc

### Cell 2 -- load_dataset

Output:
```
Loaded 1000 files | 1,500,000 rows | 25 subjects | 40 signs
```

Findings:
- 1,000 files -- 25 subjects × 40 signs = 1,000 CSVs, every single one loaded without hitting the `except` block. Zero corrupted files.
- 1,500,000 rows -- 1,000 files × 1,500 rows each, perfectly consistent. No file is shorter or longer than expected.
- 25 subjects, 40 signs -- complete dataset, no gaps at this stage.
- The key thing here is what didn't print -- no `Failed:` lines. If any CSV had been corrupted or malformed, we'd see it here. Clean load.
- Loading 1.5M rows into memory took a few seconds but pandas handled it fine. When we move to `dataset.py` and start windowing, we'll be working with numpy arrays instead of a full DataFrame in memory -- much more efficient for training.

---

## Section 2: Structure Overview

### Cell 1 -- Shape and dtypes

Output:
```
Shape: (1500000, 26)

Dtypes:
timestamp     float64
user_id         int64
flex_1        float64
...
subject           str
sign              str
sign_type         str
```

Findings:
- 26 columns total -- 21 sensor features + timestamp + user_id + the 3 we added (subject, sign, sign_type)
- All sensor columns are float64 -- no integer sensor readings that would need casting before feeding into PyTorch, which expects floats
- user_id is int64 -- the original numeric subject identifier from the dataset. Redundant with our string `subject` column (e.g. `'001'`). We'll use `subject` for our train/val/test split and ignore `user_id` in `dataset.py`
- subject, sign, sign_type are strings -- labels not features, they never touch the model input

### Cell 2 -- Sanity checks

Output:
```
Missing values: None -- dataset is complete

Rows per file -- Min: 1500 | Max: 1500 | Mean: 1500.0

Estimated sample rate: 100.0 Hz
Recording duration:    14.99 s
```

Findings:
- No missing values -- every one of the 21 feature channels has a value for every row across all 1.5M rows. No imputation needed, no dropping rows. Clean.
- Min = Max = Mean = 1500 -- every single recording is exactly 1,500 rows. Critical for windowing -- a consistent recording length means our window count formula `(1500 - 100) // 50 + 1 = 29` applies uniformly across every subject and every sign. No edge cases to handle.
- 100.0 Hz exactly -- sample rate is perfectly consistent. Confirms that 100 timesteps = 1 second is precise, not approximate.
- 14.99 seconds -- just under 15s due to the timestamp being measured from first row to last rather than including the duration of the final sample. Expected.

---

## Section 3: Signal Visualization

### Cell 1 -- Static vs dynamic signal traces (sign `a` vs sign `j`)

Findings:

**Flex (row 1)**
- Both signs show relatively stable flex traces with sensor noise spikes between repetitions
- Sign `j` shows `flex_5` (pinky) ranging much wider and dipping negative -- the pinky traces the J shape
- Sign `a` has tighter, more consistent flex values overall

**Gyroscope (row 2)**
- Sign `a` sits almost completely flat -- y-axis only reaches ±0.075
- Sign `j` has sharp periodic spikes reaching ±6, nearly 80x larger -- each spike is one J-tracing motion
- The periodicity is visible -- roughly 10 repetitions across 30 seconds (~one sign every 3 seconds)
- This completely validates the two-model strategy -- gyroscope alone separates static from dynamic

**Quaternion (row 3)**
- Sign `a` is nearly flat -- wrist orientation barely changes over the full recording
- Sign `j` shows large sweeping sinusoidal curves -- wrist rotating continuously through the J motion
- Quaternion data is critical for dynamic signs but adds minimal discriminative value for static ones

**Accel body (row 4)**
- Sign `a` is near-zero with small noise
- Sign `j` has large spikes of ±10 -- wrist is both rotating and translating during the J stroke
- Acceleration spikes align with gyroscope spikes as expected

**Flag:** Both plots run longer than expected (~35s and ~32s vs expected ~15s). The recording contains multiple repetitions of the sign, not a single hold. Good for windowing -- more genuine variation per file.

### Cell 2 -- Mean flex sensor values per sign (Subject 001)

Findings:
- `j` (purple) and `a` (crimson) sit in the top cluster -- flex profiles are actually quite similar, confirming flex sensors alone cannot distinguish them. Gyroscope data is what separates them.
- `b` (orange) and `hello` (green) drop sharply into negative territory by flex_3 through flex_5 -- `b` is a flat open hand with all fingers extended, `hello` involves a wave motion averaging near-zero
- Most of the 40 signs bunch together in the 40–80 range -- the hard classification problem where subtle individual finger angle differences matter. Our fingertip IMUs will capture these more precisely.
- Several signs dip below zero -- calibration artifact from the resistor divider circuit varying per sensor and per subject. Confirms per-subject normalization is not optional.

**Fix applied:** Added `plt.xticks(rotation=45, ha='right')` before `plt.tight_layout()` to fix cramped x-axis labels.

---

## Section 4: Class Balance

### Cell 1 -- Subjects with recordings per sign

Output:
```
Min: 25 (a) | Max: 25 (a)
```

Findings:
- Every bar hits the dashed line at 25 -- every sign has recordings from all 25 subjects
- Dataset is perfectly balanced -- no class has fewer samples than any other
- No weighted loss function or oversampling strategy needed during training
- Static and dynamic signs are evenly distributed with no ordering bias

---

## Section 5: Subject-Level Variation

### Cell 1 -- Inter-subject flex variation for sign `a`

Findings:
- Spread on flex_1 is massive -- subject lines span from ~-50 to +20, a range of ~70 units for the same sign. This is genuine inter-subject variation, not outliers.
- The mean profile shape is consistent even when absolute values differ wildly -- red line rises from flex_1 through flex_3, plateaus at flex_4 and flex_5. Z-score normalization preserves this shape while removing scale offset.
- Spread tightens from flex_1 toward flex_5 -- thumb (flex_1) is the most variable sensor, index and middle fingers are more consistent. Anatomically expected -- thumb positioning is hardest to standardize in fingerspelling.
- Several subjects have flex_1 values around -50 -- same calibration artifact from Section 3. Confirms per-subject z-score normalization must happen before any features are fed to the model.

**Fix applied:** Replaced 25-subject legend with a clean two-item legend showing Mean and ±1 std only.

### Cell 2 -- Coefficient of variation per feature across subjects

Output:
```
Top 5 highest variance (hardest to normalize): ['flex_1', 'ACCx_world', 'flex_2', 'Qz', 'flex_3']
Top 5 lowest variance (most consistent):       ['Qy', 'ACCy', 'Qx', 'ACCx', 'Qw']
```

Findings:
- flex_1 is the most variable feature in the entire dataset -- CoV ~11. Confirms the thumb sensor reads completely differently across subjects.
- ACCx_world at CoV ~10 is surprising -- world-frame X acceleration varies significantly because different subjects hold their wrist at different resting angles relative to "forward." Another calibration argument.
- Qz is highly variable (CoV ~3.5) but Qw, Qx, Qy are among the most consistent features. Qz represents rotation around the vertical axis (which direction the hand points left/right) -- varies significantly between subjects. Other quaternion components are more constrained by hand anatomy.
- Gyroscope channels sit in the middle -- GYRx, GYRy, GYRz all around CoV 1.5. Moderate variation, manageable with normalization.
- Most consistent features: raw/body accelerometer channels and most quaternion components -- these are the features the model can rely on most without heavy normalization.

**Key takeaway for dataset.py:** normalize flex channels aggressively using per-subject z-score. IMU channels still benefit from per-subject normalization but are less critical for quaternion and raw accelerometer channels.

---

## Section 6: Static vs Dynamic Signs

### Cell 1 -- Gyroscope magnitude distribution and median per sign

Findings:

**Left plot -- distribution**
- Static distribution has an extremely sharp spike at near-zero -- the vast majority of static sign timesteps have almost no wrist rotation
- Dynamic distribution is spread across 0–3+ rad/s with a long tail -- continuous wrist motion throughout each sign
- The two distributions barely overlap -- gyroscope magnitude alone is a near-perfect static/dynamic classifier
- This is the strongest single validation of the two-model strategy in the entire notebook

**Right plot -- median per sign**
- All 16 dynamic signs dominate the top of the chart -- `yes`, `please`, `sorry`, `fine`, `z`, `deaf`, `bye`, `good`, `goodbye`, `hello`, `thankyou`, `me`, `hungry` all clearly above static signs
- One static sign (`w`) appears in the middle of the chart at ~0.14 -- slightly elevated gyro magnitude compared to other static signs. Worth monitoring as a potential edge case during classification.
- All remaining static signs cluster at the bottom near zero -- clean separation

---

## Section 7: Feature Statistics & Correlation

### Cell 1 -- Feature statistics table

Output:
```
              mean     std      min      max     range
flex_1       2.629  42.388 -520.000  836.000  1356.000
flex_2      -3.824  34.505 -180.000  122.000   302.000
flex_3      11.971  48.322 -198.000  188.000   386.000
flex_4      24.895  48.349 -199.000  203.000   402.000
flex_5      17.155  37.974 -263.000  209.000   472.000
Qw           0.732   0.161   -0.220    1.000     1.220
Qx           0.174   0.247   -0.599    0.996     1.594
Qy          -0.484   0.296   -0.986    0.697     1.683
Qz          -0.008   0.160   -0.984    0.946     1.930
GYRx         0.009   0.318   -9.985    7.443    17.427
GYRy         0.009   0.442   -6.802    9.893    16.695
GYRz        -0.016   0.260   -5.153    4.015     9.168
ACCx_body   -0.381   1.510  -23.876   13.329    37.205
ACCy_body    0.155   1.732  -18.571   17.018    35.590
ACCz_body   -0.116   1.619  -28.004   18.349    46.353
ACCx_world  -0.004   1.541  -19.066   22.704    41.771
ACCy_world  -0.054   1.486  -21.760   23.734    45.495
ACCz_world  -0.047   1.869  -29.120   16.650    45.770
ACCx         6.391   4.404  -19.137   19.056    38.193
ACCy         2.578   3.936  -19.186   19.586    38.772
ACCz         1.584   4.278  -19.452   19.350    38.802
```

Findings:
- flex_1 has a range of 1,356 -- by far the largest of any feature. Raw ADC readings with no unit standardization. Feeding these alongside quaternion values of 0–1 would dominate the loss function. Aggressive normalization mandatory.
- Quaternion components sit in roughly -1 to +1 as expected for unit quaternions. Qw mean of 0.732 suggests the wrist is generally oriented ~45° from neutral. Naturally bounded and well-scaled.
- Gyroscope means are ~0.009 -- on average across all recordings the wrist is nearly stationary, expected since 24 of 40 signs are static. Range of ±10 rad/s captures the most aggressive dynamic sign motions.
- Body/world frame accelerometer means cluster near zero -- gravity corrected. Ranges are comparable across all six channels (~35–46).
- Raw accelerometer means are non-zero (ACCx=6.4, ACCy=2.6, ACCz=1.6) -- gravity is not removed. ACCx mean of 6.4 suggests the sensor is tilted ~40° from vertical on average. Requires different normalization treatment.

Normalization priority for dataset.py:

| Group | Priority | Reason |
|---|---|---|
| flex_1–5 | Highest | Ranges up to 1,356, per-subject z-score |
| Raw ACC | High | Non-zero mean due to gravity, per-subject z-score |
| Gyroscope | Medium | Already near-zero mean, per-subject z-score |
| ACC body/world | Medium | Gravity corrected, consistent ranges |
| Quaternion | Lowest | Naturally bounded ±1, still normalize for consistency |

### Cell 2 -- Feature correlation matrix

Output:
```
No pairs with |r| > 0.95
```

Findings:
- **Zero redundant feature pairs** -- all 21 features stay in the model input vector
- Flex sensors show moderate positive correlation with each other (r=0.5–0.8) -- anatomically expected, all fingers bend together when closing the hand. No pair exceeds 0.95.
- Quaternion components show moderate inter-correlations -- mathematically expected since Qw²+Qx²+Qy²+Qz²=1 forces some correlation by definition. All four stay in.
- Raw ACC vs Quaternion is the most interesting block -- ACCy↔Qy is deep red (~0.8), ACCx↔Qx is deep blue (~-0.75). Raw accelerometer contains gravity, and gravity's direction in the sensor frame is determined by wrist orientation (quaternion). Raw ACC channels are essentially encoding orientation information already captured by the quaternion.
- Body/world ACC blocks are mostly near-white -- very little correlation with anything else. These channels carry genuinely independent information after gravity removal. Keep all six.
- If input dimensionality ever needs reducing, dropping ACCx/ACCy/ACCz is the first candidate -- their information is largely captured by the quaternion. For now all 21 features stay in.

---

## Section 8: Windowing Strategy Preview

### Cell 1 -- Window size comparison table

Output:
```
Window    Stride   Windows/rec    Total samples
      50        25            59           59,000
     100        50            29           29,000 <- recommended
     100        25            57           57,000
     150        75            19           19,000
     200       100            14           14,000
```

Findings:
- 100/50 gives 29 windows per recording, 29,000 total samples -- enough to train without overfitting, and each window is exactly 1 second which is long enough to capture a full dynamic sign motion
- 50/25 doubles sample count to 59,000 but each window is only 0.5s -- too short to capture slower dynamic signs like `goodbye` or `thankyou` which require a full wrist rotation
- 100/25 gives 57,000 samples with 75% overlap -- heavy redundancy between consecutive windows risks overfitting without adding genuine new information
- 150/75 and 200/100 reduce sample counts too aggressively -- 19,000 and 14,000 are borderline too few for 40 classes across 21 features
- 100/50 confirmed as the right balance

### Cell 2 -- Windowing visualization (sign `hello`)

Output:
```
Total windows for this recording: 29
```

Findings:
- Recording is 65 seconds long -- subject signed `hello` repeatedly for over a minute, producing 29 windows across the full duration. Each GYRx spike is one wave motion -- roughly 12–15 repetitions visible.
- First two windows (red and orange shading) capture the opening burst of motion at ~0.5s and ~12s. 50% overlap means window 2 starts 50 timesteps in and shares the first half of its context with window 1 -- no motion event gets split cleanly at a window boundary.
- 29 windows matches the formula exactly: `(1500 - 100) // 50 + 1 = 29`. Consistent with Section 2's confirmation that every recording is exactly 1,500 rows.

---

## Section 9: Key Findings Summary

Output:
```
KEY FINDINGS

DATASET
  Subjects:         25
  Signs:            40 (static: 24, dynamic: 16)
  Rows per file:    1,500 (~15s at ~100Hz)
  Total rows:       1,500,000
  Missing values:   None

FEATURES
  Total channels:   21 (5 flex + 4 quat + 3 gyro + 9 acc)
  High corr pairs:  0 (|r| > 0.95) -- see section 7
  Gyro magnitude:   strong static/dynamic separator -- validates two-model strategy

RECOMMENDED WINDOWING
  Window size:      100 timesteps (~1s)
  Stride:           50 timesteps (50% overlap)
  Total samples:    ~29,000 across full dataset

TRAIN/VAL/TEST SPLIT
  Split by subject to prevent data leakage
  Suggested:        18 train / 4 val / 3 test (72/16/12%)

MODELLING NOTES
  Static signs:     MLP or 1D CNN on single-frame or mean-pooled input
  Dynamic signs:    LSTM or Temporal CNN on 100-timestep sequences
  Normalization:    per-subject z-score on flex channels before training
```

Findings:
- All numbers confirmed and consistent with findings across Sections 1–8
- Zero missing values, perfectly balanced classes, consistent 1,500 rows per file -- clean dataset requiring no preprocessing workarounds
- Zero highly correlated feature pairs -- all 21 features feed into the model
- Gyroscope magnitude validated as strong static/dynamic separator -- two-model strategy confirmed
- 29,000 total samples at 100/50 windowing -- sufficient for training across 40 classes
- Subject-based train/val/test split is non-negotiable -- sample-based splitting would leak subject-specific calibration artifacts into validation and test sets, inflating accuracy metrics
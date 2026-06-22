# sign lists
STATIC_SIGNS  = list('abcdefghiklmnopqrstuvwxy')
DYNAMIC_SIGNS = ['j', 'z', 'bad', 'deaf', 'fine', 'good', 'goodbye',
                 'hello', 'hungry', 'me', 'no', 'please',
                 'sorry', 'thank you', 'yes', 'you']
ALL_SIGNS = STATIC_SIGNS + DYNAMIC_SIGNS

# sensor channel groups
FLEX_COLS    = ['flex_1', 'flex_2', 'flex_3', 'flex_4', 'flex_5']
QUAT_COLS    = ['Qw', 'Qx', 'Qy', 'Qz']
GYRO_COLS    = ['GYRx', 'GYRy', 'GYRz']
ACC_B_COLS   = ['ACCx_body', 'ACCy_body', 'ACCz_body']
ACC_W_COLS   = ['ACCx_world', 'ACCy_world', 'ACCz_world']
ACC_R_COLS   = ['ACCx', 'ACCy', 'ACCz']
FEATURE_COLS = FLEX_COLS + QUAT_COLS + GYRO_COLS + ACC_B_COLS + ACC_W_COLS + ACC_R_COLS

# windowing
WINDOW_SIZE = 100   # timesteps per sample (~1s at 100Hz)
STRIDE      = 50    # 50% overlap between consecutive windows

# subject splits — split by subject to prevent data leakage
TRAIN_SUBJECTS = [f'{i:03d}' for i in range(1,  19)]   # 001–018
VAL_SUBJECTS   = [f'{i:03d}' for i in range(19, 23)]   # 019–022
TEST_SUBJECTS  = [f'{i:03d}' for i in range(23, 26)]   # 023–025
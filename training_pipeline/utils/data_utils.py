import numpy as np

from constants import DTYPES, CIDX, TARG_FEAT, MISSING_VAL


def read_csv(data_path: str) -> tuple[np.ndarray, dict]:
    """Read csv data file.
    """
    # Read file
    raw_data = []
    with open(data_path, 'r') as file:
        idx = 0
        for line in file:
            if idx == 0:
                idx += 1
                continue
            line = line.strip().split(',')
            for cidx in CIDX:
                if DTYPES[cidx] == 'int':
                    if line[cidx] in MISSING_VAL:
                        line[cidx] = None
                    else:
                        line[cidx] = str(line[cidx])
                elif DTYPES[cidx] == 'float':
                    if line[cidx] in MISSING_VAL:
                        line[cidx] = np.nan
                    else:
                        line[cidx] = float(line[cidx])
                else:
                    if line[cidx] in MISSING_VAL:
                        line[cidx] = None
                    else:
                        line[cidx] = str(line[cidx])
            raw_data.append(line)

    # Store data as ndarray
    data = np.array(raw_data).astype('object')
    for cidx in CIDX:
        if DTYPES[cidx] == 'int':
            data[:, cidx] = data[:, cidx].astype('object')
        else:
            data[:, cidx] = data[:, cidx].astype(DTYPES[cidx])

    # In case target is str, convert to int
    targ_conv = {}
    if DTYPES[TARG_FEAT[0]] == 'object':
        k = 0
        for i in set([i[0] for i in data[:, TARG_FEAT] if i[0]]):
            if i in MISSING_VAL:
                continue
            targ_conv[i] = k
            k += 1
    return data, targ_conv


def read_csv2(data_path: str) -> tuple[np.ndarray, dict]:
    """Read csv data file.
    """
    # Read file
    raw_data = []
    with open(data_path, 'r') as file:
        idx = 0
        for line in file:
            if idx == 0:
                idx += 1
                continue
            line = line.strip().split(',')
            for cidx in CIDX:
                if DTYPES[cidx] == 'int':
                    if line[cidx] in MISSING_VAL:
                        line[cidx] = -9999
                    else:
                        line[cidx] = np.int64(line[cidx])
                elif DTYPES[cidx] == 'float':
                    if line[cidx] in MISSING_VAL:
                        line[cidx] = np.nan
                    else:
                        line[cidx] = np.float32(line[cidx])
                else:
                    if line[cidx] in MISSING_VAL:
                        line[cidx] = None
                    else:
                        line[cidx] = str(line[cidx])
            raw_data.append(line)

    for cidx in CIDX:
        col = []
        for idx in range(len(raw_data)):
            col.append(raw_data[idx][cidx])
        col = np.array(col, dtype=DTYPES[cidx])
        if cidx == 0:
            data = col
        else:
            data = np.c_[data, col]

    # In case target is str, convert to int
    targ_conv = {}
    if DTYPES[TARG_FEAT[0]] == 'object':
        k = 0
        for i in set([i[0] for i in data[:, TARG_FEAT] if i[0]]):
            if i in MISSING_VAL:
                continue
            targ_conv[i] = k
            k += 1
    return data, targ_conv


def data_split(X, date_cidx):
    """Split data along date axis."""
    # Sort array by date columns
    X_sorted = np.array(X[X[:, date_cidx].argsort()], copy=True)

    # Split data into train, validation, and test set
    X_train, X_val = np.split(X_sorted, [int(0.80 * len(X_sorted))])
    X_val, X_test = np.split(X_val, [int(0.5 * len(X_val))])

    return X_train, X_val, X_test

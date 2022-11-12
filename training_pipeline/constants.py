import numpy as np

# # File name
# FILENAME = 'test.csv'

# # Target column
# TARGET = 'y'

# # Data specs
# CNAMES = ['y', 'x1', 'x2', 'x3']
# # DTYPES can be 'object', 'float', or 'int'
# DTYPES = ['int', 'float', 'int', 'object']
# CIDX = [i for i in range(len(CNAMES))]

# File nameMISSING_VAL
FILENAME = 'games.csv'

# Target column
TARGET = 'winner'

# Data specs
CNAMES = ['gameId', 'creationTime', 'gameDuration', 'seasonId', 'winner', 'firstBlood', 'firstTower', 'firstInhibitor', 'firstBaron', 'firstDragon', 'firstRiftHerald', 't1_champ1id', 't1_champ1_sum1', 't1_champ1_sum2', 't1_champ2id', 't1_champ2_sum1', 't1_champ2_sum2', 't1_champ3id', 't1_champ3_sum1', 't1_champ3_sum2', 't1_champ4id', 't1_champ4_sum1', 't1_champ4_sum2', 't1_champ5id', 't1_champ5_sum1', 't1_champ5_sum2', 't1_towerKills', 't1_inhibitorKills', 't1_baronKills', 't1_dragonKills', 't1_riftHeraldKills', 't1_ban1', 't1_ban2', 't1_ban3', 't1_ban4', 't1_ban5', 't2_champ1id', 't2_champ1_sum1', 't2_champ1_sum2', 't2_champ2id', 't2_champ2_sum1', 't2_champ2_sum2', 't2_champ3id', 't2_champ3_sum1', 't2_champ3_sum2', 't2_champ4id', 't2_champ4_sum1', 't2_champ4_sum2', 't2_champ5id', 't2_champ5_sum1', 't2_champ5_sum2', 't2_towerKills', 't2_inhibitorKills', 't2_baronKills', 't2_dragonKills', 't2_riftHeraldKills', 't2_ban1', 't2_ban2', 't2_ban3', 't2_ban4', 't2_ban5']  # noqa: E501

# DTYPES can be 'object', 'float', or 'int'
DTYPES = ['int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int']  # noqa: E501

# Column indices
CIDX = [i for i in range(len(CNAMES))]

# Features not to model on
NON_MODELING_FEATURES = ['gameId', 'creationTime', 'seasonId']

# Column index for date feature
DATE_FEATURE_CIDX = 1

# NOTE: Do not modify!
TARG_FEAT = [i for i in CIDX if CNAMES[i] == TARGET]
NUM_FEAT = [i for i in CIDX if DTYPES[i] == 'float' and CNAMES[i] not in [TARGET] + NON_MODELING_FEATURES]
CAT_FEAT = [i for i in CIDX if DTYPES[i] != 'float' and CNAMES[i] not in [TARGET] + NON_MODELING_FEATURES]

# Missing value types
MISSING_VAL = ['', 'nan', 'NA', 'NaN', 'None', '.', np.nan, None, 'na', -9999]

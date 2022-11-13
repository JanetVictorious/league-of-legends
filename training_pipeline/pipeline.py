import os
import logging

import numpy as np

from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import KBinsDiscretizer, OneHotEncoder
from sklearn.compose import make_column_transformer
from sklearn.metrics import f1_score, confusion_matrix

import dill

from constants import FILENAME, TARGET, TARG_FEAT, MISSING_VAL, DATE_FEATURE_CIDX, CNAMES, CIDX, MOD_FEAT, LOW_CAR, HIGH_CAR  # noqa: E501
from utils.data_utils import read_csv2, data_split
from utils.models import ModelName, _services
from utils.params import model_params


def run_pipeline(input_dir: str = ...,
                 output_dir: str = ...,
                 model_name: str = ...) -> None:
    """Train classifier.

    Given an input dataset, split, preprocess, train model, and export results.
    """
    logging.info('=' * 50)

    # Create model object
    logging.info(f'Creating model object {model_name}...')
    params = model_params.get(model_name)
    MODEL = _services.get(ModelName(model_name).value, **params)

    # Create output directory if not exists
    logging.info('Create output directory...')
    output_path = os.path.join(output_dir, 'serving')
    os.makedirs(output_path, exist_ok=True)

    logging.info(f'Target name: {TARGET}')

    # Load data
    data_path = os.path.abspath(os.path.join(input_dir, FILENAME))
    logging.info(f'Loading data from: {data_path}')

    data, _ = read_csv2(data_path)

    logging.info(f'Shape of data: {(data.shape)}')

    logging.info('Make sure target is present...')

    # Make sure target is present
    missing_targ = [i[0] not in MISSING_VAL for i in data[:, TARG_FEAT]]
    data = data[missing_targ, :]

    logging.info(f'Shape of dataframe: {data.shape}')

    # Columns for modeling features
    # features = NUM_FEAT + CAT_FEAT
    # logging.info(f'Nr of modeling features: {len(features)}')

    # Modeling features column index
    mod_feat_cidx = [i for i in CIDX if CNAMES[i] in MOD_FEAT]

    # Feature mapping
    mod_feat_map = np.c_[np.arange(len(MOD_FEAT)), mod_feat_cidx]
    logging.info(f'Feature mapping between raw and modeling data:\n{mod_feat_map}')

    # Map modeling features to high or low cardinality
    low_car_cidx = list(set(mod_feat_map[:, 1]).intersection(set([i for i in CIDX if CNAMES[i] in LOW_CAR])))
    logging.info(f'Low cardinality feature cidx: {low_car_cidx}')

    high_car_cidx = list(set(mod_feat_map[:, 1]).intersection(set([i for i in CIDX if CNAMES[i] in HIGH_CAR])))
    logging.info(f'High cardinality feature cidx: {high_car_cidx}')

    low_car = [mod_feat_map[mod_feat_map[:, 1] == i, 0][0] for i in low_car_cidx]
    high_car = [mod_feat_map[mod_feat_map[:, 1] == i, 0][0] for i in high_car_cidx]

    # Sort lists
    low_car.sort()
    high_car.sort()

    # Reduce index by 1 since target feature will not be present in modeling set
    low_car = [i - 1 for i in low_car]
    high_car = [i - 1 for i in high_car]

    logging.info(f'Low cardinaly column indices in modeling data: {low_car}')
    logging.info(f'High cardinaly column indices in modeling data: {high_car}')

    logging.info('Create preprocessors...')

    # Numerical preprocessor
    num_pp = make_pipeline(
        SimpleImputer(strategy='median'),
        KBinsDiscretizer(n_bins=5, strategy='kmeans', encode='ordinal')
    )

    # Categorical preprocessor
    cat_pp = make_pipeline(
        SimpleImputer(strategy='most_frequent'),
        OneHotEncoder(sparse=False, handle_unknown='ignore')
    )

    logging.info('Create transformer...')

    # Column transformer
    if low_car and high_car:
        preprocessor = make_column_transformer(
            (num_pp, high_car),
            (cat_pp, low_car)
        )
    elif low_car and not high_car:
        preprocessor = make_column_transformer(
            (cat_pp, low_car)
        )
    elif high_car and not low_car:
        preprocessor = make_column_transformer(
            (num_pp, high_car)
        )

    logging.info('Create model pipeline...')

    # Model pipeline
    model = make_pipeline(
        preprocessor,
        MODEL
    )

    logging.info('Split data...')

    # Split data
    data_train, data_val, data_test = data_split(data, DATE_FEATURE_CIDX)

    logging.info(f'Shape training set: {data_train.shape}')
    logging.info(f'Shape validation set: {data_val.shape}')
    logging.info(f'Shape test set: {data_test.shape}')

    # Extract modeling columns
    # Train set
    X_train, y_train = data_train[:, mod_feat_cidx[1:]], data_train[:, mod_feat_cidx[0]]
    logging.info(f'Shape of training features data: {X_train.shape}')
    logging.info(f'Shape of training label data: {y_train.shape}')

    # Validation set
    X_val, y_val = data_val[:, mod_feat_cidx[1:]], data_val[:, mod_feat_cidx[0]]
    logging.info(f'Shape of validation features data: {X_val.shape}')
    logging.info(f'Shape of validation label data: {y_val.shape}')

    # Test set
    X_test, y_test = data_test[:, mod_feat_cidx[1:]], data_test[:, mod_feat_cidx[0]]
    logging.info(f'Shape of test features data: {X_test.shape}')
    logging.info(f'Shape of test label data: {y_test.shape}')

    # Modify target to 0, 1
    y_train = y_train - 1
    y_val = y_val - 1
    y_test = y_test - 1

    # # Train set
    # X_train = data_train[:, features]
    # y_train = np.int32(data_train[:, TARG_FEAT]) - 1
    # y_train = y_train.reshape(-1,)

    # # Validation set
    # X_val = data_val[:, features]
    # y_val = np.int32(data_val[:, TARG_FEAT]) - 1
    # y_val = y_val.reshape(-1,)

    # # Test set
    # X_test = data_test[:, features]
    # y_test = np.int32(data_test[:, TARG_FEAT]) - 1
    # y_test = y_test.reshape(-1,)

    # Split data
    # X_train, X_test, y_train, y_test = train_test_split(
    #     X, y, test_size=0.33, random_state=43)

    logging.info('Train model...')

    # Fit model using pipeline
    model.fit(X_train, y_train)

    logging.info('Results...')
    y_pred_val = model.predict(X_val)
    y_pred_test = model.predict(X_test)

    f_score_val = f1_score(y_val, y_pred_val, average='macro')
    cm_val = confusion_matrix(y_val, y_pred_val)
    f_score_test = f1_score(y_test, y_pred_test, average='macro')
    cm_test = confusion_matrix(y_test, y_pred_test)

    logging.info('Validation set:')
    logging.info(f'F1 score: {f_score_val}')
    logging.info(f'Confusion matrix: \n{cm_val}')

    logging.info('Test set:')
    logging.info(f'F1 score: {f_score_test}')
    logging.info(f'Confusion matrix: \n{cm_test}')

    # Export results
    model_path = os.path.abspath(os.path.join(output_path, f'{model_name}_model.pkl'))
    with open(model_path, 'wb') as file:
        dill.dump((model, TARG_FEAT), file)

    logging.info(f'Output saved to: {model_path}')

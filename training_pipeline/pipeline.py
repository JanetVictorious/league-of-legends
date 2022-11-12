import os
import logging

import numpy as np

from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import KBinsDiscretizer, OneHotEncoder
from sklearn.compose import make_column_transformer
from sklearn.metrics import f1_score, confusion_matrix

import dill
import json

from constants import FILENAME, TARGET, TARG_FEAT, MISSING_VAL, NUM_FEAT, CAT_FEAT, DATE_FEATURE_CIDX
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
    features = NUM_FEAT + CAT_FEAT
    logging.info(f'Nr of modeling features: {len(features)}')

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
    # NOTE: Here since we're working with the column indices
    # we need to re-map them to fit the training dataset X
    preprocessor = make_column_transformer(
        (num_pp, [i for i in range(len(NUM_FEAT))]),
        (cat_pp, [i for i in range(len(NUM_FEAT), len(NUM_FEAT + CAT_FEAT))])
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

    # Train set
    X_train = data_train[:, features]
    y_train = np.int32(data_train[:, TARG_FEAT]) - 1
    y_train = y_train.reshape(-1,)

    # Validation set
    X_val = data_val[:, features]
    y_val = np.int32(data_val[:, TARG_FEAT]) - 1
    y_val = y_val.reshape(-1,)

    # Test set
    X_test = data_test[:, features]
    y_test = np.int32(data_test[:, TARG_FEAT]) - 1
    y_test = y_test.reshape(-1,)

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
        dill.dump((model, features, TARG_FEAT), file)

    logging.info(f'Output saved to: {model_path}')

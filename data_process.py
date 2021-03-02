import pandas as pd
import pathlib


def load_data(file_name):
    data_path = pathlib.Path('data')
    return pd.read_csv(data_path / file_name)


def get_features_df():

    df_uti_resist_lab = load_data('all_uti_resist_labels.csv')

    # Test and Train labels and features
    test_uncomp_uti_features = load_data('test_uncomp_uti_features.csv')
    train_uncomp_uti_features = load_data('train_uncomp_uti_features.csv')

    # Merged train and test data labels and features
    all_uncomp_uti_features = test_uncomp_uti_features.append(train_uncomp_uti_features)
    all_uncomp_uti_features = all_uncomp_uti_features.merge(df_uti_resist_lab[['example_id', 'is_train']])

    return all_uncomp_uti_features


def get_val_preds():
    # predicted probabilities of resistance for multiple train/validataion splits
    # across all antibiotic of interest using the optimal tuned hyperparameters
    df_prescript = load_data('all_prescriptions.csv')
    df_uti_resist_lab = load_data('all_uti_resist_labels.csv')
    val_preds_res = load_data('val_predictions.csv')
    val_preds_res = val_preds_res.merge(df_uti_resist_lab.drop(columns=['is_train', 'uncomplicated']),
                                        on='example_id', how='inner') \
        .merge(df_prescript.drop(columns=['is_train']), on='example_id', how='inner')

    return val_preds_res


def get_test_predictions():
    # Predicited probabilities of resistance for all (training and test) specimens
    # Using optimal tuned hyperparameters and reproduced pipeline 
    test_predictions_opt = load_data('test_predictions_optimal.csv')
    test_predictions_e2e = load_data('test_predictions_e2e.csv')

    return test_predictions_opt


def get_test_policy_df():
    # Predicted probabilities, true resistance labels and observed prescription, 
    # algorithm reccomendation, and final reccomednation (defaulting to observed
    # prescription if algorithm defers)
    test_policy_opt = load_data('test_policy_optimal.csv')
    test_policy_e2e = load_data('test_policy_e2e.csv')

    # Policy df with dropped predicted probabilities
    test_rec_opt = test_policy_opt.copy()[['example_id', 'NIT', 'SXT', 'CIP', 'LVX', 'prescription', 'rec_final']]
    test_rec_e2e = test_policy_e2e.copy()[['example_id', 'NIT', 'SXT', 'CIP', 'LVX', 'prescription', 'rec_final']]

    return test_policy_opt


def add_prescription(df):
    prescript = load_data('all_prescriptions.csv').drop(columns=['is_train'])
    return df.merge(prescript, how='left', on='example_id')


def add_labels(df):
    labels = load_data('all_uti_resist_labels.csv').drop(columns=['is_train', 'uncomplicated'])
    return df.merge(labels, how='left', on='example_id')


def add_race(df):
    df['race'] = df['demographics - is_white'].replace(to_replace=[0, 1],
                                                       value=['non-white', 'white'])
    return df


def age_group(x):
    """Add age group (0, 1, 2)"""
    q1 = 27.0
    q2 = 40.0
    if x.age <= q1:
        return 0
    elif x.age <= q2:
        return 1
    else:
        return 2


def add_age(df):
    df['age'] = df['demographics - age']
    df['age_group'] = df.apply(age_group, axis=1)
    return df


def add_race_age(df):
    features = add_age(add_race(get_features_df()))
    id_race = features[['example_id', 'race', 'age_group']]
    return df.merge(id_race, on='example_id', how='left')


def get_train_test(df):
    train_df = df.query('is_train == 1')
    test_df = df.query('is_train == 0')

    return train_df, test_df


def get_white_data(df):
    return df.query('race == "white"')


def get_nonwhite_data(df):
    return df.query('race == "non-white"')


def get_age_groups(df):
    young = df.query('age_group == 0')
    mid = df.query('age_group == 1')
    old = df.query('age_group == 2')
    return young, mid, old



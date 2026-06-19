import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder
import joblib
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

# Load the dataset
dt_Train=pd.read_csv("dataset\\kddTrain.csv")
dt_Test=pd.read_csv("dataset\\kddTest.csv")

# Define the column names for the dataset
columns_list = [
    'duration', 'protocol_type', 'service', 'flag', 'src_bytes', 'dst_bytes', 'land',
    'wrong_fragment', 'urgent', 'hot', 'num_failed_logins', 'logged_in', 'num_compromised',
    'root_shell', 'su_attempted', 'num_root', 'num_file_creations', 'num_shells',
    'num_access_files', 'num_outbound_cmds', 'is_host_login', 'is_guest_login', 'count',
    'srv_count', 'serror_rate', 'srv_serror_rate', 'rerror_rate', 'srv_rerror_rate',
    'same_srv_rate', 'diff_srv_rate', 'srv_diff_host_rate', 'dst_host_count', 'dst_host_srv_count',
    'dst_host_same_srv_rate', 'dst_host_diff_srv_rate', 'dst_host_same_src_port_rate',
    'dst_host_srv_diff_host_rate', 'dst_host_serror_rate', 'dst_host_srv_serror_rate',
    'dst_host_rerror_rate', 'dst_host_srv_rerror_rate', 'target', 'difficulty_level'
]

# Assign the column names to the training and testing datasets
dt_Train.columns = columns_list
dt_Test.columns = columns_list


# Drop the 'difficulty_level' column from both training and testing datasets
dt_Train.drop(['difficulty_level'], axis=1, inplace=True)
dt_Test.drop(['difficulty_level'], axis=1, inplace=True)

# Encode categorical features using LabelEncoder
# 1. PROTOCOL TYPE COLUMN
le_proto = LabelEncoder()
# Train data par fit aur transform
dt_Train['protocol_type'] = le_proto.fit_transform(dt_Train['protocol_type'].astype(str))
# Test data par transform (Bina fit kiye, sirf transform!)
dt_Test['protocol_type'] = dt_Test['protocol_type'].astype(str).map(lambda s: s if s in le_proto.classes_ else le_proto.classes_[0])
dt_Test['protocol_type'] = le_proto.transform(dt_Test['protocol_type'])
# Save encoder file
joblib.dump(le_proto, 'protocol_type_encoder.pkl')


# 2. SERVICE COLUMN
le_service = LabelEncoder()
# Train data par fit aur transform
dt_Train['service'] = le_service.fit_transform(dt_Train['service'].astype(str))
# Test data par transform safely
dt_Test['service'] = dt_Test['service'].astype(str).map(lambda s: s if s in le_service.classes_ else le_service.classes_[0])
dt_Test['service'] = le_service.transform(dt_Test['service'])
# Save encoder file
joblib.dump(le_service, 'service_encoder.pkl')


# 3. FLAG COLUMN
le_flag = LabelEncoder()
# Train data par fit aur transform
dt_Train['flag'] = le_flag.fit_transform(dt_Train['flag'].astype(str))
# Test data par transform safely
dt_Test['flag'] = dt_Test['flag'].astype(str).map(lambda s: s if s in le_flag.classes_ else le_flag.classes_[0])
dt_Test['flag'] = le_flag.transform(dt_Test['flag'])
# Save encoder file
joblib.dump(le_flag, 'flag_encoder.pkl')

# encoding the target variable in the training dataset
dt_Train['target'] = dt_Train['target'].apply(lambda x: 0 if x == 'normal' else 1)

# encoding the target variable in the test dataset
dt_Test['target'] = dt_Test['target'].apply(lambda x: 0 if x == 'normal' else 1)


# Prepare the training and testing data
x_train = dt_Train.drop(['target'], axis=1).values
y_train = dt_Train['target'].values
x_test = dt_Test.drop(['target'], axis=1).values
y_test = dt_Test['target'].values


# Train the XGBoost model
model = XGBClassifier(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    random_state=42,
    use_label_encoder=False,
    eval_metric='logloss'
)
model.fit(x_train, y_train)

# Make predictions on the test set
y_pred = model.predict(x_test)

# save the trained model to a file using joblib
joblib.dump(model, 'intrusion_model.pkl')
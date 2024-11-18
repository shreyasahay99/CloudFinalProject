import os
import pandas as pd
import h2o
import boto3
from flask import Flask
from io import StringIO
from sklearn.preprocessing import LabelEncoder
from config.config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, S3_BUCKET, S3_KEY, LOCAL_MODEL_PATH

print("Config values:", AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, S3_BUCKET, S3_KEY, LOCAL_MODEL_PATH)

# Initialize the Flask app
app = Flask(__name__, static_folder='../static')

# Initialize H2O
h2o.init()

# Initialize S3 Client
s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name='us-east-1'
)

# Helper function to download file from S3
def download_from_s3(s3_key, local_path):
    try:
        print(f"Downloading {s3_key} from S3 to {local_path}")
        s3.download_file(S3_BUCKET, s3_key, local_path)
        print("Download successful.")
    except Exception as e:
        raise RuntimeError(f"Failed to download {s3_key} from S3: {str(e)}")

# Step 1: Download and Load the Model from S3
try:
    print("Checking if model file exists locally...")
    if not os.path.exists(LOCAL_MODEL_PATH):
        download_from_s3(S3_KEY, LOCAL_MODEL_PATH)

    if os.path.exists(LOCAL_MODEL_PATH):
        print("Loading H2O model from local file...")
        model = h2o.import_mojo(LOCAL_MODEL_PATH)
        with app.app_context():
            app.config['MODEL'] = model
            print("Model loaded and set in app config successfully.")
    else:
        raise FileNotFoundError(f"Model file not found at {LOCAL_MODEL_PATH}")

except Exception as e:
    print(f"Error during model setup: {str(e)}")

# Step 2: Download and Initialize the Training Frame
try:
    s3_data_key = "Customer-Churn-Records.csv"
    print(f"Downloading training data from S3: {s3_data_key}")
    obj = s3.get_object(Bucket=S3_BUCKET, Key=s3_data_key)
    csv_string = obj['Body'].read().decode('utf-8')

    # Load CSV into a DataFrame
    data = StringIO(csv_string)
    df = pd.read_csv(data)
    print("Training data loaded successfully.")

    # Rename columns for consistency
    df.rename(columns={
        'Satisfaction Score': 'SatisfactionScore',
        'Card Type': 'CardType',
        'Point Earned': 'PointEarned'
    }, inplace=True)

    # Encode categorical columns
    categorical_columns = ['Gender', 'Geography', 'CardType']
    for col in categorical_columns:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        print(f"Encoded column: {col}")

    # Convert to H2OFrame
    training_frame = h2o.H2OFrame(df)
    print("Training frame initialized.")

    # Set training frame in app config
    with app.app_context():
        app.config['TRAINING_FRAME'] = training_frame
        print("Training frame set in app config successfully.")

except Exception as e:
    print(f"Error during training frame setup: {str(e)}")

# Debugging: Verify Model and Training Frame
with app.app_context():
    model_check = app.config.get('MODEL')
    training_frame_check = app.config.get('TRAINING_FRAME')
    if model_check:
        print("Debug: Model is loaded and available in app config.")
    else:
        print("Debug: Model is NOT loaded in app config.")

    if training_frame_check:
        print("Debug: Training frame is loaded and available in app config.")
        print("Training frame columns:", training_frame_check.columns)
    else:
        print("Debug: Training frame is NOT loaded in app config.")

# Register the blueprint after initialization
from flaskapp.routes import main
app.register_blueprint(main)

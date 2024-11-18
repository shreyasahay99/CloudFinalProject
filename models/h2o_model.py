import h2o
import os
import boto3

S3_BUCKET = "newscatayerhs"
S3_KEY = "h2o_models/GBM_4_AutoML_3_20241110_193552.zip"
# LOCAL_MODEL_PATH = "/home/ec2-user/trained_model.zip"
LOCAL_MODEL_PATH = "/Users/shreya/Documents/CC-Finalproject/data/models/trained_model.zip"

def download_model_from_s3():
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name='us-east-1'
        )
        s3.download_file(S3_BUCKET, S3_KEY, LOCAL_MODEL_PATH)
        print("Model downloaded successfully.")
    except Exception as e:
        print(f"Error downloading model from S3: {str(e)}")
        raise

def load_model():
    try:
        model = h2o.import_mojo(LOCAL_MODEL_PATH)
        print("Model loaded successfully.")
        return model
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        raise

def predict(model, data):
    try:
        input_data = list(data.values())
        column_names = list(data.keys())
        frame = h2o.H2OFrame([input_data])
        frame.columns = column_names
        prediction = model.predict(frame)
        return float(prediction[0, 0])
    except Exception as e:
        print(f"Error during prediction: {str(e)}")
        raise

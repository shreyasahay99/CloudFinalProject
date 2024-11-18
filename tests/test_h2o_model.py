import pytest
import h2o
from unittest.mock import patch
from models.h2o_model import download_model_from_s3, load_model, predict

@patch('models.h2o_model.boto3.client')
def test_download_model_from_s3(mock_boto_client):
    mock_s3 = mock_boto_client.return_value
    mock_s3.download_file.return_value = None
    download_model_from_s3()
    mock_s3.download_file.assert_called_once()

def test_load_model():
    h2o.init()
    model = load_model()
    assert model is not None
    h2o.shutdown()

def test_predict_function():
    h2o.init()
    model = load_model()
    sample_data = {'Gender': 1, 'Geography': 0, 'IsActiveMember': 1, 'Age': 35.0, 'CreditScore': 700.0, 'Balance': 50000.0, 'SatisfactionScore': 4.0, 'PointEarned': 300.0, 'Tenure': 5.0, 'EstimatedSalary': 60000.0, 'NumOfProducts': 2.0, 'CardType': 1, 'HasCrCard': 1}
    result = predict(model, sample_data)
    assert isinstance(result, float)
    assert 0.0 <= result <= 1.0
    h2o.shutdown()

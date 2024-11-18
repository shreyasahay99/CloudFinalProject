import pytest
from flaskapp import app
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_route(client):
    response = client.get('/')
    assert response.status_code == 200

def test_predict_route_missing_data(client):
    response = client.post('/predict', data={})
    assert response.status_code == 200
    assert b"Missing input" in response.data

def test_predict_route_valid_data(client):
    sample_data = {
        'Gender': '1', 'Geography': '0', 'IsActiveMember': '1', 'Age': '35', 
        'CreditScore': '700', 'Balance': '50000', 'SatisfactionScore': '4', 
        'PointEarned': '300', 'Tenure': '5', 'EstimatedSalary': '60000', 
        'NumOfProducts': '2', 'CardType': '1', 'HasCrCard': '1'
    }
    response = client.post('/predict', data=sample_data)
    assert response.status_code == 200
    assert b"Churn Probability" in response.data

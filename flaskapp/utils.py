import os
import boto3
import h2o
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
from flask import current_app
import base64

def configure_aws(app):
    """
    Configures AWS credentials using environment variables.
    """
    app.config['AWS_ACCESS_KEY_ID'] = os.getenv('AWS_ACCESS_KEY_ID')
    app.config['AWS_SECRET_ACCESS_KEY'] = os.getenv('AWS_SECRET_ACCESS_KEY')
    app.config['AWS_REGION'] = 'us-east-1'

def initialize_h2o():
    """
    Initializes the H2O server.
    """
    try:
        h2o.init()
        print("H2O initialized successfully.")
    except Exception as e:
        print(f"Error initializing H2O: {str(e)}")

def set_training_frame(frame):
    """
    Sets the training frame in Flask app config.
    """
    current_app.config['TRAINING_FRAME'] = frame
    print("Training frame set successfully in app config.")

def get_training_frame():
    """
    Retrieves the training frame from Flask app config.
    """
    training_frame = current_app.config.get('TRAINING_FRAME')
    if training_frame is None:
        print("Warning: Training frame is not initialized.")
    return training_frame

def set_model(loaded_model):
    """
    Sets the model in Flask app config.
    """
    current_app.config['MODEL'] = loaded_model
    print("Model set successfully in app config.")

def get_model():
    """
    Retrieves the model from Flask app config.
    """
    model = current_app.config.get('MODEL')
    if model is None:
        print("Warning: Model is not initialized.")
    return model

def plot_variable_importance(model):
    """
    Plots the variable importance of the model.
    """
    try:
        varimp = model.varimp(use_pandas=True)
        plt.figure(figsize=(10, 6))
        plt.barh(varimp['variable'], varimp['relative_importance'], color='skyblue')
        plt.xlabel("Relative Importance")
        plt.ylabel("Features")
        plt.title("Variable Importance Plot")
        plt.gca().invert_yaxis()

        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plot_data = base64.b64encode(buf.getvalue()).decode('utf-8')
        plt.close()
        return plot_data

    except Exception as e:
        print(f"Error generating variable importance plot: {str(e)}")
        return None

def plot_partial_dependency(feature, model):
    """
    Generates a partial dependency plot for the specified feature.
    """
    try:
        training_frame = get_training_frame()
        if training_frame is None:
            print("Training frame is not initialized.")
            return None

        partial_data = model.partial_plot(data=training_frame, cols=[feature], plot=True, server=True)

        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plot_data = base64.b64encode(buf.getvalue()).decode('utf-8')
        plt.close()
        return plot_data

    except Exception as e:
        print(f"Error generating partial plot for {feature}: {e}")
        return None
def plot_scoring_history(model):
    """
    Plots the training and validation RMSE and log loss over time from the model's scoring history.
    Returns a base64-encoded image of the plot.
    """
    try:
        # Get the scoring history as a DataFrame
        scoring_history = model.score_history()

        # Initialize the plot
        plt.figure(figsize=(12, 8))
        print(f"The columns in the validation plot {scoring_history.columns}")
        # Plot Training RMSE
        if 'training_rmse' in scoring_history.columns:
            plt.plot(scoring_history['training_rmse'], label='Training RMSE', marker='o')

        # Plot Validation RMSE (if available)
        if 'validation_rmse' in scoring_history.columns:
            plt.plot(scoring_history['validation_rmse'], label='Validation RMSE', marker='o', linestyle='--')

        # Plot Training Log Loss (if available)
        if 'training_logloss' in scoring_history.columns:
            plt.plot(scoring_history['training_logloss'], label='Training Log Loss', marker='s')

        # Plot Validation Log Loss (if available)
        if 'validation_logloss' in scoring_history.columns:
            plt.plot(scoring_history['validation_logloss'], label='Validation Log Loss', marker='s', linestyle='--')
        if 'training_auc' in scoring_history.columns:
            plt.plot(scoring_history['training_auc'], label='Training Accuracy', marker='s', linestyle='--')
        if 'training_classification_error' in scoring_history.columns:
            plt.plot(scoring_history['training_classification_error'], label='Training Classification Error', marker='s', linestyle='--')
        # Check if any metrics were plotted
        if not any(col in scoring_history.columns for col in ['training_rmse', 'validation_rmse', 'training_logloss', 'validation_logloss']):
            raise ValueError("No recognized metrics ('training_rmse', 'validation_rmse', 'training_logloss', 'validation_logloss') found in the scoring history.")

        # Customize the plot
        plt.xlabel('Number of Trees or Iterations')
        plt.ylabel('Metric Value')
        plt.title('Model Scoring History')
        plt.legend(loc='best')
        plt.grid(True)

        # Save the plot to a base64-encoded image
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        plot_data = base64.b64encode(buf.getvalue()).decode('utf-8')
        plt.close()

        return plot_data

    except Exception as e:
        print(f"Error in plot_scoring_history: {str(e)}")
        return None

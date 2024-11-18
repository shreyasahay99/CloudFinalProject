from flask import Blueprint, request, render_template, jsonify, current_app
from flaskapp.utils import plot_partial_dependency, plot_variable_importance, plot_scoring_history
import h2o
import base64
from io import BytesIO
import matplotlib.pyplot as plt

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')


def get_model_and_training_frame():
    """
    Helper function to retrieve the model and training frame from the app config.
    """
    with current_app.app_context():
        model = current_app.config.get('MODEL')
        training_frame = current_app.config.get('TRAINING_FRAME')

    if not model:
        print("Debug: Model is not initialized.")
    else:
        print("Debug: Model is initialized.")

    if not training_frame:
        print("Debug: Training frame is not initialized.")
    else:
        print("Debug: Training frame columns:", training_frame.columns)

    return model, training_frame


@main.route('/predict', methods=['POST'])
def predict():
    model, _ = get_model_and_training_frame()

    if model is None:
        return jsonify({'success': False, 'error': "Model is not initialized."}), 500

    try:
        # Collect input data from the form
        data = {
            'Gender': int(request.form['Gender']),
            'Geography': int(request.form['Geography']),
            'IsActiveMember': int(request.form['IsActiveMember']),
            'Age': float(request.form['Age']),
            'CreditScore': float(request.form['CreditScore']),
            'Balance': float(request.form['Balance']),
            'SatisfactionScore': float(request.form['SatisfactionScore']),
            'PointEarned': float(request.form['PointEarned']),
            'Tenure': float(request.form['Tenure']),
            'EstimatedSalary': float(request.form['EstimatedSalary']),
            'NumOfProducts': float(request.form['NumOfProducts']),
            'CardType': int(request.form.get('CardType', 0)),
            'HasCrCard': int(request.form.get('HasCrCard', 0))
        }

        input_data = list(data.values())
        column_names = list(data.keys())
        frame = h2o.H2OFrame([input_data], column_names=column_names)

        # Make prediction
        prediction = model.predict(frame)
        result = float(prediction[0, 0])
        return jsonify({'success': True, 'prediction': result})

    except Exception as e:
        print(f"Error during prediction: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@main.route('/plot', methods=['GET'])
def get_plot():
    model, _ = get_model_and_training_frame()

    if not model:
        return jsonify({'success': False, 'error': "Model is not initialized."}), 500

    try:
        plot_data = plot_variable_importance(model)
        if not plot_data:
            raise ValueError("Failed to generate plot data.")
        return jsonify({'success': True, 'plot_data': plot_data})
    except Exception as e:
        print(f"Error in get_plot: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})


@main.route('/scoring_history_plot', methods=['GET'])
def get_scoring_history_plot():
    model, _ = get_model_and_training_frame()

    if not model:
        return jsonify({'success': False, 'error': "Model is not initialized."}), 500

    try:
        plot_data = plot_scoring_history(model)
        if not plot_data:
            raise ValueError("Failed to generate scoring history plot data.")
        return jsonify({'success': True, 'plot_data': plot_data})
    except Exception as e:
        print(f"Error in get_scoring_history_plot: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})


@main.route('/partial_plot/<feature>', methods=['GET'])
def get_partial_plot(feature):
    model, training_frame = get_model_and_training_frame()

    if not model:
        return jsonify({'success': False, 'error': "Model is not initialized."}), 500

    if not training_frame:
        return jsonify({'success': False, 'error': "Training frame is not initialized."}), 500

    try:
        # Generate the partial plot
        plot_data = model.partial_plot(frame=training_frame, cols=[feature], plot=True, server=True)

        # Encode the plot image as a base64 string
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png')
        plt.close()
        img_buffer.seek(0)

        # Convert to base64
        img_base64 = base64.b64encode(img_buffer.read()).decode('utf-8')

        # Return the base64-encoded image
        return jsonify({'success': True, 'plot_data': img_base64})

    except Exception as e:
        print(f"Error in get_partial_plot: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

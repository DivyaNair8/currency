from flask import Flask, render_template, request
import boto3
import json

# Flask app initialization
app = Flask(__name__)

# AWS clients
lambda_client = boto3.client('lambda', region_name='us-east-1')

# Home Route
@app.route('/')
def home():
    return render_template('index.html')

# Input Route
@app.route('/input', methods=['GET', 'POST'])
def input_currency():
    if request.method == 'POST':
        # Retrieve user input
        base_currency = request.form['base_currency']
        target_currency = request.form['target_currency']
        amount = request.form.get('amount', type=float)

        # Prepare the payload for the Lambda function
        payload = {
            "base_currency": base_currency,
            "target_currency": target_currency,
            "amount": amount
        }

        # Call the Lambda function
        try:
            lambda_response = lambda_client.invoke(
                FunctionName='currency',  # Replace with your actual Lambda function name
                InvocationType='RequestResponse',
                Payload=json.dumps(payload)
            )
            response_payload = json.loads(lambda_response['Payload'].read().decode('utf-8'))

            if lambda_response['StatusCode'] == 200:
                data = json.loads(response_payload['body'])
                if 'converted_amount' in data:
                    converted_amount = data['converted_amount']
                    return render_template(
                        'output.html',
                        converted_amount=converted_amount,
                        base_currency=base_currency,
                        target_currency=target_currency,
                        amount=amount
                    )
                else:
                    error_message = data.get('error', 'An error occurred while processing the conversion.')
                    return render_template('input.html', error=error_message)
            else:
                return render_template('input.html', error="Lambda function error.")
        except Exception as e:
            return render_template('input.html', error=str(e))

    return render_template('input.html')

# Portfolio Route
@app.route('/portfolio')
def portfolio():
    return render_template('portfolio.html')

if __name__ == '__main__':
    app.run(debug=True)

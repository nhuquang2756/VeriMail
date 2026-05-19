"""
Flask Web Application for AI Spam Detector
Main entry point
"""

from flask import Flask, render_template, request, jsonify
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.core import ModelManager
from src.utils import setup_logger

# Initialize Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Setup logger
logger = setup_logger('flask_app')

# Initialize model manager
model_manager = ModelManager()

# Log all requests
@app.before_request
def log_request():
    logger.info(f"{request.method} {request.path} - {request.remote_addr}")

@app.after_request
def log_response(response):
    logger.info(f"{request.method} {request.path} - Status: {response.status_code}")
    return response

@app.route('/')
def index():
    """Render main page"""
    models = model_manager.get_available_models()
    return render_template('index.html', models=models)

@app.route('/api/predict', methods=['POST'])
def predict():
    """API endpoint for single message prediction"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        model_names = data.get('models', [])
        
        logger.info(f"Predict request - Models: {model_names}, Message length: {len(message)}")
        
        if not message:
            logger.warning("Predict request failed: No message provided")
            return jsonify({'error': 'No message provided'}), 400
        
        if not model_names:
            logger.warning("Predict request failed: No models selected")
            return jsonify({'error': 'No models selected'}), 400
        
        results = {}
        for model_name in model_names:
            try:
                prediction = model_manager.predict_single(message, model_name)
                results[model_name] = prediction
                logger.info(f"Predicted with {model_name}: {prediction}")
            except Exception as e:
                logger.error(f"Error with model {model_name}: {e}")
                results[model_name] = f"Error: {str(e)}"
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/predict-batch', methods=['POST'])
def predict_batch():
    """API endpoint for batch prediction from CSV"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        model_names = request.form.getlist('models[]')
        
        if not model_names:
            return jsonify({'error': 'No models selected'}), 400
        
        # Read CSV
        import pandas as pd
        from io import StringIO
        
        csv_data = file.read().decode('utf-8')
        df = pd.read_csv(StringIO(csv_data), delimiter='|')
        
        if 'Message' not in df.columns:
            return jsonify({'error': 'CSV must have a "Message" column'}), 400
        
        results = {}
        for model_name in model_names:
            try:
                predictions = model_manager.predict_batch(df['Message'], model_name)
                results[model_name] = predictions
            except Exception as e:
                logger.error(f"Error with model {model_name}: {e}")
                results[model_name] = [f"Error: {str(e)}"] * len(df)
        
        # Prepare response data
        output_data = df[['Message']].copy()
        for model_name in model_names:
            output_data[model_name] = results[model_name]
        
        return jsonify({
            'success': True,
            'data': output_data.to_dict('records'),
            'columns': list(output_data.columns)
        })
        
    except Exception as e:
        logger.error(f"Batch prediction error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/models', methods=['GET'])
def get_models():
    """Get list of available models"""
    try:
        models = model_manager.get_available_models()
        return jsonify({
            'success': True,
            'models': models
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Email Monitor endpoints
from src.services import EmailService

# Store email service in session (in production, use proper session management)
email_services = {}

@app.route('/api/gmail/connect', methods=['POST'])
def gmail_connect():
    """Connect to Gmail"""
    try:
        data = request.get_json()
        email = data.get('email', '')
        password = data.get('password', '')
        
        logger.info(f"Gmail connect attempt for: {email}")
        
        if not email or not password:
            logger.warning(f"Gmail connect failed: Missing credentials for {email}")
            return jsonify({'error': 'Email and password required'}), 400
        
        # Create email service
        email_service = EmailService()
        success, msg = email_service.connect(email, password)
        
        if success:
            # Store service (use session ID as key)
            session_id = email  # In production, use proper session management
            email_services[session_id] = email_service
            
            logger.info(f"Gmail connected successfully: {email}")
            return jsonify({
                'success': True,
                'message': msg,
                'session_id': session_id
            })
        else:
            logger.error(f"Gmail connect failed for {email}: {msg}")
            return jsonify({'error': msg}), 401
            
    except Exception as e:
        logger.error(f"Gmail connection error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/gmail/fetch', methods=['POST'])
def gmail_fetch():
    """Fetch emails from Gmail"""
    try:
        data = request.get_json()
        session_id = data.get('session_id', '')
        model_name = data.get('model', 'Voting Classifier')
        limit = data.get('limit', 20)
        
        logger.info(f"Fetch emails request - Session: {session_id}, Model: {model_name}, Limit: {limit}")
        
        if session_id not in email_services:
            logger.warning(f"Fetch failed: Not connected for session {session_id}")
            return jsonify({'error': 'Not connected. Please login first.'}), 401
        
        email_service = email_services[session_id]
        
        # Fetch emails
        emails, msg = email_service.fetch_recent_emails(limit=limit)
        
        if emails is None:
            logger.error(f"Fetch emails failed: {msg}")
            return jsonify({'error': msg}), 500
        
        logger.info(f"Fetched {len(emails)} emails successfully")
        
        # Analyze each email
        results = []
        spam_count = 0
        for email_data in emails:
            try:
                prediction = model_manager.predict_single(email_data['full_body'], model_name)
                if prediction == 'Spam':
                    spam_count += 1
                results.append({
                    'from': email_data['from'],
                    'subject': email_data['subject'],
                    'date': email_data['date'],
                    'body_preview': email_data['body_preview'],
                    'prediction': prediction
                })
            except Exception as e:
                logger.error(f"Error analyzing email: {e}")
                results.append({
                    'from': email_data['from'],
                    'subject': email_data['subject'],
                    'date': email_data['date'],
                    'body_preview': email_data['body_preview'],
                    'prediction': 'Error'
                })
        
        logger.info(f"Analysis complete - Total: {len(results)}, Spam: {spam_count}, Ham: {len(results) - spam_count}")
        
        return jsonify({
            'success': True,
            'emails': results,
            'count': len(results)
        })
        
    except Exception as e:
        logger.error(f"Email fetch error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/gmail/disconnect', methods=['POST'])
def gmail_disconnect():
    """Disconnect from Gmail"""
    try:
        data = request.get_json()
        session_id = data.get('session_id', '')
        
        if session_id in email_services:
            email_services[session_id].disconnect()
            del email_services[session_id]
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':

    print("=" * 70)
    print("🛡️  AI SPAM DETECTOR - Flask Version")
    print("=" * 70)
    print(f"📊 Available models: {len(model_manager.get_available_models())}")
    print(f"🌐 Starting server...")
    print("=" * 70)
    
    app.run(debug=True, host='0.0.0.0', port=5000)

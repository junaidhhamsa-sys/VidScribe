from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import logging
from pathlib import Path
import json

from pipeline_gemini import VideoSummarizerPipeline
from utils.helpers import allowed_file, get_unique_filename
import config

# Setup logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = config.MAX_FILE_SIZE
app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = config.OUTPUT_FOLDER

# Initialize pipeline
pipeline = VideoSummarizerPipeline()

# Store processing results (in-memory, use Redis in production)
processing_results = {}


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_video():
    """Handle video upload and start processing"""
    
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400
    
    file = request.files['video']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename, config.ALLOWED_EXTENSIONS):
        return jsonify({'error': f'Invalid file type. Allowed: {", ".join(config.ALLOWED_EXTENSIONS)}'}), 400
    
    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        unique_filename = get_unique_filename(filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        
        logger.info(f"Video uploaded: {filepath}")
        
        # Get output name from filename
        output_name = Path(unique_filename).stem
        
        # Start processing (synchronous for now, use Celery for async in production)
        logger.info(f"Starting processing for: {unique_filename}")
        results = pipeline.process_video(filepath, output_name)
        
        # Store results
        processing_results[output_name] = results
        
        if results['status'] == 'complete':
            # Prepare response
            response = {
                'status': 'success',
                'output_name': output_name,
                'summary': results['summary'],
                'keyframe_count': results['keyframe_count'],
                'language': results['language'],
                'slides_count': len(results['slides']),
                'ppt_filename': Path(results['ppt_path']).name
            }
            
            logger.info(f"Processing complete for: {unique_filename}")
            return jsonify(response)
        else:
            return jsonify({
                'status': 'error',
                'error': results.get('error', 'Unknown error occurred')
            }), 500
            
    except Exception as e:
        logger.error(f"Error processing video: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/download/<output_name>')
def download_ppt(output_name):
    """Download generated PowerPoint"""
    
    if output_name not in processing_results:
        return jsonify({'error': 'Results not found'}), 404
    
    results = processing_results[output_name]
    
    if results['status'] != 'complete':
        return jsonify({'error': 'Processing not complete'}), 400
    
    ppt_path = results['ppt_path']
    
    if not os.path.exists(ppt_path):
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(
        ppt_path,
        as_attachment=True,
        download_name=f"{output_name}_summary.pptx",
        mimetype='application/vnd.openxmlformats-officedocument.presentationml.presentation'
    )


@app.route('/results/<output_name>')
def get_results(output_name):
    """Get processing results"""
    
    if output_name not in processing_results:
        return jsonify({'error': 'Results not found'}), 404
    
    results = processing_results[output_name]
    
    # Remove large data for API response
    response = {
        'status': results['status'],
        'summary': results.get('summary'),
        'keyframe_count': results.get('keyframe_count'),
        'language': results.get('language'),
        'slides_count': len(results.get('slides', [])),
        'error': results.get('error')
    }
    
    return jsonify(response)


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error"""
    max_mb = config.MAX_FILE_SIZE / (1024 * 1024)
    return jsonify({'error': f'File size exceeds limit of {max_mb}MB'}), 413


if __name__ == '__main__':
    # Ensure directories exist
    config.UPLOAD_FOLDER.mkdir(exist_ok=True)
    config.OUTPUT_FOLDER.mkdir(exist_ok=True)
    config.TEMP_FOLDER.mkdir(exist_ok=True)
    
    # Run app on port 5001 (5000 is often used by macOS AirPlay)
    app.run(debug=True, host='0.0.0.0', port=5001)

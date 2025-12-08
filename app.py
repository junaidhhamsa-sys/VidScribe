"""Flask application for video summarization"""

from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import logging
from pathlib import Path
import threading

from pipeline import VideoPipeline
from utils import VideoValidator, FileHandler, get_unique_filename, setup_logger
from generators import get_available_templates
import config

# Setup logging
setup_logger()
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = config.MAX_FILE_SIZE
app.config['SECRET_KEY'] = config.FLASK_SECRET_KEY

# Initialize components
validator = VideoValidator()
file_handler = FileHandler()

# Store processing results (in-memory, use Redis in production)
processing_status = {}
processing_results = {}


@app.route('/')
def index():
    """Main page"""
    templates = get_available_templates()
    return render_template('index.html', templates=templates, config=config)


@app.route('/upload', methods=['POST'])
def upload_video():
    """Handle video upload"""
    
    logger.info("Upload request received")
    
    # Check if file exists
    if 'video' not in request.files:
        return jsonify({'error': config.ERROR_MESSAGES['no_file']}), 400
    
    file = request.files['video']
    
    if file.filename == '':
        return jsonify({'error': config.ERROR_MESSAGES['no_file']}), 400
    
    # Get form parameters
    output_format = request.form.get('output_format', 'ppt')
    template = request.form.get('template', config.DEFAULT_TEMPLATE)
    
    logger.info(f"Upload details: format={output_format}, template={template}")
    
    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        unique_filename = get_unique_filename(filename)
        filepath = file_handler.save_upload(file, unique_filename)
        
        logger.info(f"File saved: {filepath}")
        
        # Validate video
        is_valid, error = validator.validate_file(filepath)
        if not is_valid:
            file_handler.delete_file(filepath)
            return jsonify({'error': error}), 400
        
        # Get video info
        video_info = validator.get_video_info(filepath)
        
        # Generate processing ID
        output_name = Path(unique_filename).stem
        
        # Initialize processing status
        processing_status[output_name] = {
            'status': 'queued',
            'progress': 0,
            'message': 'Video uploaded successfully'
        }
        
        # Start processing in background thread
        thread = threading.Thread(
            target=process_video_background,
            args=(filepath, output_format, template, output_name)
        )
        thread.daemon = True
        thread.start()
        
        logger.info(f"Processing started for: {output_name}")
        
        return jsonify({
            'status': 'success',
            'output_name': output_name,
            'video_info': {
                'duration': video_info['duration_formatted'],
                'resolution': video_info['resolution'],
                'size': f"{video_info['file_size_mb']:.2f} MB"
            },
            'message': 'Video uploaded and processing started'
        })
        
    except Exception as e:
        logger.error(f"Upload error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


def process_video_background(video_path: str, output_format: str, 
                            template: str, output_name: str):
    """Process video in background thread"""
    
    try:
        # Update status
        processing_status[output_name] = {
            'status': 'processing',
            'progress': 10,
            'message': 'Initializing pipeline...'
        }
        
        # Initialize pipeline
        pipeline = VideoPipeline()
        
        # Process video
        results = pipeline.process_video(
            video_path=video_path,
            output_format=output_format,
            ppt_template=template if output_format == 'ppt' else None,
            output_name=output_name
        )
        
        # Store results
        processing_results[output_name] = results
        
        if results['status'] == 'complete':
            processing_status[output_name] = {
                'status': 'complete',
                'progress': 100,
                'message': 'Processing complete!'
            }
        else:
            processing_status[output_name] = {
                'status': 'error',
                'progress': 0,
                'message': results.get('error', 'Unknown error')
            }
            
    except Exception as e:
        logger.error(f"Background processing error: {e}", exc_info=True)
        processing_status[output_name] = {
            'status': 'error',
            'progress': 0,
            'message': str(e)
        }


@app.route('/status/<output_name>')
def get_status(output_name):
    """Get processing status"""
    
    if output_name not in processing_status:
        return jsonify({'error': 'Not found'}), 404
    
    status = processing_status[output_name]
    
    # Add results if complete
    if status['status'] == 'complete' and output_name in processing_results:
        results = processing_results[output_name]
        status['results'] = {
            'title': results.get('title', 'Video Summary'),
            'summary': results.get('summary', ''),
            'slides_count': len(results.get('slides', [])),
            'language': results.get('language', 'unknown'),
            'processing_time': results.get('processing_time', 0),
            'output_type': results.get('output_type'),
            'output_path': Path(results.get('output_path', '')).name if results.get('output_path') else None
        }
    
    return jsonify(status)


@app.route('/download/<output_name>')
def download_file(output_name):
    """Download generated file"""
    
    if output_name not in processing_results:
        return jsonify({'error': 'Results not found'}), 404
    
    results = processing_results[output_name]
    
    if results['status'] != 'complete':
        return jsonify({'error': 'Processing not complete'}), 400
    
    output_path = results.get('output_path')
    
    if not output_path or not os.path.exists(output_path):
        return jsonify({'error': 'File not found'}), 404
    
    # Determine mimetype
    output_type = results.get('output_type', 'ppt')
    if output_type == 'ppt':
        mimetype = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        ext = '.pptx'
    elif output_type == 'pdf':
        mimetype = 'application/pdf'
        ext = '.pdf'
    else:
        return jsonify({'error': 'Invalid output type'}), 400
    
    filename = f"{output_name}_summary{ext}"
    
    return send_file(
        output_path,
        as_attachment=True,
        download_name=filename,
        mimetype=mimetype
    )


@app.route('/templates')
def list_templates():
    """Get available templates"""
    templates = get_available_templates()
    return jsonify({'templates': templates})


@app.route('/cleanup', methods=['POST'])
def cleanup():
    """Cleanup old files"""
    try:
        file_handler.cleanup_old_outputs(hours=config.KEEP_OUTPUTS_HOURS)
        return jsonify({'status': 'success', 'message': 'Cleanup complete'})
    except Exception as e:
        logger.error(f"Cleanup error: {e}")
        return jsonify({'error': str(e)}), 500


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error"""
    max_gb = config.MAX_FILE_SIZE / (1024 ** 3)
    return jsonify({'error': f'File size exceeds {max_gb:.1f}GB limit'}), 413


@app.errorhandler(500)
def internal_error(error):
    """Handle internal server error"""
    logger.error(f"Internal error: {error}")
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Ensure directories exist
    file_handler.ensure_directories()
    
    # Run app
    logger.info("="*70)
    logger.info("🚀 Starting VidScribe Application")
    logger.info("="*70)
    logger.info(f"Host: {config.FLASK_HOST}")
    logger.info(f"Port: {config.FLASK_PORT}")
    logger.info(f"Debug: {config.FLASK_DEBUG}")
    logger.info("="*70)
    
    app.run(
        debug=config.FLASK_DEBUG,
        host=config.FLASK_HOST,
        port=config.FLASK_PORT
    )
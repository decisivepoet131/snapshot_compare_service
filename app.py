from flask import Flask
from routes.snapshot_compare import snapshot_compare_bp
from utils.logger import logger, log_service_start_stop
import atexit
import os

app = Flask(__name__)

# Register blueprints
app.register_blueprint(snapshot_compare_bp)

# Log service start
if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
    log_service_start_stop("Service start...")

def on_exit():
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        # Log service stop
        log_service_start_stop("Service stop...")

# Register the exit handler
atexit.register(on_exit)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Default to 5000 if not set
    app.run(debug=True, port=port)
from flask import Blueprint, request, jsonify
import os
import time
import gzip
import shutil
from werkzeug.utils import secure_filename
from services.item_attributes_snapshot_compare import item_attributes_compare
from services.item_prices_snapshot_compare import item_price_compare
from services.link_groups_snapshot_compare import link_groups_compare
from utils.logger import log_entry_exit, log_response, logger, save_result_and_log

snapshot_compare_bp = Blueprint('snapshot_compare', __name__)

def decompress_gz(file_path, output_path):
    with gzip.open(file_path, 'rb') as f_in:
        with open(output_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

@snapshot_compare_bp.route('/api/snapshot-compare/item-attributes', methods=['POST'])
@snapshot_compare_bp.route('/api/snapshot-compare/item-prices', methods=['POST'])
@snapshot_compare_bp.route('/api/snapshot-compare/link-groups', methods=['POST'])
@log_entry_exit
def snapshot_compare():
    try:
        # Ensure exactly two files are provided
        files = {k.lower(): v for k, v in request.files.items()}
        if 'file1' not in files or 'file2' not in files:
            logger.warning("Exactly two files are required")
            return log_response(jsonify({"error": "Exactly two files are required"}), 400)

        file1 = files['file1']
        file2 = files['file2']

        ignored_attributes = request.form.get('ignored_attributes', '').split(',')
        if ignored_attributes == ['']:
            ignored_attributes = []

        # Secure filenames
        filename1 = secure_filename(file1.filename)
        filename2 = secure_filename(file2.filename)

        # Save files to a temporary location
        script_dir = os.path.dirname(os.path.abspath(__file__))
        temp_dir = os.path.join(script_dir, "temp")
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        file1_path = os.path.join(temp_dir, filename1)
        file2_path = os.path.join(temp_dir, filename2)
        file1.save(file1_path)
        file2.save(file2_path)

        logger.info(f"Received files: {filename1}, {filename2}")

        # Decompress the files
        decompressed_file1_path = os.path.join(temp_dir, f"decompressed_{filename1}")
        decompressed_file2_path = os.path.join(temp_dir, f"decompressed_{filename2}")
        decompress_gz(file1_path, decompressed_file1_path)
        decompress_gz(file2_path, decompressed_file2_path)

        # Determine which comparison to run based on the endpoint
        if request.path.endswith('item-attributes'):
            result = item_attributes_compare(decompressed_file1_path, decompressed_file2_path, ignored_attributes)
        elif request.path.endswith('item-prices'):
            result = item_price_compare(decompressed_file1_path, decompressed_file2_path, ignored_attributes)
        elif request.path.endswith('link-groups'):
            result= link_groups_compare(decompressed_file1_path, decompressed_file2_path, ignored_attributes)
        else:
            logger.error("Invalid endpoint")
            return log_response(jsonify({"error": "Invalid endpoint"}), 400)

        if os.environ.get('LOG_RESULTS') == 'TRUE':
            save_result_and_log(result, request.path)

        # Clean up temporary files
        os.remove(file1_path)
        os.remove(file2_path)
        os.remove(decompressed_file1_path)
        os.remove(decompressed_file2_path)

        return log_response(jsonify(result), 200)
    except Exception as e:
        logger.exception("Exception occurred during snapshot comparison")
        return log_response(jsonify({"error": "Internal Server Error"}), 500)
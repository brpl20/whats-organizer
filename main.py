import os
import sys
import json
import uuid
import argparse
from typing import List, Optional, Dict, Any
from process_convo import process_convo_offline
from connection_handlers import cleanup_files

def main():
    parser = argparse.ArgumentParser(description='Process WhatsApp conversation zip files offline')
    parser.add_argument('zip_file', help='Path to the WhatsApp conversation zip file')
    parser.add_argument('--output', '-o', help='Output directory for processed files (default: current directory)')
    parser.add_argument('--keep-temp', '-k', action='store_true', help='Keep temporary files after processing')
    parser.add_argument('--no-pdf', '-n', action='store_true', help='Skip PDF generation')
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.zip_file):
        print(f"Error: File '{args.zip_file}' not found.")
        return 1
    
    # Set output directory
    output_dir = args.output if args.output else os.getcwd()
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Generate a unique folder name based on the zip file name
    unique_folder = str(uuid.uuid4())
    
    # Process the conversation
    print("Processing WhatsApp conversation...")
    result = process_convo_offline(args.zip_file, unique_folder, print_status)
    
    if isinstance(result, list) and result and isinstance(result[0], dict) and "ERRO" in result[0]:
        print(f"Error: {result[0]['ERRO']}")
        return 1
    
    # Save the result as JSON
    output_json = os.path.join(output_dir, 'conversation.json')
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"Processed conversation saved to {output_json}")
    
    # Clean up temporary files if not keeping them
    if not args.keep_temp:
        cleanup_files(unique_folder)
    
    return 0

def print_status(message: str):
    """Simple status printer for offline mode"""
    print(f"Status: {message}")

if __name__ == "__main__":
    sys.exit(main())

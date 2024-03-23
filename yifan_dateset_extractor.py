#!/usr/bin/env python3
import json
import requests
import logging


# Setup basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_data(json_data):
    """Extracts prev_hash and spent_by from the JSON data."""
    # Check if 'inputs' and 'outputs' are in the JSON data and extract accordingly
    prev_hashes = [inp['prev_hash'] for inp in json_data.get('inputs', []) if 'prev_hash' in inp]
    spent_by = [out['spent_by'] for out in json_data.get('outputs', []) if 'spent_by' in out]
    return prev_hashes, spent_by

def read_json_file(filepath):
    """Reads a JSON file and returns its content."""
    try:
        with open(filepath, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"The file {filepath} was not found.")
    except json.JSONDecodeError:
        print(f"Error decoding JSON from the file {filepath}.")
    return None

def fetch_transaction_data(tx_hash):
    """Fetches transaction data from the BlockCypher API for the given transaction hash."""
    url = f"https://api.blockcypher.com/v1/btc/main/txs/{tx_hash}"
    try:
        logging.info(f"Fetching data for hash: {tx_hash}")
        logging.info(f"URL: {url}")
        response = requests.get(url)
        if response.status_code == 200:
            logging.info(f"Successfully fetched data for hash: {tx_hash}")
            return response.json()
        else:
            logging.warning(f"Failed to fetch data for hash: {tx_hash} with status code: {response.status_code}")
    except requests.RequestException as e:
        logging.error(f"Request exception occurred: {e}")
    return None

            
def append_to_json_file(file_path, data):
    """Appends data to a JSON array in a file."""
    try:
        with open(file_path, 'r+') as file:
            file_data = json.load(file)
            file_data.append(data)
            file.seek(0)
            json.dump(file_data, file, indent=4)
            logging.info(f"Successfully appended data to {file_path}")
    except FileNotFoundError:
        with open(file_path, 'w') as file:
            json.dump([data], file, indent=4)
            logging.info(f"Created {file_path} and appended data")
    except json.JSONDecodeError:
        logging.error(f"File {file_path} contains invalid JSON.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        
def initial_json_data(json_content):
    json_content = read_json_file("1_transaction.json")
    block_hash = json_content.get("block_hash", "Not available")
    logging.info(f"Block hash: {block_hash}")  # Log the block hash here
    prev_hashes = [inp['prev_hash'] for inp in json_content.get('inputs', []) if 'prev_hash' in inp]
    spent_by_hashes = [out['spent_by'] for out in json_content.get('outputs', []) if 'spent_by' in out]

def update_transactions(initial_json_data):
    """Updates the transactions file with data fetched using the provided hashes."""
    
    to_process_hashes = set()  # A set to keep track of hashes to process
    
    # Start with extracting hashes from the initial transaction
    prev_hashes, spent_by_hashes = extract_data(initial_json_data)
    
    # log the initial hashes
    logging.info(f"Initial prev_hashes: {prev_hashes}")
    logging.info(f"Initial spent_by_hashes: {spent_by_hashes}")
    
    to_process_hashes.update(prev_hashes + spent_by_hashes)
    # log current set
    logging.info(f"Current set of hashes to process: {to_process_hashes}")
    
    processed_hashes = set()  # A set to keep track of already processed hashes

    while to_process_hashes:
        current_hash = to_process_hashes.pop()  # Get a hash to process
        if current_hash in processed_hashes:
            continue  # Skip if this hash has already been processed

        transaction = fetch_transaction_data(current_hash)
        if transaction:
            append_to_json_file("previous_transactions_1.json", transaction)

            # Extract prev_hash and spent_by hashes from the current transaction and add them for processing
            prev_hashes, spent_by_hashes = extract_data(transaction)
            to_process_hashes.update(prev_hashes + spent_by_hashes)

        processed_hashes.add(current_hash)  # Mark the current hash as processed

    logging.info("Finished processing all transactions.")
            
if __name__ == "__main__":
        json_content = read_json_file("1_transaction.json")
        update_transactions(json_content)

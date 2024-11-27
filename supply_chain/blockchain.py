import hashlib
import json
import uuid
from .models import StoreBlock
from datetime import datetime
from .models import Block
from time import time

# class Blockchain:
#     def _init_(self):
#         self.chain = []

#     def add_block(self, transaction_data):
#         previous_hash = self.chain[-1]['block_hash'] if self.chain else '0'
#         block = {
#             'previous_hash': previous_hash,
#             'transaction_details': transaction_data,
#             'timestamp': str(datetime.now()),
#         }
#         block['block_hash'] = self.compute_hash(block)
#         self.chain.append(block)
#         return block

#     def compute_hash(self, block):
#         block_string = json.dumps(block, sort_keys=True).encode()
#         return hashlib.sha256(block_string).hexdigest()

#     def get_chain(self):
#         return self.chain
    
# class Blockchain:
#     def __init__(self):
#         self.chain = []
#         self.current_transactions = []
#         self.create_block(previous_hash='1', proof=100)  # Create genesis block

#     def create_block(self, proof, previous_hash=None):
#         block = Block(
#             index=len(self.chain) + 1,
#             timestamp=time(),
#             transactions=self.current_transactions,
#             previous_hash=previous_hash or self.chain[-1].hash
#         )
#         self.current_transactions = []  # Reset the current transactions
#         self.chain.append(block)
#         return block

#     def add_transaction(self, sender, recipient, amount, crop_id):
#         self.current_transactions.append({
#             'sender': sender,
#             'recipient': recipient,
#             'amount': amount,
#             'crop_id': crop_id  # Include crop_id for tracing
#         })
#         return self.last_block.index + 1

#     @property
#     def last_block(self):
#         return self.chain[-1]

#     def proof_of_work(self, last_proof):
#         proof = 0
#         while not self.valid_proof(last_proof, proof):
#             proof += 1
#         return proof

#     @staticmethod
#     def valid_proof(last_proof, proof):
#         guess = f'{last_proof}{proof}'.encode()
#         guess_hash = hashlib.sha256(guess).hexdigest()
#         return guess_hash[:4] == "0000"  # Adjust the number of leading zeros for difficulty

#     def validate_chain(self):
#         for i in range(1, len(self.chain)):
#             current = self.chain[i]
#             previous = self.chain[i - 1]

#             # Check if the hash of the block is correct
#             if current.hash != current.calculate_hash():
#                 return False

#             # Check if the previous block's hash is correct
#             if current.previous_hash != previous.hash:
#                 return False

#         return True

#     def trace_crop(self, crop_id):
#         # This function could be customized to trace crop details
#         for block in self.chain:
#             for transaction in block.transactions:
#                 if transaction.get('crop_id') == crop_id:
#                     return block
#         return None
    
#     def create_block_with_proof(self):
#         last_block = self.last_block
#         last_proof = last_block.index  # You might want to change this to use the last proof
#         proof = self.proof_of_work(last_proof)

#         # Create a new block with the proof
#         previous_hash = last_block.hash
#         block = self.create_block(proof, previous_hash)
#         return block

import hashlib
import json
import uuid
from datetime import datetime
from time import time

class Block:
    def __init__(self, index, timestamp, transactions, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()  # Calculate hash when block is created

    def calculate_hash(self):
        # Create a unique hash for the block based on its attributes
        print(f"Calculating hash for block {self.index}")
        block_string = json.dumps({
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': self.transactions,
            'previous_hash': self.previous_hash
        }, sort_keys=True).encode()
        hash_result = hashlib.sha256(block_string).hexdigest()
        print(f"Hash for block {self.index}: {hash_result}")
        return hash_result


class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.load_chain()  # Load existing blocks from the StoreBlock model

        if not self.chain:
            # If chain is empty, create genesis block
            self.create_block(previous_hash='1', proof=100)

    def create_block(self, proof, previous_hash=None):
        block = Block(
            index=len(self.chain) + 1,
            timestamp=time(),
            transactions=self.current_transactions,
            previous_hash=previous_hash or self.chain[-1].hash
        )

        store_block = StoreBlock(
            index=block.index,
            timestamp=block.timestamp,
            transactions=block.transactions,
            previous_hash=previous_hash or '0',
            hash=block.hash
        )
        store_block.save()
        self.current_transactions = []  # Reset the current transactions
        self.chain.append(block)
        return block

    def load_chain(self):
        # Load existing blocks from the StoreBlock model and append to the chain
        stored_blocks = StoreBlock.objects.all().order_by('index')
        for stored_block in stored_blocks:
            block = Block(
                index=stored_block.index,
                timestamp=stored_block.timestamp,
                transactions=stored_block.transactions,
                previous_hash=stored_block.previous_hash
            )
            self.chain.append(block)

    def add_transaction(self, sender, recipient, amount, crop_id):
        transaction_id = str(uuid.uuid4())  # Generate a unique ID for the transaction
        timestamp = datetime.now().isoformat()  # Get the current timestamp

        self.current_transactions.append({
            'id': transaction_id,
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
            'crop_id': crop_id,
            'timestamp': timestamp  # Include timestamp
        })
        return self.last_block.index + 1

    @property
    def last_block(self):
        return self.chain[-1]

    def proof_of_work(self, last_proof):
        proof = 0
        while not self.valid_proof(last_proof, proof):
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"  # Adjust the number of leading zeros for difficulty

    def validate_chain(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            # Check if the hash of the block is correct
            if current.hash != current.calculate_hash():
                return False

            # Check if the previous block's hash is correct
            if current.previous_hash != previous.hash:
                return False

        return True

    def trace_crop(self, crop_id):
        for block in self.chain:
            for transaction in block.transactions:
                if transaction.get('crop_id') == crop_id:
                    return block
        return None

    def mine_block(self):
        last_block = self.last_block
        last_proof = last_block.index  # Adjust if you want to use last proof instead
        proof = self.proof_of_work(last_proof)

        # Create a new block
        previous_hash = last_block.hash  # Ensure you're accessing the hash
        block = self.create_block(proof, previous_hash)
        return block
    
    def calculate_hash(self):
        # Create a unique hash for the block based on its attributes
        print(f"Calculating hash for block {self.index}")
        block_string = json.dumps({
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': self.transactions,
            'previous_hash': self.previous_hash
        }, sort_keys=True).encode()
        hash_result = hashlib.sha256(block_string).hexdigest()
        print(f"Hash for block {self.index}: {hash_result}")
        return hash_result

    def get_blockchain_data(self):
        # Convert each block in the chain to a dictionary format
        blockchain_data = []
        for block in self.chain:
            blockchain_data.append({
                'index': block.index,
                'timestamp': block.timestamp,
                'transactions': block.transactions,
                'previous_hash': block.previous_hash,
                'hash': block.hash
            })
        return blockchain_data
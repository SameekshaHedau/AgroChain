from django.db import models
from django.conf import settings 
from django.contrib.auth.models import AbstractUser
import hashlib
import json
from time import time


# Create your models here.

from django.contrib.auth.models import AbstractUser

# class CustomUser(AbstractUser):
#     ROLE_CHOICES = [
#         ('FARMER', 'Farmer'),
#         ('DISTRIBUTOR', 'Distributor'),
#         ('CONSUMER', 'Consumer'),
#     ]
#     role = models.CharField(max_length=100, choices=ROLE_CHOICES)

class CustomUser(AbstractUser):
    
    ROLE_CHOICES = [
        ('FARMER', 'Farmer'),
        ('DISTRIBUTOR', 'Distributor'),
        ('CONSUMER', 'Consumer'),
    ]
    role = models.CharField(max_length=100, choices=ROLE_CHOICES)
    


    # New fields for profile picture and token balance
    profile_picture = models.ImageField(upload_to='profile_pictures/', default='default_profile.png', blank=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=100000)  # 2 decimal points for tokens

    def __str__(self):
        return self.username
    
# class Crop(models.Model):
#     name = models.CharField(max_length=100)
#     quantity = models.FloatField()
#     price = models.FloatField()
#     current_owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='owned_crops')
#     status = models.CharField(max_length=20, choices=[('listed', 'Listed'), ('sold', 'Sold')])
#     current_stage = models.CharField(max_length=100, default='Listed by Farmer')
#     transaction_hash = models.CharField(max_length=64, blank=True, null=True)
#     allowed_users = models.ManyToManyField(CustomUser, related_name='allowed_crops', blank=True)
#     visibility = models.CharField(max_length=10, choices=[('public', 'Public'), ('private', 'Private')], default='public')
    
#     def __str__(self):
#         return f"{self.name} - {self.quantity} kg - {self.current_stage}"

class Crop(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.FloatField()
    price = models.FloatField()  # Price for public visibility
    specific_user_price = models.FloatField(blank=True, null=True)  # Price for specific users
    current_owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_crops')
    
    status = models.CharField(max_length=20, choices=[('listed', 'Listed'), ('sold', 'Sold')])
    current_stage = models.CharField(max_length=100, default='Listed by Farmer')
    transaction_hash = models.CharField(max_length=64, blank=True, null=True)
    allowed_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='allowed_crops', blank=True)
    visibility = models.CharField(max_length=10, choices=[('public', 'Public'), ('private', 'Private')], default='public')

    # Token-related fields
    price_in_tokens = models.FloatField(blank=True, null=True, help_text='Optional: Price in tokens for the crop.')
    token_currency_enabled = models.BooleanField(default=False, help_text='Is token currency enabled for this crop?')

    def __str__(self):
        return f"{self.name} - {self.quantity} kg - {self.current_stage}"

    def is_token_enabled(self):
        return self.token_currency_enabled
    
# class Crop(models.Model):
#     name = models.CharField(max_length=100)
#     quantity = models.FloatField()
#     price = models.FloatField()
#     current_owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     current_stage = models.CharField(max_length=50, default="Listed by Farmer")

#     def __str__(self):
#         return f"{self.name} - {self.quantity} kg - {self.current_stage}"

# class Transaction(models.Model):
#     buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='buyer')
#     seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='seller')
#     crop = models.ForeignKey(Crop, on_delete=models.CASCADE)
#     quantity = models.FloatField()
#     price = models.FloatField()
#     transaction_hash = models.CharField(max_length=255) 
#     timestamp = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Transaction: {self.seller} -> {self.buyer} | {self.crop.name}"


class Transaction(models.Model):
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sold_transactions', on_delete=models.CASCADE)
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='purchased_transactions', on_delete=models.CASCADE)  # Correct field name
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_hash = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

class Block(models.Model):
    index = models.IntegerField(null=True)
    previous_hash = models.CharField(max_length=64)
    timestamp = models.FloatField(default=time)
    transactions = models.JSONField(default=list)  # Stores transactions as a JSON list
    proof = models.IntegerField()

    def __str__(self):
        return f"Block {self.index}"

    @classmethod
    def create_block(cls, index, previous_hash, transactions, proof):
        """Creates a new block and saves it to the database."""
        block = cls(
            index=index,
            previous_hash=previous_hash,
            timestamp=time.time(), 
            transactions=json.dumps(transactions),  # Convert transactions to JSON string for storage
            proof=proof
        )
        block.save()
        return block

    @classmethod
    def calculate_hash(cls, block):
        """Calculates the hash of a block."""
        block_string = json.dumps(block.__dict__, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

# class Block(models.Model):

class PurchasedCrop(models.Model):
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sold_crops', on_delete=models.CASCADE)
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='purchased_crops', on_delete=models.CASCADE)
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_hash = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Purchased: {self.crop.name} by {self.buyer.username} from {self.seller.username} | Quantity: {self.quantity} | Price: {self.price}"
    

class StoreBlock(models.Model):
    index = models.IntegerField(null=True)
    timestamp = models.FloatField(default=time)
    transactions = models.JSONField(default=list)
    previous_hash = models.CharField(max_length=64)
    hash = models.CharField(max_length=64)

    def __str__(self):
        return f"Block {self.index} - Hash: {self.hash}"
    
    

class Token(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tokens')
    balance = models.FloatField(default=0.0, help_text='The number of tokens the user owns.')
    
    def __str__(self):
        return f"{self.owner.username} - {self.balance} tokens"

    def transfer(self, recipient, amount):
        """
        Transfer tokens from one user to another.
        
        :param recipient: The user receiving the tokens.
        :param amount: The number of tokens to transfer.
        :raises: ValueError if the owner has insufficient balance or invalid transfer amount.
        """
        if amount <= 0:
            raise ValueError("Transfer amount must be positive.")
        if self.balance < amount:
            raise ValueError("Insufficient balance to complete the transfer.")
        
        # Deduct tokens from the current owner's balance
        self.balance -= amount
        self.save()

        # Add tokens to the recipient's balance
        recipient_token, created = Token.objects.get_or_create(owner=recipient)
        recipient_token.balance += amount
        recipient_token.save()

    def has_sufficient_balance(self, amount):
        """
        Check if the owner has enough balance to cover a transaction.
        
        :param amount: The number of tokens required.
        :return: True if the balance is sufficient, False otherwise.
        """
        return self.balance >= amount
    
class UserSpecificCrop(models.Model):
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name='user_specifics')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    specific_price = models.FloatField(null=True, blank=True)  # Price specific to this user
    allowed = models.BooleanField(default=False)  # Whether this user can see the crop

    def __str__(self):
        return f"{self.user.username} - {self.crop.name} - {self.specific_price}"
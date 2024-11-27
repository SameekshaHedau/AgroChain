
from .models import Crop, Transaction, PurchasedCrop,Token, UserSpecificCrop
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.http import JsonResponse
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Crop, Transaction, StoreBlock,CustomUser
from .blockchain import Blockchain, Block
from django.contrib.auth.models import User
from django.contrib.auth import logout
from .forms import CropForm
from decimal import Decimal

# Create your views here.
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm, CropPriceUpdateForm

from django.shortcuts import render, redirect
from .models import Crop
from .blockchain import Blockchain  # Import your blockchain class

blockchain = Blockchain()  # Initialize your blockchain




def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # form.save()
            # return redirect('login')  # Change this to your login URL name
            user=form.save()
            user.role = request.POST.get('role')  # Ensure you have a way to capture the role in your form
            user.save()

            # Automatically log the user in after registration
            login(request, user)
            return redirect('dashboard')
        
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

# In supply_chain/views.py

def home(request):
    return render(request, 'home.html')  # Assuming you have a template named 'home.html'


def transaction_history(request):
    transactions = Transaction.objects.filter(buyer=request.user) | Transaction.objects.filter(seller=request.user)
    return render(request, 'transaction_history.html', {'transactions': transactions})

@login_required
def dashboard(request):
    user = request.user
    print("Dashboard view called")
    user_role = getattr(request.user, 'role', None)
    print(f"User Role: {user_role}")
    # print(f"User: {user.username}, Role: {user.role}")  # Debugging line
    all_user_specific_crops = UserSpecificCrop.objects.all()
    not_allowed_crops = UserSpecificCrop.objects.filter(user=user, allowed=False)
    #Crops specifically allowed for this user (those listed for them by others)
    user_crops = Crop.objects.filter(allowed_users=user)

    # Publicly available crops (those that are public for all users)
    public_crops = Crop.objects.filter(visibility='public')
    # Fetch crops owned by the user
    # user_crops = Crop.objects.filter(current_owner=user)  # Crops owned by the logged-in user

    # # Fetch public crops (can be viewed by all users)
    # public_crops = Crop.objects.filter(visibility='public')  # All crops that are public

    # # Fetch crops not allowed for the user to purchase
    # not_allowed_crops = Crop.objects.exclude(allowed_users=user)  # Crops not allowed for this user

    # # Debugging output to check data retrieval
    # print("User Crops:", user_crops)
    # print("Public Crops:", public_crops)
    # print("Not Allowed Crops:", not_allowed_crops)

    # if hasattr(user,'role'):
        # print(f"User Role: {user.role}")  # Debugging statement
    if user.role == 'FARMER':
        # # Crops specifically allowed for this user (those listed for them by others)
        # user_crops = Crop.objects.filter(allowed_users=user)

        # # Publicly available crops (those that are public for all users)
        # public_crops = Crop.objects.filter(visibility='public')

        return render(request, 'farmer_dashboard.html', {'user_crops': user_crops, 'public_crops': public_crops,'all_user_specifics': all_user_specific_crops,'not_allowed_crops': not_allowed_crops})

    elif user.role == 'DISTRIBUTOR':
        # user_crops = Crop.objects.filter(allowed_users=user)
        # public_crops = Crop.objects.filter(visibility='public')

        return render(request, 'distributor_dashboard.html', {'user_crops': user_crops, 'public_crops': public_crops,'all_user_specifics': all_user_specific_crops,'not_allowed_crops': not_allowed_crops})

    elif user.role == 'CONSUMER':
        # Consumers can view all crops that are publicly available
        # public_crops = Crop.objects.filter(visibility='public')
        # user_crops = Crop.objects.filter(allowed_users=user)
       
        return render(request, 'consumer_dashboard.html', {'user_crops': user_crops,'public_crops': public_crops,'all_user_specifics': all_user_specific_crops,'not_allowed_crops': not_allowed_crops})
        
    
    else:
        return redirect('list_crops')

# new Code 
# @login_required
# def farmer_dashboard(request):
#     user = request.user
#     user_crops = Crop.objects.filter(allowed_users=user)
#     public_crops = Crop.objects.filter(visibility='public')
#     all_user_specific_crops = UserSpecificCrop.objects.all()
#     not_allowed_crops = UserSpecificCrop.objects.filter(user=user, allowed=False)
#     return render(request, 'farmer_dashboard.html', {
#         'user_crops': user_crops,
#         'public_crops': public_crops,
#         'all_user_specifics': all_user_specific_crops,
#         'not_allowed_crops': not_allowed_crops
#     })

# @login_required
# def distributor_dashboard(request):
#     user = request.user
#     user_crops = Crop.objects.filter(allowed_users=user)
#     public_crops = Crop.objects.filter(visibility='public')
#     all_user_specific_crops = UserSpecificCrop.objects.all()
#     not_allowed_crops = UserSpecificCrop.objects.filter(user=user, allowed=False)
#     return render(request, 'distributor_dashboard.html', {
#         'user_crops': user_crops,
#         'public_crops': public_crops,
#         'all_user_specifics': all_user_specific_crops,
#         'not_allowed_crops': not_allowed_crops
#     })

# @login_required
# def consumer_dashboard(request):
#     user = request.user
#     public_crops = Crop.objects.filter(visibility='public')
#     user_crops = Crop.objects.filter(allowed_users=user)
#     all_user_specific_crops = UserSpecificCrop.objects.all()
#     not_allowed_crops = UserSpecificCrop.objects.filter(user=user, allowed=False)
#     return render(request, 'consumer_dashboard.html', {
#         'user_crops': user_crops,
#         'public_crops': public_crops,
#         'all_user_specifics': all_user_specific_crops,
#         'not_allowed_crops': not_allowed_crops
#     })


# Initialize Blockchain instance
blockchain = Blockchain()

# @login_required
# def list_crops(request):
#     if request.method == 'POST':
#         # Using .get() method to prevent MultiValueDictKeyError
#         crop_name = request.POST.get('name')
#         quantity_str = request.POST.get('quantity')
#         price_str = request.POST.get('price')

#         # Validating the input
#         if crop_name and quantity_str and price_str:
#             try:
#                 quantity = float(quantity_str)
#                 price = float(price_str)

#                 # Creating the crop instance
#                 crop = Crop.objects.create(
#                     name=crop_name,
#                     quantity=quantity,
#                     price=price,
#                     current_owner=request.user,
#                     current_stage='Listed by Farmer'
#                 )
#                 crop.save()

#                 # Get the crop ID after saving the crop
#                 crop_id = crop.id

#                 # Create a transaction and add it to the blockchain
#                 transaction = {
#                     'crop_name': crop_name,
#                     'quantity': quantity,
#                     'price': price,
#                     'owner': request.user.username,
#                     'stage': 'Listed by Farmer'
#                 }
                
#                 # Assuming you have a recipient for the transaction (it could be set to None or a placeholder if not applicable)
#                 recipient = None  # Replace with actual recipient if available
                
#                 # Add the transaction to the blockchain
#                 blockchain.add_transaction(transaction, recipient, price, crop_id)

#                 # Create a new block to store the transaction
#                 blockchain.mine_block()

#                 messages.success(request, f"Crop '{crop_name}' listed successfully and added to the blockchain!")
#             except ValueError:
#                 messages.error(request, "Invalid quantity or price. Please enter numeric values.")
#         else:
#             messages.error(request, "All fields are required.")

#         return redirect('list_crops')

#     # Fetching all crops to display
#     crops = Crop.objects.all()
#     return render(request, 'list_crops.html', {'crops': crops})

from django.shortcuts import render, redirect
from .models import Crop  # Assuming you have a Crop model
from django.contrib import messages
from django.contrib.auth.models import User

@login_required
def list_crops(request):
    if request.user.role == 'CUSTOMER':
        return render(request, 'not_allowed.html')

    if request.method == 'POST':
        form = CropForm(request.POST)

        if form.is_valid():
            crop = form.save(commit=False)
            crop.current_owner = request.user  # Set the current owner
            crop.current_stage = f'Listed by {request.user.role}'
            crop.visibility = form.cleaned_data['visibility']

            # Handle pricing based on visibility
            if crop.visibility == 'public':
                crop.price = form.cleaned_data['price']  # Set public price
                crop.specific_user_price = None  # Clear specific user price if public

            crop.save()  # Save the crop instance to the database

            # Save the allowed users if visibility is private
            if crop.visibility == 'private':
                crop.price = form.cleaned_data['price']  # Set public price
                crop.specific_user_price = form.cleaned_data['specific_user_price']

                allowed_user_ids = request.POST.getlist('allowed_users')
                crop.allowed_users.set(allowed_user_ids)

                # Create UserSpecificCrop instances for allowed users (allowed=True)
                for user_id in allowed_user_ids:
                    user = CustomUser.objects.get(id=user_id)
                    UserSpecificCrop.objects.create(crop=crop, user=user, allowed=True)

                # Create UserSpecificCrop instances for users who are not allowed (allowed=False)
                all_user_ids = CustomUser.objects.values_list('id', flat=True)
                not_allowed_user_ids = set(all_user_ids) - set(map(int, allowed_user_ids))

                for user_id in not_allowed_user_ids:
                    user = CustomUser.objects.get(id=user_id)
                    UserSpecificCrop.objects.create(crop=crop, user=user, allowed=False)

            # Add transaction to blockchain...
            sender = request.user.username
            recipient = None  # Adjust based on your app logic
            crop_id = crop.id
            # Use public_price if visibility is public, else use specific_user_price
            price_to_use = crop.price if crop.visibility == 'public' else crop.specific_user_price
            blockchain.add_transaction(sender, recipient, price_to_use, crop_id)
            blockchain.mine_block()

            messages.success(request, f"Crop '{crop.name}' listed successfully!")
            return redirect('list_crops')
    else:
        form = CropForm()

    # Get crops for current user and crops that are public or visible to the user
    user_crops = Crop.objects.filter(current_owner=request.user)
    public_crops = Crop.objects.filter(visibility='public')
    allowed_crops = Crop.objects.filter(allowed_users=request.user)

    crops = user_crops | allowed_crops

    return render(request, 'list_crops.html', {
        'form': form,
        'crops': crops,
        'public_crops': public_crops,
        'users': CustomUser.objects.all()
    })

# def buy_crop(request, crop_id):
#     crop = Crop.objects.get(id=crop_id)
#     if request.method == 'POST':
#         buyer = request.user
#         quantity = float(request.POST['quantity'])
#         price = float(request.POST['price'])

#         # Create a transaction record
#         transaction = Transaction.objects.create(
#             buyer=buyer,
#             seller=crop.current_owner,
#             crop=crop,
#             quantity=quantity,
#             price=price
#         )

#         # Update crop ownership and stage
#         crop.current_owner = buyer
#         crop.current_stage = 'Purchased by Distributor'
#         crop.save()

#         # Add transaction to blockchain
#         transaction_data = {
#             'buyer': buyer.username,
#             'seller': crop.current_owner.username,
#             'crop_name': crop.name,
#             'quantity': quantity,
#             'price': price
#         }
#         blockchain.add_block(transaction_data)

#         return redirect('list_crops')

#     return render(request, 'buy_crop.html', {'crop': crop})

@login_required
def buy_crops(request, crop_id):
    # Get the crop based on crop_id
    crop = get_object_or_404(Crop, id=crop_id)

    if request.method == 'POST':
        # Handle the purchase logic
        quantity_to_buy = int(request.POST.get('quantity', 0))
        if quantity_to_buy <= 0 or quantity_to_buy > crop.quantity:
            return render(request, 'buy_crop.html', {
                'crop': crop,
                'error': 'Invalid quantity'
            })

        # Calculate total cost using Decimal for precision
        total_cost = Decimal(crop.price) * quantity_to_buy

        # Get the user's balance (ensure it's Decimal)
        user = request.user
        user_balance = Decimal(user.balance)

        if user_balance < total_cost:
            return render(request, 'buy_crop.html', {
                'crop': crop,
                'error': 'Insufficient balance'
            })

        # Deduct the total cost from the user's balance
        user.balance -= total_cost

        # Save the updated user balance
        user.save()

        # Add the transaction to the blockchain
        blockchain.add_transaction(
            sender=crop.current_owner.username,
            recipient=user.username,
            amount=float(total_cost),  # Convert to float for blockchain
            crop_id=crop_id
        )

        # Mine a new block to confirm the transaction
        mined_block = blockchain.mine_block()

        # Create a transaction entry in the database
        transaction = Transaction.objects.create(
            seller=crop.current_owner,
            buyer=user,
            crop=crop,
            quantity=quantity_to_buy,
            price=float(crop.price),
            transaction_hash=mined_block.hash
        )

        # Create a PurchasedCrop entry
        purchased_crop = PurchasedCrop.objects.create(
            seller=crop.current_owner,
            buyer=user,
            crop=crop,
            quantity=quantity_to_buy,
            price=float(crop.price),
            transaction_hash=mined_block.hash
        )

        # Update the crop's quantity
        crop.quantity -= quantity_to_buy
        if crop.quantity == 0:
            crop.status = 'sold'
        crop.save()

        # Render the success page with transaction details
        return render(request, 'purchase_success.html', {
            'crop': crop,
            'quantity': quantity_to_buy,
            'total_cost': total_cost,
            'transaction_id': transaction.id,
            'purchased_crop_id': purchased_crop.id,
            'remaining_balance': float(user.balance),
            'transaction_hash':mined_block.hash
        })

    elif request.method == 'GET':
        # Optionally return crop details or a form for purchase
        return render(request, 'buy_crop.html', {
            'crop': crop
        })
    else:
        return render(request, 'buy_crop.html', {
            'crop': crop,
            'error': 'Invalid request method'
        })


# @login_required
# def buy_crops(request, crop_id):
#     # Get the crop based on crop_id
#     # if request.user.role=='FARMER':
#     #     return render(request, 'not_allowed.html')
    
#     crop = get_object_or_404(Crop, id=crop_id)

#     if request.method == 'POST':
#         # Handle the purchase logic
#         quantity_to_buy = int(request.POST.get('quantity', 0))
#         if quantity_to_buy <= 0 or quantity_to_buy > crop.quantity:
#             return JsonResponse({'error': 'Invalid quantity'}, status=400)

#         # Add the transaction to the blockchain
#         blockchain.add_transaction(
#             sender=crop.current_owner.username,
#             recipient=request.user.username,
#             amount=crop.price * quantity_to_buy,
#             crop_id=crop_id
#         )

#         # Mine a new block to confirm the transaction
#         mined_block = blockchain.mine_block()

#         # Create a transaction entry in the database
#         transaction = Transaction.objects.create(
#             seller=crop.current_owner,
#             buyer=request.user,  # Assuming the user is logged in
#             crop=crop,
#             quantity=quantity_to_buy,
#             price=crop.price,
#             transaction_hash=mined_block.hash  # Use the block hash
#         )

#         # Create a PurchasedCrop entry
#         purchased_crop = PurchasedCrop.objects.create(
#             seller=crop.current_owner,
#             buyer=request.user,
#             crop=crop,
#             quantity=quantity_to_buy,
#             price=crop.price,
#             transaction_hash=mined_block.hash  # Use the same hash for tracing
#         )

#         # Update the crop's quantity
#         crop.quantity -= quantity_to_buy
#         if crop.quantity == 0:
#             crop.status = 'sold'
#         crop.save()

#         return render(request, 'purchase_success.html', {
#             'transaction_id': transaction.id,
#             'purchased_crop_id': purchased_crop.id
#         })
    
#     elif request.method == 'GET':
#         # Optionally return crop details or a form for purchase
#         return render(request, 'buy_crop.html', {
#             'crop': crop
#         })
#     else:
#         return JsonResponse({'error': 'Invalid request method'}, status=405)
    
@login_required
def purchased_crops(request):
    # Example query, adjust as needed
    purchased_crops = PurchasedCrop.objects.filter(buyer=request.user)
    return render(request, 'purchased_crops.html', {'purchased_crops': purchased_crops})

@login_required
def trace_crops(request):
    # Get the crops purchased by the logged-in user
    purchased_crops = PurchasedCrop.objects.filter(buyer=request.user)

    # Add traceability information for each purchased crop
    crops_with_traceability = []
    for purchased_crop in purchased_crops:
        crop_id = purchased_crop.crop.id

        # Get the traceability information from the blockchain
        traceability_info = blockchain.trace_crop(crop_id)

        # Get the list of transactions related to this crop
        transactions = Transaction.objects.filter(crop_id=crop_id)

        # Append the crop data along with traceability and transaction information
        crops_with_traceability.append({
            'purchased_crop': purchased_crop,
            'traceability_info': traceability_info,
            'transactions': transactions,
        })

    # Pass the crops with traceability data to the template
    return render(request, 'trace_crop.html', {'crops_with_traceability': crops_with_traceability})

@login_required
def sell_crop(request):
    if request.method == 'POST':
        # Allow only distributors to sell crops
        if request.user.role != 'distributor':
            messages.error(request, "Only distributors can sell crops.")
            return redirect('list_crops')

        crop_name = request.POST['name']
        quantity = float(request.POST['quantity'])
        price = float(request.POST['price'])

        crop = Crop.objects.create(
            name=crop_name,
            quantity=quantity,
            price=price,
            current_owner=request.user,
            status='listed',
            current_stage='Listed by Distributor'
        )

        # Create a blockchain transaction (pseudo-code)
        transaction_index = blockchain.new_transaction(
            sender=request.user.username,
            recipient='Market',
            crop_name=crop.name,
            quantity=crop.quantity,
            price=crop.price
        )
        crop.transaction_hash = f'Transaction #{transaction_index}'
        crop.save()

        messages.success(request, f"You have listed {crop.name} for sale!")
        return redirect('transaction_history')

    return render(request, 'sell_crop.html')

@login_required
def blockchain_status(request):
    chain = blockchain.get_chain()
    return render(request, 'blockchain_status.html', {'chain': chain})

from django.shortcuts import redirect

def profile_view(request):
    # Redirect users to their dashboard or home page after login
    return redirect('dashboard')  # Replace 'dashboard' with the name of the view you want to redirect to

# def trace_crop(request, crop_id):
#     crop = get_object_or_404(Crop, id=crop_id)
#     return render(request, 'trace_crop.html', {'crop': crop})

def trace_crop(request, crop_id):
    block = blockchain.trace_crop(crop_id)
    return render(request, 'trace_crop.html', {'block': block})

@login_required
def user_logout(request):
    logout(request)  # This will log out the user
    return redirect('dashboard')   # Redirect to a success page

# def logout_success(request):
#     return redirect('dashboard')

# views.py
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib import messages

def custom_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "You are now logged in.")
            return redirect('dashboard')  # Redirect to the desired page after login
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'registration/login.html', {'form': form})

@login_required
def view_blockchain(request):
    blockchain_data = StoreBlock.objects.all()  # Get blockchain data
    return render(request, 'view_blockchain.html', {'blockchain_data': blockchain_data})

@login_required
def edit_crop_price(request, crop_id):
    crop = get_object_or_404(Crop, id=crop_id)

    # Ensure only the current owner can edit the crop
    if request.user != crop.current_owner:
        messages.error(request, "You do not have permission to edit this crop.")
        return redirect('list_crops')

    if request.method == 'POST':
        form = CropPriceUpdateForm(request.POST, instance=crop)
        if form.is_valid():
            # Get the updated price
            updated_price = form.cleaned_data['price']

            # Update the crop price
            crop.price = updated_price
            crop.save()  # Save the updated crop

            # Prepare transaction details
            sender = request.user.username
            recipient = None  # Depending on your application, this could be an actual recipient

            # Add the price update transaction to the blockchain
            blockchain.add_transaction(sender, recipient, updated_price, crop.id)

            # Mine a new block to confirm the transaction
            blockchain.mine_block()

            messages.success(request, f"Price for '{crop.name}' updated successfully and recorded in the blockchain!")
            return redirect('list_crops')
    else:
        form = CropPriceUpdateForm(instance=crop)

    return render(request, 'edit_crop_price.html', {'form': form, 'crop': crop})

@login_required
def my_crops(request):
    # Get the crops listed by the current user
    crops = Crop.objects.filter(current_owner=request.user)

    return render(request, 'my_crops.html', {'crops': crops})
from .models import CustomUser  # Adjust import based on your project structure

def user_info(request):
    """Adds user profile information to the context."""
    if request.user.is_authenticated:
        # Ensure profile_picture is a field in your CustomUser model
        profile_picture_url = request.user.profile_picture.url if hasattr(request.user, 'profile_picture') and request.user.profile_picture else 'default_profile.png'
        
        return {
            'profile_name': request.user.username,
            'dp_url': profile_picture_url,
            'available_tokens': getattr(request.user, 'balance', 0),  # Assuming token_balance is an attribute of CustomUser
        }
    return {}
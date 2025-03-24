from functools import wraps
from django.http import HttpResponse, JsonResponse
from profiles.models import Profile
from .models import Post

def action_permission(func):
    @wraps(func)  # Preserves the original function's metadata
    def wrapper(request, **kwargs):
        try:
            pk = kwargs.get('pk')
            
            # Check if user is authenticated
            if not request.user.is_authenticated:
                return JsonResponse({'error': 'Authentication required'}, status=401)
                
            # Get user profile
            try:
                profile = Profile.objects.get(user=request.user)
            except Profile.DoesNotExist:
                return JsonResponse({'error': 'User profile not found'}, status=404)
                
            # Get post
            try:
                post = Post.objects.get(pk=pk)
            except Post.DoesNotExist:
                return JsonResponse({'error': 'Post not found'}, status=404)
                
            # Check if user is author
            if profile.user == post.author.user:
                print('yes - permission granted')
                return func(request, **kwargs)
            else:
                print('no - permission denied')
                # Return appropriate response type based on request
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'error': 'Access denied'}, status=403)
                else:
                    return HttpResponse('Access denied - you need to be the author', status=403)
        except Exception as e:
            print(f"Error in permission check: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)
   
    return wrapper
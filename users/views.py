from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import Post, Like, Dislike, Share, Conversation, Message  # Assuming you have a Post model
from .forms import PostForm, UserUpdateForm, ProfileUpdateForm, MessageForm # Assuming you have a PostForm to handle post uploads
from .models import Profile, Post, Comment, Conversation, RoomMessage, Membership
from .forms import CommentForm
from django.contrib import messages
from django.db.models import Max, Subquery, OuterRef
import random
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponseBadRequest

@login_required
def home(request):
    if request.method == 'POST':
        content = request.POST.get('post_content')
        image = request.FILES.get('post_image')
        title = request.POST.get('post_title')
        post = Post.objects.create(author=request.user, title=title, content=content, image=image)
        post.save()
        return redirect('home')

    # Retrieve posts in random order
    posts = list(Post.objects.all())
    random.shuffle(posts)
    return render(request, 'users/home.html', {'posts': posts})



def login_view(request):
    if request.method == 'POST':
        # Get the username and password from the request
        username = request.POST['username']
        password = request.POST['password']

        # Attempt to authenticate the user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Ensure the user has a profile
            Profile.objects.get_or_create(user=user)

            # Log the user in
            login(request, user)

            # Redirect to the homepage
            print("User authenticated, redirecting to home...")
            return redirect('home')  # Redirect to your homepage
        else:
            print("Invalid credentials")
            # Re-render the login page with an error message
            return render(request, 'users/login.html', {'error': 'Invalid credentials'})
    # If the request is not a POST request, re-render the login page
    return render(request, 'users/login.html')


def signup_view(request):
    # If the request is a POST request, create a new user based on the data in the request form
    if request.method == 'POST':
        # Create a UserCreationForm instance with data from the request
        form = UserCreationForm(request.POST)
        # Check if the form is valid
        if form.is_valid():
            # Save the user to the database
            user = form.save()
            # Check if the profile already exists
            if not hasattr(user, 'profile'):
                # Create a profile for the new user
                Profile.objects.create(user=user)
            # Redirect to the login page after signup
            return redirect('login')
    # If the request is not a POST request, create an empty UserCreationForm instance
    else:
        form = UserCreationForm()
    
    # Render the signup page with the form
    return render(request, 'users/signup.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def profile_view(request, username=None):
    if username:
        user = get_object_or_404(User, username=username)  # Get user by username
    else:
        user = request.user  # Get the logged-in user

    posts = Post.objects.filter(author=user)  # Get posts authored by this user
    # is_own_profile = request.user == user  # Check if it's the user's own profile

    context = {
        'user': user,
        'posts': posts,
        # 'is_own_profile': is_own_profile,
    }
    return render(request, 'users/profile.html', context)
@login_required
def post_upload_view(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user  # Set the author of the post to the logged-in user
            post.save()
            return redirect('home')
    else:
        form = PostForm()
    return render(request, 'users/home.html', {'form': form})


# profile view
@login_required
def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=user).order_by('-created_at')
    return render(request, 'users/profile.html', {'profile_user': user, 'posts': posts})



def edit_profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)

            # Handle password change
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')

            if password1 and password2 and password1 == password2:
                user.set_password(password1)
                messages.success(request, 'Your password was successfully updated!')
            elif password1 or password2:
                messages.error(request, 'Passwords do not match.')

            user.save()  # Save the user with updated email and username
            profile_form.save()  # Save the profile with the updated bio and image
            update_session_auth_hash(request, user)  # Update session to prevent logout
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')  # Redirect to the profile page after successful update
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }

    return render(request, 'users/profile_edit.html', context)



# post or uploading
@login_required
def create_post(request):
    if request.method == 'POST':
        content = request.POST.get('post_content')
        image = request.FILES.get('post_image')
        if content or image:
            post = Post.objects.create(user=request.user, content=content, image=image)
            return redirect('home')  # Redirect to the home page after posting
    return render(request, 'users/home.html')


# post like , dislike , share related
@require_POST
def like_post(request, post_id):
    post = Post.objects.get(id=post_id)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return JsonResponse({'likes_count': post.likes.count()})

@require_POST
def dislike_post(request, post_id):
    post = Post.objects.get(id=post_id)
    if request.user in post.dislikes.all():
        post.dislikes.remove(request.user)
    else:
        post.dislikes.add(request.user)
    return JsonResponse({'dislikes_count': post.dislikes.count()})


@require_POST
def comment_post(request, post_id):
    post = Post.objects.get(id=post_id)
    comment_text = request.POST.get('text', '').strip()  # Strip to remove leading/trailing whitespace

    if not comment_text:
        return HttpResponseBadRequest("Comment cannot be empty")

    comment = Comment.objects.create(post=post, author=request.user, text=comment_text)
    return JsonResponse({
        'author': comment.author.username,
        'text': comment.text
    })




# post comment page 
@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('post_detail', post_id=post_id)  # Redirect to the same page
    else:
        form = CommentForm()
        context = {
        'post': post,
        'comments': comments,
        'form': form,
    }
    return render(request, 'users/post_detail.html', {'post': post, 'comments': comments, 'form': form})


# message form


def conversation_detail(request, username):
    other_user = get_object_or_404(User, username=username)
    conversation = Conversation.objects.filter(
        participants=request.user
    ).filter(
        participants=other_user
    ).distinct().first()

    if not conversation:
        conversation = Conversation.objects.create()
        conversation.participants.add(request.user, other_user)

    messages = conversation.messages.all().order_by('timestamp')

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.conversation = conversation
            message.sender = request.user
            message.save()
            return redirect('conversation_detail', username=other_user.username)
    else:
        form = MessageForm()

    return render(request, 'users/conversation_detail.html', {
        'conversation': conversation,
        'messages': messages,
        'form': form,
        'other_user_name': other_user.username
    })


@login_required
def conversation_list(request):
    conversations = Conversation.objects.filter(participants=request.user).annotate(
        last_message_time=Max('messages__timestamp')
    ).order_by('-last_message_time')

    conversation_details = []
    for conversation in conversations:
        other_user = conversation.participants.exclude(id=request.user.id).first()
        conversation_details.append({
            'username': other_user.username,
            'conversation': conversation
        })
    
    return render(request, 'users/conversation_list.html', {'conversation_details': conversation_details})


# rooms views
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Room, Membership, Message

@login_required
def create_room(request):
    if request.method == 'POST':
        name = request.POST['name']
        description = request.POST['description']
        room = Room.objects.create(name=name, description=description, creator=request.user)
        room.members.add(request.user)
        return redirect('room_detail', room_id=room.id)
    return render(request, 'users/create_room.html')

@login_required
def join_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    Membership.objects.get_or_create(user=request.user, room=room)
    return redirect('room_detail', room_id=room.id)

@login_required
def leave_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    membership = Membership.objects.filter(user=request.user, room=room).first()
    if membership:
        membership.delete()
    return redirect('room_list')

@login_required
def room_detail(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    messages = RoomMessage.objects.filter(room=room).order_by('timestamp')
    
    if request.method == 'POST':
        content = request.POST.get('content')
        image = request.FILES.get('image')
        voice_message = request.FILES.get('voice_message')
        
        RoomMessage.objects.create(
            room=room,
            user=request.user,
            content=content,
            image=image,
            voice_message=voice_message
        )
        return redirect('room_detail', room_id=room.id)
    
    return render(request, 'users/room_detail.html', {'room': room, 'messages': messages})

# in room
# Views for Searching and Adding Members
from django.db.models import Q

@login_required
def search_users(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    query = request.GET.get('query', '')
    users = User.objects.filter(Q(username__icontains=query) | Q(email__icontains=query)).exclude(id__in=room.members.values_list('id', flat=True))
    return render(request, 'users/search_users.html', {'room': room, 'users': users})

@login_required
def add_member(request, room_id, user_id):
    room = get_object_or_404(Room, id=room_id)
    user = get_object_or_404(User, id=user_id)
    Membership.objects.get_or_create(user=user, room=room)
    return redirect('room_detail', room_id=room.id)


@login_required
def recent_chats(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    recent_users = Message.objects.filter(room=room).values('user').distinct()
    users = User.objects.filter(id__in=recent_users)
    return render(request, 'users/recent_chats.html', {'room': room, 'users': users})

@login_required
def room_list(request):
    # Get the rooms the user has joined
    joined_rooms = Membership.objects.filter(user=request.user).select_related('room')

    # Annotate rooms with the timestamp of the latest message
    joined_rooms = joined_rooms.annotate(
        latest_message_timestamp=Max('room__roommessage__timestamp'),
        latest_message=Subquery(
            RoomMessage.objects.filter(room=OuterRef('room_id')).order_by('-timestamp').values('content')[:1]
        )
    ).order_by('-latest_message_timestamp')

    # Get all rooms excluding those already joined by the user
    all_rooms = Room.objects.exclude(id__in=joined_rooms.values_list('room_id', flat=True))

    return render(request, 'users/room_list.html', {
        'joined_rooms': joined_rooms,
        'all_rooms': all_rooms,
    })


@login_required
def join_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    Membership.objects.get_or_create(user=request.user, room=room)
    return redirect('room_list')

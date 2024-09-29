from django.urls import path
from . import views
from .views import room_list, join_room
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),  # Default profile for logged-in user
    path('profile/<str:username>/', views.profile_view, name='profile_detail'),  # Specific user profile
    path('edit/', views.edit_profile, name='edit_profile'),  # Edit profile
    path('post_upload/', views.post_upload_view, name='post_upload'),
    path('like-post/<int:post_id>/', views.like_post, name='like_post'),
    path('dislike-post/<int:post_id>/', views.dislike_post, name='dislike_post'),
    path('comment-post/<int:post_id>/', views.comment_post, name='comment_post'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    # message urls
    path('messages/', views.conversation_list, name='conversation_list'),
    path('messages/<str:username>/', views.conversation_detail, name='conversation_detail'),
    # rooms urls
    path('create-room/', views.create_room, name='create_room'),
    path('room/<int:room_id>/', views.room_detail, name='room_detail'),
    path('room/<int:room_id>/join/', views.join_room, name='join_room'),
    path('room/<int:room_id>/leave/', views.leave_room, name='leave_room'),
    # search user for rooms adding user
    path('room/<int:room_id>/search-users/', views.search_users, name='search_users'),
    path('room/<int:room_id>/add-member/<int:user_id>/', views.add_member, name='add_member'),
    path('room/<int:room_id>/recent-chats/', views.recent_chats, name='recent_chats'),
    path('rooms/', room_list, name='room_list'),
    path('rooms/join/<int:room_id>/', join_room, name='join_room'),
    # password reset
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='users/password_reset.html'), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), name='password_reset_complete'),
]
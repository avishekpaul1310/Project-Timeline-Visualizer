def notifications_processor(request):
    unread_notifications_count = 0
    if request.user.is_authenticated:
        unread_notifications_count = request.user.notifications.filter(is_read=False).count()
        print(f"User {request.user.username} has {unread_notifications_count} unread notifications")
    
    return {
        'unread_notifications_count': unread_notifications_count
    }
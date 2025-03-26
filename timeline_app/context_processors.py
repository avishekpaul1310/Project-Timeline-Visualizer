def notifications_processor(request):
    unread_notifications_count = 0
    if request.user.is_authenticated:
        try:
            unread_notifications_count = request.user.notifications.filter(is_read=False).count()
        except Exception as e:
            # Log the error but don't let it break the site
            print(f"Error in notifications_processor: {e}")
    
    return {
        'unread_notifications_count': unread_notifications_count
    }
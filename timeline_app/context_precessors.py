# timeline_app/context_processors.py
def notifications_processor(request):
    unread_notifications_count = 0
    if request.user.is_authenticated:
        unread_notifications_count = request.user.notifications.filter(is_read=False).count()
    
    return {
        'unread_notifications_count': unread_notifications_count
    }
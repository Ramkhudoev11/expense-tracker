def subscription_context(request):
    if request.user.is_authenticated:
        subscription = getattr(request.user, 'subscription', None)
        return {'subscription': subscription}
    return {'subscription': None}

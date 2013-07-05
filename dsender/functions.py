__author__ = 'delin'


def prepare_data(request):
    user = None

    if request.user.is_authenticated:
        user = request.user

    data = {
        'user': user,
    }

    return data
def custom_show_pyinstrument(request):
    return request.user.is_superuser


PYINSTRUMENT_SHOW_CALLBACK = "%s.custom_show_pyinstrument" % __name__

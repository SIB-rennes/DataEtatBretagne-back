
def allowed_file(filename, allowed_extensions=None):
    if allowed_extensions is None:
        allowed_extensions = {'csv'}

    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions
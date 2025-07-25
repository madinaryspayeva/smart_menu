import os
from uuid import uuid4


def user_avatar_upload_path(instance, filename):
    """Generate file path for new user avatar."""
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid4()}{ext}'
    return os.path.join('uploads', 'user_avatars', filename)
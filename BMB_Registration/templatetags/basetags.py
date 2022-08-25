import os
import random

from django.template import Library
from BCM.settings import MEDIA_ROOT, STATIC_ROOT

from BMB_Registration.models import User

register = Library()


# @register.simple_tag
@register.simple_tag(takes_context=False)
def mediaimages():

    image_dir = os.path.join(STATIC_ROOT, "retreatpictures")
    if not os.path.exists(image_dir):
        return None

    VALID = (".png", ".jpg", ".jpeg")

    images = [
        os.path.join("retreatpictures", x)
        for x in os.listdir(image_dir)
        if any(x.endswith(y) for y in VALID)
    ]
    random.shuffle(images)

    # look for an image called "splash" to put at the front if it exists
    try:
        splash = [
            ix
            for ix, x in enumerate(images)
            if os.path.basename(x).startswith("splash")
        ][0]
    except IndexError:  # no image called splash
        return images

    images[0], images[splash] = images[splash], images[0]  # swap

    return images


@register.filter
def give_talk(request):

    user = request.session.get("user")
    email = None

    if user:
        email = user.get("email")

    if email is None:
        return False

    user = User.objects.get(email=email)

    if user:
        return user.presentation == "talk"
    else:
        return False

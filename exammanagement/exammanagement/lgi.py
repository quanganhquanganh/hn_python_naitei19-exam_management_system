import os

from lgi import get_lgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "exammanagement.settings")

application = get_lgi_application()

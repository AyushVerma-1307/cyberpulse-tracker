import sys
path = '/home/YOUR_PYTHONANYWHERE_USERNAME/Xtra'
if path not in sys.path:
    sys.path.append(path)

from track import app as application

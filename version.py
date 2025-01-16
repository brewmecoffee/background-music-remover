"""
Version information for Background Music Remover
"""

# Version info
VERSION_MAJOR = 1
VERSION_MINOR = 0
VERSION_PATCH = 0
VERSION = f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_PATCH}"
BUILD_NUMBER = 1

# App info
APP_NAME = "Background Music Remover"
DESCRIPTION = "Remove background music from videos while keeping vocals"
AUTHOR = "Devashish Sharma"
COMPANY = "Devashish Sharma"
COPYRIGHT = "© 2025 Zit Media. All rights reserved."
WEBSITE = "https://github.com/brewmecoffee/background-music-remover"

def get_version_info():
    """Returns complete version information dictionary"""
    return {
        'version': VERSION,
        'version_tuple': (VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH, BUILD_NUMBER),
        'app_name': APP_NAME,
        'description': DESCRIPTION,
        'author': AUTHOR,
        'company': COMPANY,
        'copyright': COPYRIGHT,
        'website': WEBSITE
    }
[app]

# (str) Title of your application
title = Absensi Billman

# (str) Package name
package.name = absensibillman

# (str) Package domain (needed for android packaging)
package.domain = org.billman

# (str) Source where the main.py lives
source.dir = .

# (list) Source files to include (let it empty if you want to include all files)
source.include_exts = py,png,jpg,kv,atlas

# (list) Application requirements
# pastikan requirements sesuai dengan aplikasi Anda (misal: python3,kivy,requests)
requirements = python3,kivy,requests

# (str) Custom source folders for requirements
#requirements.source.kivy = ../../../kivy

# (str) Application versioning
version = 1.0

# (list) Supported orientations
orientation = portrait

# (list) List of permissions
android.permissions = INTERNET

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.min_api = 21

# (str) Android NDK version to use
android.ndk = 25b

# (str) Android SDK version to use
android.sdk = 33

# (bool) Automatically accept android SDK licenses
android.accept_sdk_license = True

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

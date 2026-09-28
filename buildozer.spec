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

# (str) Application versioning
version = 1.0

# (list) Application requirements
requirements = python3,kivy,requests

# (str) Supported orientation (landscape, portrait, all)
orientation = portrait

# (list) Permissions
android.permissions = INTERNET

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.min_api = 21

# (int) Android SDK version to use
android.sdk = 33

# (str) Android NDK version to use
android.ndk = 27.3.13750724

# (bool) Automatically accept android SDK licenses
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1

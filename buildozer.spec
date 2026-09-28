[app]

title = Absensi Billman
package.name = absensibillman
package.domain = org.billman

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,ttf

version = 1.0

requirements = python3,kivy==2.2.1,kivymd==1.1.1,pillow,requests,urllib3,chardet,idna,certifi,plyer,pyjnius,android

orientation = portrait
fullscreen = 0

android.permissions = INTERNET,CAMERA,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a
android.accept_sdk_license = True

[buildozer]

log_level = 2
warn_on_root = 1

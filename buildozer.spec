[app]
title = Mis llamadas
package.name = misllamadas
package.domain = org.ejemplo
source.dir = .
source.include_exts = py
version = 1.0
requirements = python3,kivy,pyjnius
p4a.branch = v2024.01.21
orientation = portrait
fullscreen = 0

# ACTION_DIAL no necesita permisos. Si cambias a ACTION_CALL, descomenta:
# android.permissions = CALL_PHONE

android.api = 34
android.minapi = 24
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1

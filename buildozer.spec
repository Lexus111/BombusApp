[app]
title = BombusPro
package.name = bombuspro
package.domain = org.bombus
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy==2.2.0,kivymd==1.1.1,sqlite3,kivy-garden.mapview,openssl,requests,urllib3,chardet,idna
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
# ВАЖНО: Это принимает лицензии автоматически
android.accept_sdk_license = True
# ВАЖНО: Используем API, который точно работает
android.api = 31
android.minapi = 21
p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1

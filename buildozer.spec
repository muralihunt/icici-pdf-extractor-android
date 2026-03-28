[app]
title = ICICI Extractor
package.name = iciciextractor
package.domain = org.icici.tools
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.1.0

# Added openssl and sqlite3 for runtime stability
requirements = python3,kivy==2.2.0,pymupdf,pandas,plyer,openssl,sqlite3

orientation = portrait
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.accept_sdk_license = True
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE
android.archs = arm64-v8a, armeabi-v7a

[buildozer]
log_level = 2

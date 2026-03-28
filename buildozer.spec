[app]
title = PDF Pro Searcher
package.name = pdfprosearcher
package.domain = org.murali.tools
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 2.0.1

requirements = python3,kivy==2.2.0,pymupdf,pandas,plyer,openssl,sqlite3,openpyxl

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

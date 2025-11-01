#!/usr/bin/env python
"""
Скрипт для проверки доступности media файлов
"""

import os
from pathlib import Path

# Добавляем путь к проекту
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "askpupkin.settings")
django.setup()

from django.conf import settings
from django.test import Client

print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")
print(f"MEDIA_URL: {settings.MEDIA_URL}")
print(f"DEBUG: {settings.DEBUG}")

# Проверяем существование файла
media_file = Path(settings.MEDIA_ROOT) / "img" / "avatar.jpg"
print(f"\nFile exists: {media_file.exists()}")
if media_file.exists():
    print(f"File size: {media_file.stat().st_size} bytes")

# Проверяем через test client
client = Client()
response = client.get("/media/img/avatar.jpg")
print(f"\nHTTP Status: {response.status_code}")
if response.status_code == 200:
    print(f"Content-Type: {response.get('Content-Type')}")
    print(f"Content-Length: {response.get('Content-Length')}")
else:
    print(f"Response: {response.content[:200]}")


# Temel imaj olarak Python'un en son sürümünü kullanın
FROM python:3.9-slim

# Çalışma dizinini belirleyin
WORKDIR /app

# Gereksinim dosyalarını kopyalayın ve bağımlılıkları yükleyin
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama dosyalarını kopyalayın
COPY . /app/

# Django uygulamanızın çalıştırılması için gerekli komutlar
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

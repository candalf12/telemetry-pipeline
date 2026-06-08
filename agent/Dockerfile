# Temel işletim sistemi olarak standart Ubuntu 22.04 kullanıyoruz
FROM ubuntu:22.04

# Gerekli derleme araçlarını (g++ ve cmake) kuruyoruz
# Etkileşimli kurulum ekranlarına takılmamak için DEBIAN_FRONTEND ayarını yapıyoruz
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# Konteyner içindeki çalışma dizinimizi ayarlıyoruz
WORKDIR /app

# Kendi bilgisayarımızdaki ajan kodlarını konteynerin içine kopyalıyoruz
COPY . /app/

# CMake kullanarak C++ projemizi derliyoruz
RUN cmake .
RUN make

# Konteyner ayağa kalktığında çalıştırılacak komutu belirliyoruz
CMD ["./agent"]
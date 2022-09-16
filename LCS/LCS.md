# LCS

Live Camera Surveillance

*Can use Gpu or Cpu ---Choose opencv options dependinng on preferences*
* With Gpu Option , update system with below requirements 
    `Ubuntu 18.04 LTS`
    `NVIDIA 460`
    `CUDA 10`
    `CuDNN 7.6.5`
    `gcc/g++ 7.5.0`

*LCS has been optimized to use cpu . No need for Gpu.*

# Dependencies
```
sudo apt-get install libssl-dev
sudo apt-get install qtbase5-dev
sudo apt-get install qtdeclarative5-dev
sudo apt-get install libhdf5-serial-dev
sudo apt-get install build-essential git unzip pkg-config
sudo apt-get install libjpeg-dev libpng-dev libtiff-dev
sudo apt-get install libavcodec-dev libavformat-dev libswscale-dev
sudo apt-get install libgtk2.0-dev libcanberra-gtk*
sudo apt-get install python3-dev python3-numpy python3-pip
sudo apt-get install libxvidcore-dev libx264-dev libgtk-3-dev
sudo apt-get install libtbb2 libtbb-dev libdc1394-22-dev
sudo apt-get install libv4l-dev v4l-utils
sudo apt-get install liblapacke-dev
sudo apt install default-jre
sudo apt install redis-server
sudo apt install -y mongodb
sudo apt-get install libboost-all-dev
sudo apt-get install libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev
sudo apt-get install libavresample-dev libvorbis-dev libxine2-dev
sudo apt-get install libfaac-dev libmp3lame-dev libtheora-dev
sudo apt-get install libopencore-amrnb-dev libopencore-amrwb-dev
sudo apt-get install libopenblas-dev libatlas-base-dev libblas-dev
sudo apt-get install liblapack-dev libeigen3-dev gfortran
sudo apt-get install liblapack-dev libeigen3-dev gfortran
sudo apt-get install libprotobuf-dev libgoogle-glog-dev libgflags-dev
 sudo apt install libpcre3-dev libssl-dev zlib1g-dev
sudo apt install libavcodec-dev libavformat-dev libswscale-dev libavresample-dev libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libxvidcore-dev x264 libx264-dev libfaac-dev libmp3lame-dev libtheora-dev libvorbis-dev python3-dev libatlas-base-dev gfortran libgtk-3-dev libv4l-dev

```
# CMAKE >=3.19

```
See [Install cmake from source](https://github.com/Kitware/CMake.git)
git clone https://github.com/Kitware/CMake.git
cd cmake directory then ..
./bootstrap && make && sudo make install

```
# OPENCV 4.5.0 (GPU )

```
cd /tmp
wget -O opencv.zip https://github.com/opencv/opencv/archive/master.zip
wget -O opencv_contrib.zip https://github.com/opencv/opencv_contrib/archive/master.zip
unzip opencv.zip
unzip opencv_contrib.zip
# Create build directory and switch into it
mkdir -p build && cd build
#build opencv with dnn modules and cuda support
cmake -D CMAKE_BUILD_TYPE=RELEASE  \
-D CMAKE_C_COMPILER=/usr/bin/gcc-7 \
-D CMAKE_INSTALL_PREFIX=/usr/local \
-D OPENCV_EXTRA_MODULES_PATH=../opencv_contrib-master/modules ../opencv-master \
-D BUILD_TIFF=ON \
-D WITH_FFMPEG=ON \
-D WITH_GSTREAMER=ON \
-D WITH_TBB=ON \
-D BUILD_TBB=ON \
-D WITH_EIGEN=ON \
-D WITH_V4L=ON \
-D WITH_LIBV4L=ON \
-D WITH_VTK=OFF \
-D WITH_QT=OFF \
-D WITH_OPENGL=ON \
-D OPENCV_ENABLE_NONFREE=ON \
-D INSTALL_C_EXAMPLES=OFF \
-D INSTALL_PYTHON_EXAMPLES=OFF \
-D PYTHON_DEFAULT_EXECUTABLE=$(which python3) \
-D BUILD_SHARED_LIBS=OFF \
-D BUILD_NEW_PYTHON_SUPPORT=ON \
-D OPENCV_GENERATE_PKGCONFIG=ON \
-D BUILD_TESTS=OFF \
-D WITH_CUDA=ON \
-D WITH_CUDNN=ON \
-D OPENCV_DNN_CUDA=ON \
-D ENABLE_FAST_MATH=ON \
-D CUDA_FAST_MATH=ON \
-D WITH_CUBLAS=ON \
-D OPENCV_PC_FILE_NAME=opencv4.pc \
-D OPENCV_ENABLE_NONFREE=ON \
-D CUDA_TOOLKIT_ROOT_DIR=/usr/local/cuda-10.0 -D BUILD_EXAMPLES=OFF ..
```
```
make -j$(nproc)
sudo make install
sudo ldconfig
pkg-config --modversion opencv4
```
# OPENCV 4.5.0 
```
cd /tmp
wget -O opencv.zip https://github.com/opencv/opencv/archive/master.zip
wget -O opencv_contrib.zip https://github.com/opencv/opencv_contrib/archive/master.zip
unzip opencv.zip
unzip opencv_contrib.zip
# Create build directory and switch into it
mkdir -p build && cd build
cmake -D CMAKE_BUILD_TYPE=RELEASE  \
-D CMAKE_C_COMPILER=/usr/bin/gcc-7 \
-D CMAKE_INSTALL_PREFIX=/usr/local \
-D OPENCV_EXTRA_MODULES_PATH=../opencv_contrib-master/modules ../opencv-master \
-D BUILD_TIFF=ON \
-D WITH_FFMPEG=ON \
-D WITH_GSTREAMER=ON \
-D WITH_TBB=ON \
-D BUILD_TBB=ON \
-D WITH_EIGEN=ON \
-D OPENCV_ENABLE_NONFREE=ON \
-D INSTALL_C_EXAMPLES=OFF \
-D INSTALL_PYTHON_EXAMPLES=OFF \
-D PYTHON_DEFAULT_EXECUTABLE=$(which python3) \
-D BUILD_SHARED_LIBS=OFF \
-D BUILD_NEW_PYTHON_SUPPORT=ON \
-D OPENCV_GENERATE_PKGCONFIG=ON \
-D OPENCV_PC_FILE_NAME=opencv4.pc \
-D OPENCV_ENABLE_NONFREE=ON \
-D BUILD_EXAMPLES=OFF ..
```
```
make -j$(nproc)
sudo make install
sudo ldconfig
pkg-config --modversion opencv4
```
# libmongoc and libbson
```
sudo apt-get install libbson-1.0-0
sudo apt-get install libmongoc-1.0-0
```
# mongo-c driver

```
git clone https://github.com/mongodb/mongo-c-driver.git
git checkout 1.17.0
mkdir cmake-build
cd cmake-build
cmake -DENABLE_AUTOMATIC_INIT_AND_CLEANUP=OFF ..
cmake --build .
sudo cmake --build . --target install
sudo cmake --build . --target uninstall [--]
```
# mongocxx-3.6.x

```
curl -OL https://github.com/mongodb/mongo-cxx-driver/releases/download/r3.6.5/mongo-cxx-driver-r3.6.5.tar.gz
tar -xzf mongo-cxx-driver-r3.6.5.tar.gz
cd mongo-cxx-driver-r3.6.5/build
cmake ..                                \
    -DCMAKE_BUILD_TYPE=Release          \
    -DCMAKE_INSTALL_PREFIX=/usr/local
sudo cmake --build . --target EP_mnmlstc_core
cmake --build .
sudo cmake --build . --target install
sudo cmake --build . --target uninstall [--]
```

#  hiredis
```
git clone https://github.com/redis/hiredis.git
cd hiredis
make
sudo make install
```

#  redis-plus-plus
```
git clone https://github.com/sewenew/redis-plus-plus.git
cd redis-plus-plus
mkdir build
cd build
cmake ..
make
sudo make install
```
# NGINX SERVER  + RTMP 
```
git clone https://github.com/sergey-dryabzhinsky/nginx-rtmp-module.git
wget http://nginx.org/download/nginx-1.17.6.tar.gz
tar -xf nginx-1.17.6.tar.gz
cd nginx-1.17.6
./configure --prefix=/usr/local/nginx --with-http_ssl_module --add-module=../nginx-rtmp-module
make -j 1
make install

#Nginx Directories
    #rtmp Directories 
    cd /var/www/htm/ && mkdir camera1 && cd ..
    #update rtmp section in nginx.conf file with updated directory
    sudo vi  /usr/local/nginx/conf/nginx.conf and paste the server block below inside rtmp section
    #rtmp [ hls streaming]
    server {
        listen 5612;
        application ld24 {
            hls_cleanup on;
            hls_playlist_length 3s;
            hls_path /var/www/html/camera1;
            hls_variant _low BANDWIDTH=160000;
            hls_variant _mid BANDWIDTH=320000;
            hls_variant _hi  BANDWIDTH=640000;
            hls_sync 2ms;
            hls_continuous on;
        }
    }
    
    sudo nginx -t [if Ok proceed]
    sudo systemctl restart nginx
    sudo systemctl restart nginx

    #for more example see sample-nginx.conf file 

    # amqp [stomp rabbitmq streaming plugin]
    stream {
            # List of upstream AMQP connections
            upstream stream_amqp {
                    least_conn;
                    server 127.0.0.1:15674;
            }

            # AMQP definition
            server {
                    listen 5003; # the port to listen on this server
                    proxy_pass stream_amqp; # forward traffic to this upstream group
                    proxy_timeout 3s;
                    proxy_connect_timeout 3s;
        }

    }


```
# DEPLOYMENT
LCS refers to the process of doing video surveillance of live cameras with the goal fof identifying POIs.
LCS  proceses real time video data  with the support of concurency and parallelism.This has been greaty enhanced by queing and multithreading.
*LCS*
```
```

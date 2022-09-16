#pragma once
#include <array>
#include <thread>
#include <stdio.h>
#include <chrono>
#include <vector>
#include <time.h>
#include <iostream>
#include <iterator>
#include <unistd.h>
#include "stdlib.h"

#include <opencv2/core.hpp>
#include <condition_variable>
#include <opencv2/opencv.hpp>
#include <opencv2/calib3d.hpp>
#include "opencv2/imgcodecs.hpp"
#include "MTCNN/mtcnn_opencv.hpp"

#include "tbb/concurrent_queue.h"
#include "tbb/concurrent_hash_map.h"

#include <sw/redis++/redis++.h>

#include <bsoncxx/json.hpp>
#include <mongocxx/client.hpp>
#include <mongocxx/stdx.hpp>
#include <mongocxx/uri.hpp>
#include <mongocxx/instance.hpp>

#include <bsoncxx/builder/stream/helpers.hpp>
#include <bsoncxx/builder/stream/document.hpp>
#include <bsoncxx/builder/stream/array.hpp>

using namespace std;
using namespace cv;
using namespace tbb;
using namespace sw::redis;

// Tunable Parameters
const int avg_face = 15;
const int minSize = 20;
const int stage = 4;
const string prefix = "../models/linux";

using namespace std::chrono_literals;

class MTCNN;

struct  frame_pointers{
    Mat avFrame;
    string *avUrl;
    int *TotalFrame;
};

class VideoStreamer{
    public:
        std::vector<int> cap_frame_width;
        std::vector<int> cap_frame_height;
        std::vector<int> cap_fps;
        std::vector<string> camera_source;
        std::vector<int> camera_index;
        std::vector<VideoCapture*> camera_capture;
        std::vector<concurrent_queue<frame_pointers>*> frame_queue;
        VideoStreamer(std::vector<string> source);
        void RedisQue(cv::Mat frame, std::string channelName,int q ,string dataSource);
        ~VideoStreamer();
    private:
        int camera_count;
};

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


#include <sys/types.h>
#include <sys/stat.h>
#include <stdlib.h>

#include <opencv2/core.hpp>
#include <condition_variable>
#include <opencv2/opencv.hpp>
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

extern "C" {
#include <libavutil/opt.h>
#include <libavcodec/avcodec.h>
#include <libavutil/channel_layout.h>
#include <libavutil/common.h>
#include <libavutil/imgutils.h>
#include <libavutil/mathematics.h>
#include <libavutil/samplefmt.h>
#include <libavformat/avformat.h>
#include <libswscale/swscale.h>
#include <libswresample/swresample.h>
#include <libavfilter/buffersink.h>
#include <libavfilter/buffersrc.h>
#include <libavutil/hwcontext.h>
}


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
    Mat *avFrame;
    float *avTime;
    long *posFrame;
    long *TotalFrame;
    string *avUrl;
    int *FrameVolume;
};

struct  recording_pointers{
    Mat *avFrame;
    int *FrameVolume;
};

class VideoStreamer{
    public:
        vector<int> cap_frame_width;
        vector<int> cap_frame_height;
        vector<int> cap_fps;
        vector<string> camera_source;
        vector<int> camera_index;
        vector<VideoCapture*> camera_capture;
        vector<concurrent_queue<recording_pointers>*> record_queue;
        vector<concurrent_queue<frame_pointers>*> frame_queue;
        VideoStreamer(vector<string> source);
        void RedisQue(cv::Mat frame, std::string channelName, float faceTime ,int q ,string dataSource , double videoProgress);
        ~VideoStreamer();
    private:
        int camera_count;
};

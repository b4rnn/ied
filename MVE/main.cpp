#include "stream.hpp"
#include "FacePreprocess.h"

vector<string> capture_destination;
Redis *pubConnection = new Redis("tcp://127.0.0.1:6379");

int GVEP(VideoStreamer &vStreamer , vector<string> capture_source){
    concurrent_queue<recording_pointers> *r;
    concurrent_queue<frame_pointers> *y;

    VideoCapture **capture_array = (VideoCapture **) malloc(capture_source.size() * sizeof(VideoCapture *));
    cv::Mat **frame =(cv::Mat  **) malloc(capture_source.size() * sizeof(cv::Mat  *));
    float timestamps[capture_source.size()];
    long frame_counter[capture_source.size()];
    long total_frames[capture_source.size()]; 
    std::string video_urls[capture_source.size()];

    int total_videos_frames = 0;

    for (int i = 0; i <capture_source.size(); i++) {
        Mat* _frame = new Mat();
        string url = capture_source[i];
        VideoCapture *capture = new VideoCapture(url , cv::CAP_FFMPEG);
        int _cap_frame_width = capture->get(cv::CAP_PROP_FRAME_WIDTH); 
        vStreamer.cap_frame_width.push_back(_cap_frame_width);
        int _cap_frame_height = capture->get(cv::CAP_PROP_FRAME_HEIGHT);
        vStreamer.cap_frame_height.push_back(_cap_frame_height);
        int _cap_fps = capture->get(cv::CAP_PROP_FPS);
        vStreamer.cap_fps.push_back(_cap_fps); 
        int frame_count = capture->get(cv::CAP_PROP_FRAME_COUNT);
        y = new concurrent_queue<frame_pointers>;
        vStreamer.frame_queue.push_back(y);
        r = new concurrent_queue<recording_pointers>;
        vStreamer.record_queue.push_back(r);
        capture_array[i] = capture;
        frame[i]= _frame;
        total_frames[i] = frame_count;
        video_urls[i] = url;
        total_videos_frames += frame_count;
    }
    
    while (true){

        for (int k= 0; k <capture_source.size(); k++) {
            try{
                (*capture_array[k]) >> *frame[k];
                std::this_thread::sleep_for(std::chrono::milliseconds(20));
                timestamps[k] = capture_array[k]->get(cv::CAP_PROP_POS_MSEC);
                frame_counter[k] = capture_array[k]->get(cv::CAP_PROP_POS_FRAMES);
                frame_pointers fp ={frame[k], &timestamps[k] , &frame_counter[k] ,&total_frames[k] ,&video_urls[k] ,&total_videos_frames};
                vStreamer.frame_queue[k]->push(fp);
                vStreamer.record_queue[k]->push({frame[k] , &total_videos_frames});
                
               }catch( cv::Exception& e ){
                const char* err_msg = e.what();
                std::cout << "LIVE CAM ERROR " <<  k << "FRAME NO " << frame_counter[k] << std::endl;
                continue;
            }
        }
    }
}

int FACIAL_DETECTION(VideoStreamer &vStreamer , vector<string> capture_source,MTCNN &detector ,vector<string> capture_channels){
    std::this_thread::sleep_for(std::chrono::milliseconds(5000));
    float factor = 0.709f;
    char buff[10];
    char string[10];
    vector<double> angle_list;
    float threshold[3] = {0.7f, 0.6f, 0.6f};
    double fps, current, score, angle, padding;

    MTCNN * _detector = &detector;
    struct frame_pointers *_frame_pointers =( struct frame_pointers  *) malloc(capture_source.size() * sizeof(struct frame_pointers));
    long frame_count[capture_source.size()];
    long frame_progress[capture_source.size()];

    cv::Mat frame;
    int frames_validator;
    int frames_counter = 0;

    // gt face landmark
    float v1[5][2] = {
            {30.2946f, 51.6963f},
            {65.5318f, 51.5014f},
            {48.0252f, 71.7366f},
            {33.5493f, 92.3655f},
            {62.7299f, 92.2041f}};

    cv::Mat src(5, 2, CV_32FC1, v1);

    while(true){
        for (int q = 0; q < vStreamer.camera_source.size(); q++) {
            bool ok = vStreamer.frame_queue[q]->try_pop(_frame_pointers[q]);
            if(ok){
                try{
                    ++frames_counter;
                    frame_count[q] = *_frame_pointers[q].TotalFrame;
                    frame_progress[q]= ((double)*_frame_pointers[q].posFrame/frame_count[q])*100;
                    if(*_frame_pointers[q].posFrame%vStreamer.cap_fps[q]  == 0){
                        vector<FaceInfo> faceInfo = _detector->Detect_mtcnn(*_frame_pointers[q].avFrame, minSize, threshold, factor, stage);
                        for (int i = 0; i < faceInfo.size(); i++) {
                            int x = (int) faceInfo[i].bbox.xmin;
                            int y = (int) faceInfo[i].bbox.ymin;
                            int w = (int) (faceInfo[i].bbox.xmax - faceInfo[i].bbox.xmin + 1);
                            int h = (int) (faceInfo[i].bbox.ymax - faceInfo[i].bbox.ymin + 1);

                            // Perspective Transformation
                            float v2[5][2] =
                                    {{faceInfo[i].landmark[0], faceInfo[i].landmark[1]},
                                    {faceInfo[i].landmark[2], faceInfo[i].landmark[3]},
                                    {faceInfo[i].landmark[4], faceInfo[i].landmark[5]},
                                    {faceInfo[i].landmark[6], faceInfo[i].landmark[7]},
                                    {faceInfo[i].landmark[8], faceInfo[i].landmark[9]},
                                    };
                            cv::Mat dst(5, 2, CV_32FC1, v2);
                            memcpy(dst.data, v2, 2 * 5 * sizeof(float));

                            //extract detected face 
                            if(faceInfo[i].bbox.score >=  0.99995){
                                frame = _frame_pointers[q].avFrame->clone();
                                cv::Mat m = FacePreprocess::similarTransform(dst, src);
                                cv::Mat aligned = frame.clone();
                                cv::warpPerspective(frame, aligned, m, cv::Size(96, 112), INTER_LINEAR);
                                cv::resize(aligned, aligned, Size(112, 112), 0, 0, INTER_LINEAR);

                                vStreamer.RedisQue(aligned, capture_channels[q], *_frame_pointers[q].avTime , q, *_frame_pointers[q].avUrl, frame_progress[q]);
                            }
                        }
                        faceInfo.clear();
                    }
                frames_validator = *_frame_pointers[q].FrameVolume - frames_counter;
                if(frames_validator ==0){
                    std::cout << " TRAINING OF  " << vStreamer.camera_source.size() << " VIDEOS FINISHED " << std::endl;
                    exit(3);
                }

                }catch( cv::Exception& e ){
                    const char* err_msg = e.what();
                    std::cout << " FACIAL DETECTION ERROR AT CAMERA " << q << std::endl;
                    continue;
                }
                ok = vStreamer.frame_queue[q]->try_pop(_frame_pointers[q]);
                vStreamer.frame_queue[q]->clear();
            }
        }
    }
}

int MEDIA_RECORDER(VideoStreamer &vStreamer , vector<string> capture_source ,vector<string> capture_channels){
    std::this_thread::sleep_for(std::chrono::milliseconds(5000));
    cv::Mat **frames =(cv::Mat  **) malloc(capture_source.size() * sizeof(cv::Mat  *));
    AVFormatContext **out_fmt_ctx_arr = (AVFormatContext **) malloc(capture_source.size() * sizeof(AVFormatContext *));
    AVCodecContext **out_codec_ctx_arr = (AVCodecContext **) malloc(capture_source.size() * sizeof(AVCodecContext *));
    AVStream **out_stream_arr = (AVStream **) malloc(capture_source.size() * sizeof(AVStream *));
    int out_stream_index_arr[capture_source.size()] , out_videoStream;
    struct SwsContext ** out_pSwsCtx_array = (SwsContext **) malloc(capture_source.size() * sizeof(SwsContext *));
    AVFrame **frame_arr = (AVFrame **) malloc(capture_source.size() * sizeof(AVFrame *));
    AVPacket **pkt_arr =(AVPacket **) malloc(capture_source.size() * sizeof(AVPacket *));

    std::vector<uint8_t>** imgbuf = (std::vector<uint8_t>  **) malloc(capture_source.size() * sizeof(std::vector<uint8_t> *));
    std::vector<uint8_t>** framebuf = (std::vector<uint8_t>  **) malloc(capture_source.size() * sizeof(std::vector<uint8_t> *));

    cv::Mat **image_array =(cv::Mat  **) malloc(capture_source.size() * sizeof(cv::Mat  *));
    struct recording_pointers *_recording_pointers =( struct recording_pointers  *) malloc(capture_source.size() * sizeof(struct recording_pointers));

    for (int i = 0; i < capture_source.size(); i++){
        AVFormatContext *format_ctx = avformat_alloc_context();
        std::string videoUrl  = capture_source[i];
        const char *outFname  = videoUrl.c_str();

        int directory_status;
        string folder_name = "/var/www/html/recordings/videos/"+capture_channels[i];
        const char* dirname = folder_name.c_str();
        directory_status = mkdir(dirname,0777);
        std::string segment_list_type = folder_name + "/stream.m3u8";

        avformat_alloc_output_context2(&format_ctx, nullptr, "hls", segment_list_type.c_str());
        if(!format_ctx) {
            return 1;
        }

        if (!(format_ctx->oformat->flags & AVFMT_NOFILE)) {
            int avopen_ret  = avio_open2(&format_ctx->pb, outFname,
                                        AVIO_FLAG_WRITE, nullptr, nullptr);
            if (avopen_ret < 0)  {
                std::cout << "failed to open stream output context, stream will not work! " <<  outFname << std::endl;
                return 1;
            }
        }

        AVCodec *out_codec = avcodec_find_encoder(AV_CODEC_ID_H264);
        AVStream *out_stream = avformat_new_stream(format_ctx, out_codec);
        AVCodecContext *out_codec_ctx = avcodec_alloc_context3(out_codec);
        //set codec params
        const AVRational dst_fps = {vStreamer.cap_fps[i], 1};
        out_codec_ctx->codec_tag = 0;
        out_codec_ctx->codec_id = AV_CODEC_ID_H264;
        out_codec_ctx->codec_type = AVMEDIA_TYPE_VIDEO;
        out_codec_ctx->width = vStreamer.cap_frame_width[i];
        out_codec_ctx->height =vStreamer.cap_frame_height[i];
        out_codec_ctx->gop_size = 5;
        out_codec_ctx->pix_fmt = AV_PIX_FMT_YUV420P;
        out_codec_ctx->framerate = dst_fps;
        out_codec_ctx->time_base.num = 1;
        out_codec_ctx->time_base.den = vStreamer.cap_fps[i]; // fps
        //out_codec_ctx->thread_type = FF_THREAD_SLICE;
        
        out_codec_ctx->time_base = av_inv_q(dst_fps);
        if (format_ctx->oformat->flags & AVFMT_GLOBALHEADER)
        {
            out_codec_ctx->flags |= AV_CODEC_FLAG_GLOBAL_HEADER;
        }
        
        int ret_avp = avcodec_parameters_from_context(out_stream->codecpar, out_codec_ctx);
        if (ret_avp < 0)
        {
            std::cout << "Could not initialize stream codec parameters!" << std::endl;
            exit(1);
        }
        
        if (!directory_status){
            std::cout << "CREATED DIR " <<  dirname << std::endl;
            std::string hls_segment_filename = folder_name + "/filename%03d.ts";
            std::cout << "HLS SEGMENT " <<  hls_segment_filename << std::endl;

            

            AVDictionary *hlsOptions = NULL;

            av_dict_set(&hlsOptions, "profile", "main", 0);
            av_dict_set(&hlsOptions, "preset", "ultrafast", 0);
            av_dict_set(&hlsOptions, "tune", "zerolatency", 0);
            //av_dict_set(&hlsOptions, "crf", "20", 0); //this gave me quality
            //av_dict_set(&hlsOptions, "force_key_frames", "expr:gte(t,n_forced*3)", AV_DICT_DONT_OVERWRITE);

            av_dict_set(&hlsOptions,     "hls_segment_type",   "mpegts", 0);
            av_dict_set(&hlsOptions,     "segment_list_type",  "m3u8",   0);
            //av_dict_set(&hlsOptions,     "segment_list",  segment_list_type.c_str(),   0);
            //av_dict_set_int(&hlsOptions, "hls_list_size",      3,  0);
            //av_dict_set_int(&hlsOptions, "hls_time",           3.0,   0);
            //av_dict_set(&hlsOptions,     "hls_flags",          "delete_segments", 0);
            av_dict_set(&hlsOptions,     "hls_segment_filename", hls_segment_filename.c_str(),   0);
            av_dict_set(&hlsOptions,     "hls_playlist_type", "vod", 0);
            av_dict_set(&hlsOptions,     "segment_time_delta", "1.0", 0);
            av_dict_set(&hlsOptions,     "hls_flags", "append_list", 0);
            av_dict_set_int(&hlsOptions, "reference_stream",   out_stream->index, 0);
            av_dict_set(&hlsOptions,     "segment_list_flags", "cache+live", 0);

            int ret_avo = avcodec_open2(out_codec_ctx, out_codec, &hlsOptions);
            if (ret_avo < 0)
            {
                std::cout << "Could not open video encoder!" << std::endl;
                exit(1);
            }
            out_stream->codecpar->extradata = out_codec_ctx->extradata;
            out_stream->codecpar->extradata_size = out_codec_ctx->extradata_size;
            out_stream_arr[i] = out_stream;

            av_dump_format(format_ctx, 0, outFname, 1);

            SwsContext * pSwsCtx = sws_getContext(vStreamer.cap_frame_width[i],vStreamer.cap_frame_height[i],AV_PIX_FMT_BGR24, vStreamer.cap_frame_width[i] , vStreamer.cap_frame_height[i] , AV_PIX_FMT_YUV420P , SWS_FAST_BILINEAR, NULL, NULL, NULL);
                    
            if (pSwsCtx == NULL) {
                fprintf(stderr, "Cannot initialize the sws context\n");
                return -1;
            }
            

            int ret_avfw = avformat_write_header(format_ctx, &hlsOptions);
            if (ret_avfw < 0)
            {
                std::cout << "Could not write header!" << std::endl;
                exit(1);
            }

            std::vector<uint8_t>* _imgbuf = new std::vector<uint8_t>(vStreamer.cap_frame_height[i] * vStreamer.cap_frame_width[i] * 3 + 16);
            std::vector<uint8_t>* _framebuf = new std::vector<uint8_t>(av_image_get_buffer_size(AV_PIX_FMT_YUV420P, vStreamer.cap_frame_width[i], vStreamer.cap_frame_height[i], 1));

            out_fmt_ctx_arr[i] = format_ctx;
            out_codec_ctx_arr[i] = out_codec_ctx;
            out_pSwsCtx_array[i] = pSwsCtx;
            cv::Mat* image = new cv::Mat(vStreamer.cap_frame_height[i], vStreamer.cap_frame_width[i], CV_8UC3, _imgbuf->data(), vStreamer.cap_frame_width[i] * 3);
            image_array[i]=image;
            imgbuf[i]=_imgbuf;
            framebuf[i]=_framebuf;
            
        }

         std::cout << "DONE REMUXING " <<  outFname << std::endl;
    }

    int av_ret;
    int frames_validator;
    int frames_counter = 0;
    AVFrame *frame = av_frame_alloc();
    
    while(1){
         for (int j = 0; j < capture_source.size(); j++) {
            try{
                ++frames_counter;
                av_image_fill_arrays(frame->data, frame->linesize, framebuf[j]->data(), AV_PIX_FMT_YUV420P, vStreamer.cap_frame_width[j], vStreamer.cap_frame_height[j], 1);
                frame->width = vStreamer.cap_frame_width[j];
                frame->height = vStreamer.cap_frame_height[j];
                frame->format = static_cast<int>(AV_PIX_FMT_YUV420P);

                vStreamer.record_queue[j]->try_pop( _recording_pointers[j]);
                image_array[j] = _recording_pointers[j].avFrame;
                const int stride[] = {static_cast<int>(image_array[j]->step[0])};
                sws_scale(out_pSwsCtx_array[j], &image_array[j]->data, stride , 0 , vStreamer.cap_frame_height[j] , frame->data, frame->linesize); 
                frame->pts += av_rescale_q(1, out_codec_ctx_arr[j]->time_base, out_stream_arr[j]->time_base);
                AVPacket pkt = {0};
                av_init_packet(&pkt);
                if(out_stream_arr[j] != NULL){
                    
                    int ret_frame = avcodec_send_frame(out_codec_ctx_arr[j], frame);
                    if (ret_frame < 0)
                    {
                        std::cout << "Error sending frame to codec context!" << std::endl;
                        exit(1);
                    }
                    int ret_pkt = avcodec_receive_packet(out_codec_ctx_arr[j], &pkt);
                    if (ret_pkt < 0)
                    {
                        std::cout << "Error receiving packet from codec context!" << " WIDTH " <<  vStreamer.cap_frame_width[0] <<" HEIGHT " << vStreamer.cap_frame_height[j] << std::endl;
                        exit(1);
                    }

                    if (pkt.pts == AV_NOPTS_VALUE || pkt.dts == AV_NOPTS_VALUE) {
                        av_log (out_fmt_ctx_arr[j], AV_LOG_ERROR,
                            "Timestamps are unset in a packet for stream% d\n", out_stream_arr[j]-> index);
                        return AVERROR (EINVAL);
                    }

                    if (pkt.pts < pkt.dts) {
                    av_log (out_fmt_ctx_arr[j], AV_LOG_ERROR, "pts%" PRId64 "<dts%" PRId64 "in stream% d\n",
                        pkt.pts, pkt.dts,out_stream_arr[j]-> index);
                    return AVERROR (EINVAL);
                    }
                    if (pkt.stream_index == out_stream_arr[j]->index){
                        av_interleaved_write_frame(out_fmt_ctx_arr[j], &pkt);
                    }
                }
                frames_validator = *_recording_pointers[j].FrameVolume - frames_counter;
                
                if(frames_validator ==0){
                    std::cout << " RECORDING  OF  " << vStreamer.camera_source.size() << " VIDEOS FINISHED " << std::endl;
                    //exit(3);
                }

            }catch( cv::Exception& e ){
                const char* err_msg = e.what();
                std::cout << "exception caught: corrrupted image on frame " << j << std::endl;
            }
            vStreamer.record_queue[j]->clear();
        }
    }
}

int main(int argc, char* argv[])
{
    vector<string> _capture_source(argv, argv+argc);
    _capture_source.erase(_capture_source.begin());

    vector<string> capture_source;
    vector<string> capture_data;
 
    std::stringstream superVideo(_capture_source[0]);
    string video;
    while (superVideo >> video)
    {
        capture_data.push_back(video);
        if (superVideo.peek() == ',')
            superVideo.ignore();
    }

    char chars[] = "[-{,\'}_]";

    for (int j=0;j<capture_data.size();j++)
    {
        std::string data = capture_data.at(j);
        for (unsigned int i = 0; i < strlen(chars); ++i)
        {
            data.erase(std::remove(data.begin(), data.end(), chars[i]), data.end());
        }
        std::string _video = data.substr(data.find(":")+1);
        capture_source.push_back(_video);
        std::string _channels = data.substr(0 ,data.find(":"));
        capture_destination.push_back(_channels);
    }

  VideoStreamer vStreamer(capture_source);
  //load models
  MTCNN detector(prefix);
  //threads
  thread t1(std::thread(GVEP, std::ref(vStreamer),  std::ref(capture_source) ));
  thread t2(std::thread(FACIAL_DETECTION, std::ref(vStreamer),  std::ref(capture_source), std::ref(detector), std::ref(capture_destination) ));
  thread t3(std::thread(MEDIA_RECORDER , std::ref(vStreamer),  std::ref(capture_source) , std::ref(capture_destination)));
  
  t1.join();
  t2.join();
  t3.join();
  std::this_thread::sleep_for(std::chrono::milliseconds(1000));
return 0;
}

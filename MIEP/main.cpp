#include "stream.hpp"
#include "FacePreprocess.h"

std::vector<string> capture_destination;
Redis *pubConnection = new Redis("tcp://127.0.0.1:6379");

int GVEP(VideoStreamer &vStreamer , std::vector<string> capture_source){
    concurrent_queue<frame_pointers> *y;

    cv::Mat **frame =(cv::Mat  **) malloc(capture_source.size() * sizeof(cv::Mat  *));
    std::string video_urls[capture_source.size()];

    int total_videos_frames = capture_source.size();

    for (int i = 0; i <capture_source.size(); i++) {
        string _url = capture_source[i];
        Mat* _frame = new cv::Mat;
        frame[i]= _frame;
        video_urls[i] = _url;
        y = new concurrent_queue<frame_pointers>;
        vStreamer.frame_queue.push_back(y);
    }

    std::cout << "FRAMES TOTAL " << total_videos_frames << std::endl;
    while(true){
        for (int k= 0; k <capture_source.size(); k++) {
            try{
                string url = capture_source[k];
                Mat this_frame = imread(url, IMREAD_UNCHANGED);
                (*frame[k]) =this_frame; 
                std::this_thread::sleep_for(std::chrono::milliseconds(20));
                frame_pointers fp ={(*frame[k]),&video_urls[k] ,&total_videos_frames};
                vStreamer.frame_queue[k]->push(fp);
                }catch( cv::Exception& e ){
                const char* err_msg = e.what();
                std::cout << "PIC ERROR " << video_urls[k] << std::endl;
                continue;
            }
        }
    }
}

int FACIAL_DETECTION(VideoStreamer &vStreamer , std::vector<string> capture_source,MTCNN &detector ,std::vector<string> capture_channels){
    std::this_thread::sleep_for(std::chrono::milliseconds(5000));
    float factor = 0.709f;
    char buff[10];
    char string[10];
    std::vector<double> angle_list;
    float threshold[3] = {0.7f, 0.6f, 0.6f};
    double fps, current, score, angle, padding;

    MTCNN * _detector = &detector;
    struct frame_pointers *_frame_pointers =( struct frame_pointers  *) malloc(capture_source.size() * sizeof(struct frame_pointers));

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
                    std::cout << " TRAINING OF  " << *_frame_pointers[q].avUrl  << std::endl;
                    ++frames_counter;
                    std::vector<FaceInfo> faceInfo = _detector->Detect_mtcnn(_frame_pointers[q].avFrame, minSize, threshold, factor, stage);
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
                        if(faceInfo[i].bbox.score >=  0.98){
                            std::cout << "Height " << h <<  " Width " << w  << " X " <<  x<< " Y " << y <<std::endl;
                            frame = _frame_pointers[q].avFrame.clone();
                            cv::Rect roi(x, y, w, h);
                            cv::Mat dFace = frame(roi);

                            cv::Mat m = FacePreprocess::similarTransform(dst, src);
                            cv::Mat aligned = frame.clone();
                            cv::warpPerspective(frame, aligned, m, cv::Size(96, 112), INTER_LINEAR);
                            cv::resize(aligned, aligned, Size(112, 112), 0, 0, INTER_LINEAR);

                            //cv::resize(dFace, dFace, Size(100, 100), 0, 0, INTER_AREA); 
                            vStreamer.RedisQue(aligned, capture_channels[q], q, *_frame_pointers[q].avUrl);
                        }
                    }

                    faceInfo.clear();

                frames_validator = *_frame_pointers[q].TotalFrame - frames_counter;
                if(frames_validator ==0){
                    std::cout << " TRAINING OF  " << vStreamer.camera_source.size() << " VIDEOS FINISHED " << std::endl;
                    exit(3);
                }
                }catch( cv::Exception& e ){
                    const char* err_msg = e.what();
                    std::cout << " FACIAL DETECTION ERROR AT FRAME " << frames_counter << std::endl;
                    continue;
                }
                ok = vStreamer.frame_queue[q]->try_pop(_frame_pointers[q]);
                vStreamer.frame_queue[q]->clear();
            }
        }
    }
}

int main(int argc, char* argv[])
{
    std::vector<string> _capture_source(argv, argv+argc);
    _capture_source.erase(_capture_source.begin());

    std::vector<string> capture_source;
    std::vector<string> capture_data;
 
    std::stringstream superVideo(_capture_source[0]);
    string video;
    while (superVideo >> video)
    {
        capture_data.push_back(video);
        if (superVideo.peek() == ',')
            superVideo.ignore();
    }

    char chars[] = "[{-,\'}]";

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
  t1.join();
  t2.join();
  std::this_thread::sleep_for(std::chrono::milliseconds(1000));
return 0;
}

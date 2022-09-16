#include "stream.hpp"

mongocxx::instance instance{};
mongocxx::uri uri("mongodb://127.0.0.1:27017");
mongocxx::client client(uri);
mongocxx::database db = client["photo_bomb"];
mongocxx::collection _collection = db["images"];

VideoStreamer::VideoStreamer(std::vector<string> stream_source){
    camera_source = stream_source;
    camera_count = camera_source.size();
}

VideoStreamer::~VideoStreamer(){
    //stopMultiCapture();
}

void VideoStreamer::RedisQue(cv::Mat frame, std::string channelName, int q , std::string dataSource) {
    auto end = std::chrono::system_clock::now();
    char filename[100];
    auto TimeStamp =  std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::system_clock::now().time_since_epoch()).count();
    sprintf(filename, "/var/www/html/quotas/%ld.png", TimeStamp);
    std::time_t end_time = std::chrono::system_clock::to_time_t(end); 
    auto builder1 = bsoncxx::builder::stream::document{};
    bsoncxx::document::value doc_value = builder1
            << "id" << channelName
            << "image" <<  "http://127.0.0.1/quotas/"+ std::to_string(TimeStamp)+".png"
            << "imageurl" << "http://127.0.0.1"+dataSource.erase(0,13)

    << bsoncxx::builder::stream::finalize;
    cv::imwrite(filename, frame);
    //PUT TO DB
    _collection.insert_one(doc_value.view());
}

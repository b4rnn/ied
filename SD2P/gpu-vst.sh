#!/usr/bin/parallel --shebang-wrap --pipe /bin/bash

######################################################
#                                                    #
#       VSS --video streaming server pipeline ----   #
#           CHUNKS VIDEO FOR ADAPTIVE STREAMING      #
#               ---GPU                               #
#         AUTHOR @ {PIXEL ASSASSIN }                 #
#                                                    #
######################################################
MP4_FILE=$1
MP4_FILE_DIRECTORY=$2
MP4_VIDEO_FILE_NAME=$MP4_FILE_DIRECTORY
#mkdir /var/www/html/$2

MP4_VIDEOS_MOBILE_DATASET_DIRECTORY=/var/www/html/$2

mkdir $MP4_VIDEOS_MOBILE_DATASET_DIRECTORY
mkdir /var/www/html/hls/
mkdir /var/www/html/hls/$MP4_FILE_DIRECTORY/
#ENCODE MP4 FOR MOBILE PHONES
    ffmpeg -i $MP4_FILE  -c:v h264_nvenc -rc:v vbr_hq -cq:v 19  -profile:v baseline  -pix_fmt yuv420p -c:a aac -strict -2 -ac 2 -b:a 128k -movflags faststart /var/www/html/$MP4_FILE_DIRECTORY/$MP4_VIDEO_FILE_NAME".mp4"

#ENCODED MP4 FILE PATH
mobile_mp4_video_as_output=$MP4_VIDEOS_MOBILE_DATASET_DIRECTORY/$MP4_VIDEO_FILE_NAME".mp4"
#HLS STREAMING
    #encode the mobile mp4 to m3u8 
            #1280x720
            #ffmpeg -i $mobile_mp4_video_as_output -c:a aac -strict experimental -c:v h264_nvenc -s 1280x720 -aspect 16:9 -f hls -hls_list_size 1000000 -hls_time 2 /var/www/html/hls/$MP4_FILE_DIRECTORY/$MP4_VIDEO_FILE_NAME"_720_out.m3u8"
            #540x960
            ffmpeg -i $mobile_mp4_video_as_output -c:a aac -strict experimental -c:v h264_nvenc -s 540x960 -aspect 16:9 -f hls -hls_list_size 1000000 -hls_time 2 /var/www/html/hls/$MP4_FILE_DIRECTORY/$MP4_VIDEO_FILE_NAME"_540_out.m3u8"
            #480x800
            ffmpeg -i $mobile_mp4_video_as_output -c:a aac -strict experimental -c:v h264_nvenc -s 854x480 -aspect 16:9 -f hls -hls_list_size 1000000 -hls_time 2 /var/www/html/hls/$MP4_FILE_DIRECTORY/$MP4_VIDEO_FILE_NAME"_480_out.m3u8"
            #360x640
            ffmpeg -i $mobile_mp4_video_as_output -c:a aac -strict experimental -c:v h264_nvenc -s 360x640 -aspect 16:9 -f hls -hls_list_size 1000000 -hls_time 2 /var/www/html/hls/$MP4_FILE_DIRECTORY/$MP4_VIDEO_FILE_NAME"_360_out.m3u8"
            #240x320
            ffmpeg -i $mobile_mp4_video_as_output -c:a aac -strict experimental -c:v h264_nvenc -s 240x320 -aspect 16:9 -f hls -hls_list_size 1000000 -hls_time 2 /var/www/html/hls/$MP4_FILE_DIRECTORY/$MP4_VIDEO_FILE_NAME"_240_out.m3u8"
        #create the streaming file
            #m3u8 playlist file
            playlist_file=/var/www/html/hls/$MP4_FILE_DIRECTORY/$MP4_VIDEO_FILE_NAME
            play_name=$MP4_VIDEO_FILE_NAME
            playlist_bucket=$playlist_file".m3u8"
            touch $playlist_bucket
            echo "#EXTM3U" >> $playlist_bucket
            echo "#EXT-X-STREAM-INF:PROGRAM-ID=1, BANDWIDTH=400000" >> $playlist_bucket
            echo $play_name"_240_out.m3u8" >> $playlist_bucket
            echo "#EXT-X-STREAM-INF:PROGRAM-ID=1, BANDWIDTH=700000" >> $playlist_bucket
            echo $play_name"_360_out.m3u8" >> $playlist_bucket
            echo "#EXT-X-STREAM-INF:PROGRAM-ID=1, BANDWIDTH=1000000" >> $playlist_bucket
            echo $play_name"_480_out.m3u8" >> $playlist_bucket
            echo "#EXT-X-STREAM-INF:PROGRAM-ID=1, BANDWIDTH=1500000" >> $playlist_bucket
            echo $play_name"_540_out.m3u8" >> $playlist_bucket
            #echo "#EXT-X-STREAM-INF:PROGRAM-ID=1, BANDWIDTH=2000000" >> $playlist_bucket
            #echo $play_name"_720_out.m3u8" >> $playlist_bucket

#REMOVE MP4_INPUT_FILE
#rm -rf $MP4_VIDEOS_MOBILE_DATASET_DIRECTORY
#rm -rf $MP4_FILE

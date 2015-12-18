/*
 * Copyright 2012 Open Source Robotics Foundation
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
*/

#include <gazebo/transport/transport.hh>
#include <gazebo/msgs/msgs.hh>
#include <gazebo/gazebo.hh>
#include <gazebo/common/UpdateInfo.hh>
#include <gazebo/common/SingletonT.hh>
#include <gazebo/common/Timer.hh>
#include <gazebo/util/UtilTypes.hh>
#include <gazebo/common/common.hh>
#include <iostream>


// For Ach
#include <errno.h>
#include <fcntl.h>
#include <assert.h>
#include <unistd.h>
#include <pthread.h>
#include <ctype.h>
#include <stdbool.h>
#include <math.h>
#include <inttypes.h>
#include <ach.h>

// For OpenCV
#include <opencv2/opencv.hpp>

// ach channels
ach_channel_t chan_cam;

const cv::Vec3b hsv_max = cv::Vec3b(120 + 30, 255, 255);
const cv::Vec3b hsv_min = cv::Vec3b(120 - 30,  50,   0);

struct {
	double err[2];
	bool onscreen;
} __attribute__((packed)) ball_offset = { { 0.0, 0.0 }, false };

void cb(ConstImageStampedPtr& msg) {
	// process image here
	cv::Mat_<cv:Vec3b> img(240, 320, cv::DataType<cv::Vec3b>::type);
	cv::cvtColor(msg->image().data, img, CV_RGB2HSV);
	cv::Mat_<uchar> mask(240, 320, CV_U8);
	cv::inRange(img, hsv_min, hsv_max, mask);
	
	double ave_y = 0.0, ave_x = 0.0;
	unsigned count = 0;
	for (int y = 0; y < 240; y++) for (int x = 0; x < 320; x++) {
		if (mask(y, x)) {
			count++;
			ave_x += x;
			ave_y += y;
		}
	}
	if (count == 0) ball_offset.onscreen = false;
	else {
		ball_offset.onscreen = true;
		ball_offset.err[0] = (ave_x / count) / 160.0 - 1.0;
		ball_offset.err[1] = -(ave_y / count) / 120.0 + 1.0;
	}
	
	ach_put(&chan_cam, ball_offset, sizeof(ball_offset));
}

int main(int argc, char** argv) {
	int r = ach_open(&chan_cam, "ball-offset", NULL);
	assert(r == ACH_OK);
	
	gazebo::load(argc, argv);
	gazebo::run();
	
	gazebo::transport::NodePtr node(new gazebo::transport::Node());
	node->Init();
	gazebo::transport::SubscriberPtr sub = node->SubScribe("/gazebo/default/pan_tilt/l_camera/camera/image", cb);
	
	for (;;) gazebo::common::Time::MSleep(100);
	gazebo::transport::fini();
	return 0;
}


int i = 0;
/////////////////////////////////////////////////
// Function is called everytime a message is received.
//void cb(gazebo::msgs::Image &_msg)
//void cb(const std::string& _msg)
//void cb(gazebo::msgs::ImageStamped &_msg)
//void cb(ConstWorldStatisticsPtr &_msg)
//void cb(const std::string& _msg)
void cbL(ConstImageStampedPtr &_msg)
{
  size_t size;
 ach_put(&chan_vid_chan_L, _msg->image().data().c_str() , _msg->image().data().size());

}

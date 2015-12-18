#include <boost/bind.hpp>
#include <gazebo/gazebo.hh>
#include <gazebo/transport/transport.hh>
#include <gazebo/msgs/msgs.hh>
#include <gazebo/physics/physics.hh>
#include <gazebo/common/common.hh>
#include <stdio.h>
#include <iostream>
#include <gazebo/transport/TransportTypes.hh>
#include <gazebo/msgs/MessageTypes.hh>
#include <gazebo/common/Time.hh>

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
#include <string.h>

// ach channels
static ach_channel_t chan_ref;
static ach_channel_t chan_state;

// data members
static double dxl_ref[2] = { 0.0, 0.0 };
static struct {
	double pos[2];
	double time;
} __attribute__((packed)) state = { { 0.0, 0.0 }, 0.0 };

namespace gazebo {

class ModelPtCtl : public ModelPlugin {
private:
	// gazebo pointers
	physics::ModelPtr model;
	physics::WorldPtr world;
	event::ConnectionPtr updateConnection;
	physics::JointPtr j_pan;
	physics::JointPtr j_tilt;
	
public:
	void Load(physics::ModelPtr parent, sdf::ElementPtr sdf) {
		int r = ach_open(&chan_ref, "pt-ref", NULL);
		assert(r == ACH_OK);
		ach_put(&chan_ref, &dxl_ref, sizeof(dxl_ref));
		
		r = ach_open(&chan_state, "pt-state", NULL);
		assert(r == ACH_OK);
		ach_put(&chan_state, &state, sizeof(state));
		
		model = parent;
		world = physics::get_world("default");
		
		if (FindJointByParam(sdf, j_pan, "pan") && FindJointByParam(sdf, j_tilt, "tilt"))
			updateConnection = event::Events::ConnectWorldUpdateBegin(
				boost::bind(&ModelPtCtl::OnUpdate, this));
	}
	
	bool FindJointByParam(sdf::ElementPtr sdf, physics::JointPtr& joint, std::string param) {
		if (!sdf->HasElement(param)) {
			gzerr << "param [" << param << "] not found\n";
			return false;
		}
		std::string elem_name = sdf->GetElement(param)->GetValueString();
		joint = model->GetJoint(elem_name);
		if (!joint) {
			gzerr << "joint by name [" << elem_name << "] not found in model\n";
			return false;
		}
		return true;
	}
	
	void OnUpdate() {
		size_t fs;
		int r = ach_get(&chan_ref, &dxl_ref, sizeof(dxl_ref), &fs, NULL, ACH_O_LAST);
		if (r == ACH_OK || r == ACH_STALE_FRAMES || r == ACH_MISSED_FRAME) {
			//gzerr << "expected size [" << sizeof(dxl_ref) << "] - got size [" << fs << "]\n";
			//assert(fs == sizeof(dxl_ref));
		}
		// else report issue
		
		j_pan->SetMaxForce(0, 10000);
		j_tilt->SetMaxForce(0, 10000);
		//j_pan->SetAngle(0, dxl_ref[0]);
		//j_tilt->SetAngle(0, dxl_ref[1]);
		j_pan->SetVelocity(0, dxl_ref[0]);
		j_tilt->SetVelocity(0, dxl_ref[1]);
		
		state.pos[0] = dxl_ref[0];
		state.pos[1] = dxl_ref[1];
		state.time = world->GetSimTime().Double();
		ach_put(&chan_state, &state, sizeof(state));
	}
};

GZ_REGISTER_MODEL_PLUGIN(ModelPtCtl)

}

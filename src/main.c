#include <string.h>
#include <stdio.h>

#include <hubo.h>

// Headers required for Ach
#include <errno.h>
#include <fcntl.h>
#include <assert.h>
#include <unistd.h>
#include <pthread.h>
#include <ctype.h>
#include <stdbool.h>
#include <math.h>
#include <inttypes.h>
#include "ach.h"

static inline double sqr(double x) { return x * x; }
static inline double acos_clmp(double x) { return acos(fmax(fmin(x, 1.0), -1.0)); }

// Constants
static const double LEG_UPPER = 300.3;
static const double LEG_LOWER = 300.38;
static const double LEG_TOTAL = 600.68;
static const double HIP_TO_MID = 88.43;

// Pre-calculated because old C can't handle the truth
// See the python version for the expressions these came from
static const double H_TOP = 594.135167702;
static const double H_MID = 394.135167702;
static const double L_H_MID = 347.067583851;
static const double L_AMP = 247.067583851;

static const double REF_INTERVAL = 0.05;

// Channel IDs
ach_channel_t chan_ref;      // Feed-Forward (Reference)
ach_channel_t chan_state;    // Feed-Back (State)
// State containers
hubo_ref_t ref;
hubo_state_t state;

void run_phase(void (*phase_func)(double), double phase_len) {
	size_t size = 0;
	int r = ach_get(&chan_state, &state, sizeof(state), &size, NULL, ACH_O_LAST);
	if (r != ACH_OK) assert(size == sizeof(state));
	double time_init = state.time;
	double time_last = time_init + phase_len;
	for (;;) {
		// Adaptive delay (timing)
		r = ach_get(&chan_state, &state, sizeof(state), &size, NULL, ACH_O_LAST);
		if (r != ACH_OK) assert(size == sizeof(state));
		double time_cur = state.time;
		// Phase time
		if (time_cur >= time_last) break;
		// Step calculations
		phase_func(time_cur - time_init);
		ach_put(&chan_ref, &ref, sizeof(ref));
		// Adaptive delay (sleep)
		r = ach_get(&chan_state, &state, sizeof(state), &size, NULL, ACH_O_LAST);
		if (r != ACH_OK) assert(size == sizeof(state));
		double delay = time_cur + REF_INTERVAL - state.time;
		usleep((unsigned)(delay * 1000000));
	}
	// Ensure phase reaches its final point
	phase_func(phase_len);
	ach_put(&chan_ref, &ref, sizeof(ref));
	usleep(500000); // Arbitrary inter-phase delay
}

// Robot lifts its arm over 1 second
void arm_phase(double phase_time) {
	// IK
	double gamma = (M_PI / 6)*(1.0 - cos(M_PI * phase_time));
	// Ref output
	ref.ref[RSR] = -gamma;
	ref.ref[LSR] = gamma;
}

// Robot eases into new support polygon over 2 seconds
void lean_phase(double phase_time) {
	// IK
	double w = (HIP_TO_MID/2)*(1.0 - cos((M_PI / 2) * phase_time));
	double theta = asin(w / LEG_TOTAL);
	// Ref output
	ref.ref[RHR] = ref.ref[LHR] = theta;
	ref.ref[RAR] = ref.ref[LAR] = -theta;
}

// Robot lifts its left leg over 2 seconds
void lift_phase(double phase_time) {
	// IK
	double l = L_AMP * cos((M_PI / 2) * phase_time) + L_H_MID;
	double phi = acos_clmp(( sqr(LEG_UPPER) + sqr(LEG_LOWER) - sqr(l)) / (2*LEG_UPPER*LEG_LOWER));
	double a   = acos_clmp(( sqr(LEG_UPPER) - sqr(LEG_LOWER) + sqr(l)) / (2*LEG_UPPER*l));
	double b   = acos_clmp((-sqr(LEG_UPPER) + sqr(LEG_LOWER) + sqr(l)) / (2*LEG_LOWER*l));
	double psi = M_PI - phi;
	// Ref output
	ref.ref[LHP] = -a;
	ref.ref[LKN] = psi;
	ref.ref[LAP] = -b;
}

// Robot moves up and down with a period of 4 seconds
void hop_phase(double phase_time) {
	// IK
	double h = 200*cos((M_PI / 2) * phase_time) + H_MID;
	double l = sqrt(sqr(h) + sqr(HIP_TO_MID));
	double theta = atan(HIP_TO_MID / h);
	double phi = acos_clmp(( sqr(LEG_UPPER) + sqr(LEG_LOWER) - sqr(l)) / (2*LEG_UPPER*LEG_LOWER));
	double a   = acos_clmp(( sqr(LEG_UPPER) - sqr(LEG_LOWER) + sqr(l)) / (2*LEG_UPPER*l));
	double b   = acos_clmp((-sqr(LEG_UPPER) + sqr(LEG_LOWER) + sqr(l)) / (2*LEG_LOWER*l));
	double psi = M_PI - phi;
	// Ref output
	ref.ref[RHR] = ref.ref[LHR] = theta;
	ref.ref[RAR] = -theta;
	ref.ref[LAR] = 0;
	ref.ref[RHP] = -a;
	ref.ref[RKN] = psi;
	ref.ref[RAP] = -b;
}

int main(int argc, char** argv) {
	// Open channels
	int r = ach_open(&chan_ref, HUBO_CHAN_REF_NAME , NULL);
	assert( ACH_OK == r );
	r = ach_open(&chan_state, HUBO_CHAN_STATE_NAME , NULL);
	assert( ACH_OK == r );
	
	// Initialize state containers
	memset(&ref  , 0, sizeof(ref  ));
	memset(&state, 0, sizeof(state));
	
	// Run the program
	puts("C Code!");
	puts("Lifting arms ...");
	run_phase(arm_phase, 1);
	puts("Leaning ...");
	run_phase(lean_phase, 2);
	puts("Lifting foot ...");
	run_phase(lift_phase, 2);
	puts("Hopping ...");
	run_phase(hop_phase, 25);
	
	// Return the robot to normal
	execl("/usr/bin/python", "/usr/bin/python", "src/reset.py", (char*) NULL);
}

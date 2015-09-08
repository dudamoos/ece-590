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

// Channel IDs
ach_channel_t chan_hubo_ref;      // Feed-Forward (Reference)
ach_channel_t chan_hubo_state;    // Feed-Back (State)

int main(int argc, char** argv) {
	// Open channels
	int r = ach_open(&chan_hubo_ref, HUBO_CHAN_REF_NAME , NULL);
	assert( ACH_OK == r );
	r = ach_open(&chan_hubo_state, HUBO_CHAN_STATE_NAME , NULL);
	assert( ACH_OK == r );
	
	// Initialize state containers
	struct hubo_ref H_ref;
	struct hubo_state H_state;
	memset(&H_ref  , 0, sizeof(H_ref  ));
	memset(&H_state, 0, sizeof(H_state));
	
	// Move arm into position
	H_ref.ref[LEB] = -M_PI / 2;
	H_ref.ref[LSP] = -M_PI / 2;
	H_ref.ref[LWY] = M_PI / 2;
	H_ref.ref[LF1] = M_PI / 2;
	H_ref.ref[LF2] = M_PI / 2;
	ach_put(&chan_hubo_ref, &H_ref, sizeof(H_ref));
	// Allow the robot time to stabilize
	sleep(5);
	
	size_t size;
	double wave_rot = M_PI / 3;
	for (;;) {
		// Display the current state
		r = ach_get(&chan_hubo_state, &H_state, sizeof(H_state), &size, NULL, ACH_O_LAST);
		if (r != ACH_OK) assert(size == sizeof(H_state));
		printf("LWP: %f\n", H_state.joint[LWP].pos);
		
		// Set the new state
		H_ref.ref[LWP] = wave_rot; // left shoulder roll
		wave_rot = -wave_rot; // use other direction next time
		ach_put(&chan_hubo_ref, &H_ref, sizeof(H_ref));
		
		// Wait for half a second to keep waving
		usleep(500000);
	}
}

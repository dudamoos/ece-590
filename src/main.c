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
	
	size_t size;
	double wave_rot = M_PI / 4;
	for (;;) {
		// Get current state
		r = ach_get(&chan_hubo_state, &H_state, sizeof(H_state), &size, NULL, ACH_O_LAST);
		if (r != ACH_OK) assert(size == sizeof(H_state));
		
		// Set new state
		H_ref.ref[LSP] = -M_PI / 2; // left shoulder pitch
		H_ref.ref[LEB] = -M_PI / 2; // left elbow bend
		
		// Set changing state
		H_ref.ref[LSR] = wave_rot; // left shoulder roll
		wave_rot = -wave_rot; // use other direction next time
		
		// Print current state
		printf("LSP: %f, LEB: %f, LSR: %f\n", H_state.joint[LSP].pos, H_state.joint[LEB].pos, H_state.joint[LSR].pos);
		
		// Send new state
		ach_put(&chan_hubo_ref, &H_ref, sizeof(H_ref));
		
		// Wait for half a second to keep waving
		usleep(500000);
	}
}

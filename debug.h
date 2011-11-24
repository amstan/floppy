#ifndef DEBUG_H
#define DEBUG_H

/*! @file debug.h
 * Provides various debugging functions to make programming easier
 * @param DEBUG flag, can either be defined inside here or in the makefile
 * @note All printing functions will automatically include \\n after them and fflush the stream
 * @code #ifdef DEBUG
           Code that will only get executed while debugging
         #endif
 */

///Prints debug info using printf(to stdout) if DEBUG is defined
#ifdef DEBUG
	#define debug(...) printf(dbg,__VA_ARGS__); printf("\n"); fflush(stdout);
#else
	#define debug(...) (1);
#endif

#endif

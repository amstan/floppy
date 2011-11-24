#include <msp430.h>

#include "bitop.h"
#include "debug.h"

#include <stdlib.h> 

#define RUN 0
#define DIR 1
#define SW 3
#define LED 6

#define PERIOD TACCR0
#define	C3	60300
#define	Cs3	56914.9505736345
#define	D3	53720.922154873
#define	Ds3	50706.1133967601
#define	E3	47860.2208603847
#define	F3	45174.0621957505
#define	Fs3	42636.9891891892
#define	G3	40244.0969387755
#define	Gs3	37986.2412713701
#define	A3	35853.8318181818
#define	As3	33841.7839368457
#define	B3	31942.3463189439
#define	C4	30148.8476092191
#define	Cs4	28457.4752868172
#define	D4	26860.4610774365
#define	Ds4	25352.2418281747
#define	E4	23929.3844613658
#define	F4	22586.384331243
#define	Fs4	21319.0707856969
#define	G4	20122.0484693878
#define	Gs4	18993.120635685
#define	A4	17926.9159090909
#define	As4	16920.8919684229
#define	B4	15971.1731594719
#define	C5	15074.7118967989
#define	Cs5	14228.4809784079
#define	D5	13430.0018728824
#define	Ds5	12676.3246283648
#define	E5	11964.6922306829
#define	F5	11293.1921656215

unsigned int song[] = {
	E4, E4, F4, G4, G4, F4, E4, D4, C4, C4, D4, E4, E4, D4, D4,
	E4, E4, F4, G4, G4, F4, E4, D4, C4, C4, D4, E4, D4, C4, C4,
};
unsigned char nsong = sizeof(song)/sizeof(int);

void __delay_ms(unsigned int ms) {
	for(;ms!=0;ms--) {
		__delay_cycles(16000);
	}
}

void chip_init(void) {
	WDTCTL = WDTPW + WDTHOLD; // Stop watchdog timer
	DCOCTL  = CALDCO_16MHZ; // Load the clock calibration
	BCSCTL1 = CALBC1_16MHZ;
}

void io_init(void) {
	P1DIR=0b01000011;
	P1OUT=0b00000000;
}

void timer_init(void) {
	//internal osc, 1xprescaler, up mode
	TACTL = TASSEL_2 + ID_1 + MC_1;

	//Enable Interrupts
	CCTL0 |= CCIE; //Timer
	_BIS_SR(GIE);  //Global
}

void floppy_init(unsigned int pos) {
	TACTL=0;
	
	unsigned char i;
	
	//move to the bottom
	set_bit(P1OUT,DIR);
	for(i=0;i<200;i++) {
		toggle_bit(P1OUT,RUN);
		__delay_ms(10);
	}
	
	//move to the middle
	clear_bit(P1OUT,DIR);
	for(i=0;i<pos;i++) {
		toggle_bit(P1OUT,RUN);
		__delay_ms(10);
	}
}

void __attribute__((interrupt (TIMER0_A0_VECTOR))) timer_vector() {
	toggle_bit(P1OUT,RUN);
	if(test_bit(P1OUT,RUN))
		toggle_bit(P1OUT,DIR);
}

int main(void)
{
	chip_init();
	io_init();
	
	PERIOD=0xFFFF;
	timer_init();
	while(test_bit(P1IN,SW));
	
	floppy_init(TAR%100+20);
	set_bit(P1OUT,LED);
	
	PERIOD=C3;
	timer_init();
	
	unsigned char i;
	while(1) {
		for(i=0;i<nsong;i++) {
			PERIOD=song[i];
			__delay_ms(500);
			while(!test_bit(P1IN,SW));
		}
	}
}

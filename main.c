#include <msp430.h>

#include "bitop.h"
#include "debug.h"

#include <msp430.h>
//#include <legacymsp430.h>
#include <stdint.h>
#include "config.h"
#include "ringbuffer.h"
#include "usci_serial.h"

#define RUN 0
#define DIR 4
#define SW 3
#define LED 6

#define PERIOD TACCR0

ringbuffer_ui8_16 usci_buffer = { 0, 0, { 0 } };

Serial<ringbuffer_ui8_16> usci0 = { usci_buffer };

void __attribute__((interrupt (USCIAB0RX_VECTOR))) USCI0RX_ISR() {
	usci_buffer.push_back(UCA0RXBUF);
}

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
	P1DIR=0b01010001;
	P1OUT=0b00000000;
}

void timer_init(unsigned int on) {
	//internal osc, 1xprescaler, up mode
	TACTL = TASSEL_2 + ID_1 + MC_1*(on!=0);

	//Enable Interrupts
	CCTL0 |= CCIE; //Timer
	_BIS_SR(GIE);  //Global
}

void floppy_init(unsigned int pos) {
	timer_init(0);
	
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
	
	usci0.init();
	usci0.xmit("UART Inited\n");
	usci0.xmit("Waiting for random button...\n");
	
	//Move the cursor to a random place based on input from button
	set_bit(P1OUT,LED);
	while(test_bit(P1IN,SW));
	timer_init(1);
	clear_bit(P1OUT,LED);
	while(!test_bit(P1IN,SW));
	usci0.xmit("Moving head...\n");
	floppy_init(TAR%60+20);
	set_bit(P1OUT,LED);
	usci0.xmit("Floppy Inited\n");
	
	timer_init(0);
	
	while(1) {
		unsigned char d0, d1;
		unsigned char type = usci0.recv();
		switch(type) {
			case 1: usci0.xmit("stop\n"); timer_init(0); break;
			case 2: usci0.xmit("play\n");
				d0=usci0.recv();
				d1=usci0.recv();
				PERIOD=(d0<<8)|d1;
				timer_init(1);
				break;
			default:
			case 0: usci0.xmit("align\n"); break;
		}
		__delay_ms(10);
	}
}

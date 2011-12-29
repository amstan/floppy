#include <msp430.h>

#include "bitop.h"
#include "debug.h"

#include <msp430.h>
#include <stdint.h>
#include "config.h"
#include "ringbuffer.h"
#include "usci_serial.h"

#define ALIGN 0
#define STOP 1
#define PLAY 2
#define INSTR 3
#define TOGGLE_DIR 4
#define RESET 5

#define INSTR_OSCILATE 0
#define INSTR_VIOLIN 1
unsigned char instr=INSTR_OSCILATE;

#define POS_START 0
#define POS_END 160
#define POS_THRESHOLD 30
unsigned int pos=0;
unsigned char dir=0;

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
	#define LED_R 0
	#define LED_G 6
	#define RUN 4
	#define DIR 5
	#define SW 3
	
	P1DIR=0b01110001;
	P1OUT=0b00000000;
}

void timer_init(unsigned int on) {
	//internal osc, 8xprescaler, up mode
	TACTL = TASSEL_2 + ID_2 + MC_1*(on!=0);

	//Enable Interrupts
	CCTL0 |= CCIE; //Timer
	_BIS_SR(GIE);  //Global
}

void floppy_init(unsigned int target_pos) {
	timer_init(0);
	
	//move to the bottom
	set_bit(P1OUT,DIR);
	for(unsigned char i=0;i<200;i++) {
		toggle_bit(P1OUT,RUN);
		__delay_ms(10);
	}
	
	//move to target_pos
	clear_bit(P1OUT,DIR);
	for(pos=0;pos<target_pos;pos++) {
		toggle_bit(P1OUT,RUN);
		__delay_ms(10);
	}
}

void __attribute__((interrupt (TIMER0_A0_VECTOR))) timer_vector() {
	toggle_bit(P1OUT,RUN);
	
	if(instr==INSTR_OSCILATE) {
		if(test_bit(P1OUT,RUN))
			toggle_bit(P1OUT,DIR);
	} else {
		//instr==INSTR_VIOLIN
		change_bit(P1OUT,DIR,dir);
		
		if(dir==0) {
			pos++;
			if(pos>(POS_END-POS_THRESHOLD)) dir^=1;
		} else {
			pos--;
			if(pos<(POS_START+POS_THRESHOLD)) dir^=1;
		}
	}
}

int main(void) {
	chip_init();
	io_init();
	PERIOD=0xFFFF;
	
	usci0.init();
	
	floppy_init(POS_END/2);
	
	//Move the cursor to a random place based on input from button
// 	set_bit(P1OUT,LED_G);
// 	while(test_bit(P1IN,SW));
// 	timer_init(1);
// 	clear_bit(P1OUT,LED_G);
// 	while(!test_bit(P1IN,SW));
// 	floppy_init(TAR%120+20);
// 	set_bit(P1OUT,LED_G);
//	timer_init(0);
	
	while(1) {
		unsigned char d0, d1;
		unsigned char type = usci0.recv();
		switch(type) {
			case STOP:
				timer_init(0);
				break;
			
			case PLAY:
				d0=usci0.recv();
				d1=usci0.recv();
				PERIOD=(d0<<8)|d1;
				timer_init(1);
				break;
			
			case INSTR:
				instr=usci0.recv();
				break;
			
			case TOGGLE_DIR:
				dir^=1;
				break;
			
			case RESET:
				floppy_init(POS_END/2);
				break;
			
			default:
			case ALIGN:
				break;
		}
		__delay_ms(10);
	}
}

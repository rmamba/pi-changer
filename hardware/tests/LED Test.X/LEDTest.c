#include "p24Fxxxx.h"
#include "LEDTest.h"

int main(void)
{
    TRISAbits.TRISA7 = 0; PORTAbits.RA7 = 0;
    TRISAbits.TRISA8 = 0; PORTAbits.RA8 = 0;
    TRISAbits.TRISA9 = 0; PORTAbits.RA9 = 0;
    TRISAbits.TRISA10 = 0; PORTAbits.RA10 = 0;

    while(1)
    {
        PORTAbits.RA7 = 1; DelayCount(); PORTAbits.RA7;
        PORTAbits.RA8 = 1; DelayCount(); PORTAbits.RA8;
        PORTAbits.RA9 = 1; DelayCount(); PORTAbits.RA9;
        PORTAbits.RA10 = 1; DelayCount(); PORTAbits.RA10;
    }
}

void DelayCount(void)
{
    unsigned short Delay;
    Delay = 0x8000;

    while (Delay>0)
    {
        Delay--;
        Nop();
    }
}

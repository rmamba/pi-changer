/*
 * File:   bootloader.c
 * Author: rmamba@gmail.com
 * GitHub: https://github.com/rmamba/pi-changer
 *
 * Created on 25 February 2014, 19:08
 *
 * Based on source from Microchip Inc. but modified for PIC24FJ64GB004 microcontroller
 * Source: http://www.microchip.com/stellent/idcplg?IdcService=SS_GET_PAGE&nodeId=1824&appnote=en530200
 */

#include "p24Fxxxx.h"
#include "bootloader.h"

/** CONFIGURATION **************************************************/
_CONFIG1(FWDTEN_OFF & ICS_PGx1 & GWRP_OFF & JTAGEN_OFF & GCP_OFF);
_CONFIG2(FNOSC_FRCPLL & IESO_OFF & PLL96MHZ_OFF & PLLDIV_DIV2 & OSCIOFNC_OFF & FCKSM_CSDCMD);
_CONFIG3(SOSCSEL_IO & WPDIS_WPDIS & WPCFG_WPCFGDIS);
_CONFIG4(DSWDTEN_OFF & DSBOREN_OFF);

/** VARIABLES ******************************************************/
char Buffer[PM_ROW_SIZE*3 + 1];

int main(void)
{
    uReg32 SourceAddr;
    uReg32 Delay;

    OSCTUN = 0;
    CLKDIVbits.RCDIV=0;                                                         // 8Mhz internal RC no divide
    CLKDIVbits.CPDIV=0;                                                         // USB System Clock Select bits - set to 32MHz
    CLKDIVbits.DOZEN=0;                                                         // Disable peripheral clock divider
    CLKDIVbits.DOZE=0;                                                          // 1:1
    RCONbits.SWDTEN=0;                                                          /* Disable Watch Dog Timer*/
    while(OSCCONbits.LOCK!=1) {};                                               /* Wait for PLL to lock*/

    SourceAddr.Val32 = 0xc00;
    Delay.Val32 = ReadLatch(SourceAddr.Word.HW, SourceAddr.Word.LW);
    if(Delay.Val[0] == 0)
    {
        ResetDevice();
    }

    T2CONbits.T32 = 1;                                                          /* to increment every instruction cycle */
    IFS0bits.T3IF = 0;                                                          /* Clear the Timer3 Interrupt Flag */
    IEC0bits.T3IE = 0;                                                          /* Disable Timer3 Interrup Service Routine */

    if((Delay.Val32 & 0x000000FF) != 0xFF)
    {
        /* Convert seconds into timer count value */
        Delay.Val32 = ((UWord32)(FCY)) * ((UWord32)(Delay.Val[0]));
        PR3 = Delay.Word.HW;
        PR2 = Delay.Word.LW;
        /* Enable Timer */
        T2CONbits.TON=1;
    }

    U2BRG = BRGVAL ;                                                            /*  BAUD Rate Setting of Uart2  */
    U2MODE = 0x8000;                                                            /* Reset UART to 8-n-1, alt pins, and enable */
    U2STA  = 0x0400;                                                            /* Reset status register and enable TX */

    while(1)
    {
        char Command;
        GetChar(&Command);
        switch(Command)
        {
            case COMMAND_READ_PM:                                               /*tested*/
            {
                uReg32 SourceAddr;
                GetChar(&(SourceAddr.Val[0]));
                GetChar(&(SourceAddr.Val[1]));
                GetChar(&(SourceAddr.Val[2]));
                SourceAddr.Val[3]=0;
                ReadPM(Buffer, SourceAddr);
                WriteBuffer(Buffer, PM_ROW_SIZE*3);
                break;
            }

            case COMMAND_WRITE_PM:				/* tested */
            {
                uReg32 SourceAddr;
                int    Size;
                GetChar(&(SourceAddr.Val[0]));
                GetChar(&(SourceAddr.Val[1]));
                GetChar(&(SourceAddr.Val[2]));
                SourceAddr.Val[3]=0;
                for(Size = 0; Size < PM_ROW_SIZE*3; Size++)
                {
                    GetChar(&(Buffer[Size]));
                }
                Erase(SourceAddr.Word.HW,SourceAddr.Word.LW,PM_ROW_ERASE);
                WritePM(Buffer, SourceAddr);		/*program page */
                PutChar(COMMAND_ACK);				/*Send Acknowledgement */
                break;
            }

            case COMMAND_READ_ID:
            {
                uReg32 SourceAddr;
                uReg32 Temp;
                SourceAddr.Val32 = 0xFF0000;
                Temp.Val32 = ReadLatch(SourceAddr.Word.HW, SourceAddr.Word.LW);
                WriteBuffer(&(Temp.Val[0]), 4);
                SourceAddr.Val32 = 0xFF0002;
                Temp.Val32 = ReadLatch(SourceAddr.Word.HW, SourceAddr.Word.LW);
                WriteBuffer(&(Temp.Val[0]), 4);
                break;
            }

            case COMMAND_WRITE_CM:
            {
                int    Size;
                for(Size = 0; Size < CM_ROW_SIZE*3;)
                {
                        GetChar(&(Buffer[Size++]));
                        GetChar(&(Buffer[Size++]));
                        GetChar(&(Buffer[Size++]));
                        PutChar(COMMAND_ACK);				/*Send Acknowledgement */
                }
                break;
            }
            case COMMAND_RESET:
            {
                uReg32 SourceAddr;
                int    Size;
                uReg32 Temp;

                for(Size = 0, SourceAddr.Val32 = 0xF80000; Size < CM_ROW_SIZE*3;                                                                                                                Size +=3, SourceAddr.Val32 += 2)
                {
                    if(Buffer[Size] == 0)
                    {
                        Temp.Val[0]=Buffer[Size+1];
                        Temp.Val[1]=Buffer[Size+2];
                        WriteLatch( SourceAddr.Word.HW,
                            SourceAddr.Word.LW,
                            Temp.Word.HW,
                            Temp.Word.LW);
                        WriteMem(CONFIG_WORD_WRITE);
                    }
                }

                ResetDevice();
                break;
            }

            case COMMAND_NACK:
            {
                ResetDevice();
                break;
            }


            default:
                PutChar(COMMAND_NACK);
                break;
        }
    }
}

/******************************************************************************/
void GetChar(char * ptrChar)
{
    while(1)
    {
        /* if timer expired, signal to application to jump to user code */
        if(IFS0bits.T3IF == 1)
        {
            * ptrChar = COMMAND_NACK;
            break;
        }
        /* check for receive errors */
        if(U2STAbits.FERR == 1)
        {
            continue;
        }

        /* must clear the overrun error to keep uart receiving */
        if(U2STAbits.OERR == 1)
        {
            U2STAbits.OERR = 0;
            continue;
        }

        /* get the data */
        if(U2STAbits.URXDA == 1)
        {
            T2CONbits.TON=0; /* Disable timer countdown */
            * ptrChar = U2RXREG;
            break;
        }
    }
}


/******************************************************************************/
void ReadPM(char * ptrData, uReg32 SourceAddr)
{
    int    Size;
    uReg32 Temp;

    for(Size = 0; Size < PM_ROW_SIZE; Size++)
    {
        Temp.Val32 = ReadLatch(SourceAddr.Word.HW, SourceAddr.Word.LW);

        ptrData[0] = Temp.Val[2];;
        ptrData[1] = Temp.Val[1];;
        ptrData[2] = Temp.Val[0];;

        ptrData = ptrData + 3;

        SourceAddr.Val32 = SourceAddr.Val32 + 2;
    }
}
/******************************************************************************/

void WriteBuffer(char * ptrData, int Size)
{
    int DataCount;

    for(DataCount = 0; DataCount < Size; DataCount++)
    {
        PutChar(ptrData[DataCount]);
    }
}
/******************************************************************************/
void PutChar(char Char)
{
    while(!U2STAbits.TRMT);

    U2TXREG = Char;
}
/******************************************************************************/
void WritePM(char * ptrData, uReg32 SourceAddr)
{
    int    Size,Size1;
    uReg32 Temp;
    uReg32 TempAddr;
    uReg32 TempData;

    for(Size = 0,Size1=0; Size < PM_ROW_SIZE; Size++)
    {

        Temp.Val[0]=ptrData[Size1+0];
        Temp.Val[1]=ptrData[Size1+1];
        Temp.Val[2]=ptrData[Size1+2];
        Temp.Val[3]=0;
        Size1+=3;

        WriteLatch(SourceAddr.Word.HW, SourceAddr.Word.LW,Temp.Word.HW,Temp.Word.LW);

        /* Device ID errata workaround: Save data at any address that has LSB 0x18 */
        if((SourceAddr.Val32 & 0x0000001F) == 0x18)
        {
            TempAddr.Val32 = SourceAddr.Val32;
            TempData.Val32 = Temp.Val32;
        }

        if((Size !=0) && (((Size + 1) % 64) == 0))
        {
                /* Device ID errata workaround: Reload data at address with LSB of 0x18 */
                WriteLatch(TempAddr.Word.HW, TempAddr.Word.LW,TempData.Word.HW,TempData.Word.LW);

                WriteMem(PM_ROW_WRITE);
        }

        SourceAddr.Val32 = SourceAddr.Val32 + 2;
    }
}

/******************************************************************************/




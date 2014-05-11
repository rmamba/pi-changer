/* 
 * File:   bootloader.h
 * Author: rmamba@gmail.com
 * GitHub: https://github.com/rmamba/pi-changer
 *
 * Created on 25 February 2014, 19:08
 */

#ifndef BOOTLOADER_H
#define	BOOTLOADER_H

#ifdef	__cplusplus
extern "C" {
#endif

#define COMMAND_NACK     0x00
#define COMMAND_ACK      0x01
#define COMMAND_READ_PM  0x02
#define COMMAND_WRITE_PM 0x03
#define COMMAND_WRITE_CM 0x07
#define COMMAND_RESET    0x08
#define COMMAND_READ_ID  0x09


#define PM_ROW_SIZE 64 * 8
#define CM_ROW_SIZE 8
#define CONFIG_WORD_SIZE 1

#define PM_ROW_ERASE 		0x4042
#define PM_ROW_WRITE 		0x4001
#define CONFIG_WORD_WRITE	0X4000

#define FCY			4000000				//Fosc/2
#define BAUDRATE		9600
#define BRGVAL			((FCY/BAUDRATE)/16)-1

typedef short          Word16;
typedef unsigned short UWord16;
typedef long           Word32;
typedef unsigned long  UWord32;

typedef union tuReg32
{
    UWord32 Val32;
    struct
    {
            UWord16 LW;
            UWord16 HW;
    } Word;
    char Val[4];
} uReg32;

extern UWord32 ReadLatch(UWord16, UWord16);
void PutChar(char);
void GetChar(char *);
void WriteBuffer(char *, int);
void ReadPM(char *, uReg32);
void WritePM(char *, uReg32);

#ifdef	__cplusplus
}
#endif

#endif	/* BOOTLOADER_H */


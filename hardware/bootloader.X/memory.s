/*
 * File:   memory.s
 * Author: rmamba@gmail.com
 * GitHub: https://github.com/rmamba/pi-changer
 *
 * Created on 25 February 2014, 19:08
 *
 * Based on source from Microchip Inc. but modified for PIC24FJ64GB004 microcontroller
 * Source: http://www.microchip.com/stellent/idcplg?IdcService=SS_GET_PAGE&nodeId=1824&appnote=en530200
 */

.include "p24Fxxxx.inc"

.global _LoadAddr,_WriteMem,_WriteLatch,_ReadLatch,_ResetDevice,_Erase ;C called

_LoadAddr:      ;W0=NVMADRU,W1=NVMADR - no return values
	mov	W0,TBLPAG
	mov	W1,W1
	return
;***************************************************************		
_WriteMem:      ;W0=NVMCON - no return values
	mov	W0,NVMCON
	mov	#0x55,W0	;Unlock sequence - interrupts need to be off
	mov	W0,NVMKEY
	mov	0xAA,W0
	mov	W0,NVMKEY
	bset NVMCON,#WR
	nop				;Required
	nop
1:	btsc NVMCON,#WR	;Wait for write end
	bra 1b
	return
;***************************************************************	
_WriteLatch:    ;W0=TBLPAG,W1=Wn,W2=WordHi,W3=WordLo - no return values
	mov	W0,TBLPAG	
	tblwtl W3,[W1]
	tblwth W2,[W1]
	return
;***************************************************************	
_ReadLatch:     ;W0=TBLPAG,W1=Wn - data in W1:W0
	mov	W0,TBLPAG	
	tblrdl [W1],W0
	tblrdh [W1],W1
	return
;***************************************************************
_ResetDevice:
    goto 0xc02
    return
;***************************************************************
_Erase:	
	push    TBLPAG
	mov     W2,NVMCON
	mov     w0,TBLPAG           	; Init Pointer to page to be erased
	tblwtl  w1,[w1]		        	; Dummy write to select the row
	mov     #0x55,W0	                ; Unlock sequence - interrupts need to be off
	mov     W0,NVMKEY
	mov     #0xAA,W0
	mov     W0,NVMKEY
	bset    NVMCON,#WR
	nop                             ;Required
	nop
erase_wait:
	btsc    NVMCON,#WR                 ;Wait for write end
	bra     erase_wait
	pop     TBLPAG
	return
;***************************************************************	
.end

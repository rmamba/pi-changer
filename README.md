pi-changer
==========
Expansion I/O board for RaspberryPI

Components description
==========
* PIC24FJ64GB004 microcontroller  
  * DIN13 round connector for car stereo connection/power  
  * Connector for LCD with HD44780 controller  
  * Rotary encoder  
* Stereo audio amplifier  
* 5.5mm power connector  
* On/Off switch  
* 800mA LDO or external SMPS module for 3 or 5A  
* USB hub with 5 ports on PCB and 2 header connectors (same pinout as motherboards)  
* rPi Expansion headers  
  * 3x I2C header connector  
  * SPI connector with two CS signals  
  * RS232 connector  

BOM
==========
|Designator|Footprint|Value|Quantity
|---|---|---|---
|C1, C4, C18, C20, C21|C0805|0.1uF|5
|C2, C3|C0805|0.39uF|2
|C5|CAPR5-4X5|4.7uF|1
|C6|CAPR5-4X5|10uF|1
|C7, C8|C1206|0.1uF|2
|C9, C12|C0805|0.1uF|2
|C10, C13|CAPR5-4X5|470uF|2
|C11|CAPPR5-5x11|470uF|1
|C14|C0805|100nF|1
|C15|CAPR5-4X5|4.7uF|1
|C16, C17|C1206|390nF|2
|C19|C0805|100nF|1
|C22, C23, C24, C25|C0805|18pF|4
|D1|SOT-23B_N||1
|DIN13|DIN13||1
|I2C_1, I2C_2, LEDs|HDR2X4||3
|JP1, JP2, JP3, JP4, JP5|6-0805_N|0E|5
|LCD/IO|HDR1X16||1
|P1|POT4MM-2||1
|P2|POT4MM-2||1
|POWER1|LUMBERG_1613-14||1
|POWER2|NAP2||1
|Q1, Q2|318-08||2
|R1, R2|6-0805_N|2.7E|2
|R3, R8, R11|6-0805_N|10k|3
|R4|6-0805_N|0E|1
|R5|6-0805_N|1k|1
|R6, R9|6-0805_N|680E|2
|R7, R10|6-0805_N|100k|2
|R12, R13, R14, R15|6-0805_L|470E|4
|R16, R21, R22|6-0805_N|1k|3
|R17|6-0805_N|2k7|1
|R18|6-0805_L|1k5|1
|R19|6-0805_N|47k|1
|R20|6-0805_N|330E|1
|R23, R24|6-0805_N|1k|2
|R25, R26|6-0805_N|18G|2
|Rotary|EC11 (ALPS)||1
|rPi|HDR2x13||1
|RST, USB_IN|HDR1X2||2
|SND1|HDR1X3||1
|SPI1|HDR2X5||1
|SW1|Stikalo_dvojno_200x200||1
|U1|TS9A_N||1
|U2|ZZ311||1
|U3|T03B||1
|U4, U5|SSOP-28_N||2
|U6|TQFP-PT44_L||1
|USB0, USB1, USB2|440260||3
|USB3, USB4|787616||2
|USB56|440264||1
|USBH|USB_HEADER||1
|USB_HUB|440247||1
|X1, X2|RESC6332||2

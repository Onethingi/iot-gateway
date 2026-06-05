#ifndef CAN_FRAME_H
#define CAN_FRAME_H

#include <stdint.h>

typedef struct {
    uint16_t id;        
    uint8_t  dlc;       
    uint8_t  data[8];  
} CANFrame_t;

// Node IDs
#define CAN_ID_ENGINE      0x100   
#define CAN_ID_BODY        0x200   
#define CAN_ID_DASHBOARD   0x300   

#endif
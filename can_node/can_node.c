#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <time.h>

#include "FreeRTOS_Source/include/FreeRTOS.h"
#include "FreeRTOS_Source/include/task.h"
#include "FreeRTOS_Source/include/queue.h"
#include "can_frame.h"

#define SOCKET_PATH "/tmp/can_bus.sock"
#define STACK_SIZE  2048


static QueueHandle_t canBusQueue;

void send_to_socket(CANFrame_t *frame) {
    int sock = socket(AF_UNIX, SOCK_DGRAM, 0);
    if (sock < 0) return;

    struct sockaddr_un addr;
    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;
    strncpy(addr.sun_path, SOCKET_PATH, sizeof(addr.sun_path) - 1);

    sendto(sock, frame, sizeof(CANFrame_t), 0,
           (struct sockaddr*)&addr, sizeof(addr));
    close(sock);
}

void EngineTask(void *pvParameters) {
    CANFrame_t frame;
    frame.id  = CAN_ID_ENGINE;
    frame.dlc = 2;

    while (1) {
        
        uint16_t temp = 200 + (rand() % 700);
        frame.data[0] = (temp >> 8) & 0xFF;
        frame.data[1] =  temp       & 0xFF;

        xQueueSend(canBusQueue, &frame, 0);
        printf("[Engine   ] CAN ID: 0x%03X | Temp: %.1f C\n",
               frame.id, temp / 10.0);

        vTaskDelay(pdMS_TO_TICKS(1000));   // 1s periodic
    }
}

void BodyTask(void *pvParameters) {
    CANFrame_t frame;
    frame.id  = CAN_ID_BODY;
    frame.dlc = 2;

    while (1) {
        uint16_t humidity = 300 + (rand() % 500);
        frame.data[0] = (humidity >> 8) & 0xFF;
        frame.data[1] =  humidity       & 0xFF;

        xQueueSend(canBusQueue, &frame, 0);
        printf("[Body     ] CAN ID: 0x%03X | Humidity: %.1f%%\n",
               frame.id, humidity / 10.0);

        vTaskDelay(pdMS_TO_TICKS(2000));   // 2s periodic
    }
}

void DashboardTask(void *pvParameters) {
    CANFrame_t frame;
    frame.id  = CAN_ID_DASHBOARD;
    frame.dlc = 2;

    while (1) {
        uint16_t pressure = 100 + (rand() % 400);
        frame.data[0] = (pressure >> 8) & 0xFF;
        frame.data[1] =  pressure       & 0xFF;

        xQueueSend(canBusQueue, &frame, 0);
        printf("[Dashboard] CAN ID: 0x%03X | Pressure: %.2f bar\n",
               frame.id, pressure / 100.0);

        vTaskDelay(pdMS_TO_TICKS(3000));   
    }
}

void BusMonitorTask(void *pvParameters) {
    CANFrame_t frame;

    while (1) {
        if (xQueueReceive(canBusQueue, &frame, pdMS_TO_TICKS(500))) {
            send_to_socket(&frame);
        }
    }
}

int main(void) {
    srand(time(NULL));

    canBusQueue = xQueueCreate(20, sizeof(CANFrame_t));

    xTaskCreate(EngineTask,    "Engine",    STACK_SIZE, NULL, 3, NULL);
    xTaskCreate(BodyTask,      "Body",      STACK_SIZE, NULL, 2, NULL);
    xTaskCreate(DashboardTask, "Dashboard", STACK_SIZE, NULL, 1, NULL);
    xTaskCreate(BusMonitorTask,"BusMonitor",STACK_SIZE, NULL, 2, NULL);

    printf("[CAN Node] Starting RTOS scheduler...\n");
    vTaskStartScheduler();

    return 0;
}
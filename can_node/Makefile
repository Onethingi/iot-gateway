CC      = gcc
CFLAGS  = -I. -IFreeRTOS_Source/include \
          -IFreeRTOS_Source/portable/ThirdParty/GCC/Posix \
          -IFreeRTOS_Source/portable/ThirdParty/GCC/Posix/utils \
          -DprojCOVERAGE_TEST=0 \
          -D_WINDOWS_=0

FREERTOS_SRC = \
    FreeRTOS_Source/tasks.c \
    FreeRTOS_Source/queue.c \
    FreeRTOS_Source/list.c \
    FreeRTOS_Source/timers.c \
    FreeRTOS_Source/portable/ThirdParty/GCC/Posix/port.c \
    FreeRTOS_Source/portable/ThirdParty/GCC/Posix/utils/wait_for_event.c \
    FreeRTOS_Source/portable/MemMang/heap_3.c

all:
	$(CC) $(CFLAGS) can_node.c $(FREERTOS_SRC) -o can_node -lpthread

clean:
	rm -f can_node
/* AVR host: runs the REAL compiled Arduino firmware on an emulated ATmega328P (simavr),
   exposes UART0 on a TCP socket (115200 8N1) and logs PB5 (Pin 13) / PB4 (Pin 12) edges. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <time.h>
#include <fcntl.h>
#include <errno.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include "sim_avr.h"
#include "sim_elf.h"
#include "avr_ioport.h"
#include "avr_uart.h"
#include "sim_irq.h"

static avr_t *avr;
static int cfd = -1;
static FILE *plog;

static void pin_cb(avr_irq_t *irq, uint32_t value, void *param) {
    fprintf(plog, "%s %.6f %u\n", (const char *)param, (double)avr->cycle / avr->frequency, value);
    fflush(plog);
}
static void uart_out_cb(avr_irq_t *irq, uint32_t value, void *param) {
    if (cfd >= 0) { unsigned char b = value; if (write(cfd, &b, 1) < 0) {} }
}
static double now_s(void) { struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return t.tv_sec + t.tv_nsec / 1e9; }

int main(int argc, char **argv) {
    if (argc < 4) { fprintf(stderr, "usage: host firmware.elf tcp_port pinlog.txt\n"); return 1; }
    elf_firmware_t fw; memset(&fw, 0, sizeof fw);
    if (elf_read_firmware(argv[1], &fw)) { fprintf(stderr, "cannot read elf\n"); return 1; }
    avr = avr_make_mcu_by_name("atmega328p"); avr_init(avr);
    avr_load_firmware(avr, &fw); avr->frequency = 16000000;
    plog = fopen(argv[3], "w");

    avr_irq_register_notify(avr_io_getirq(avr, AVR_IOCTL_IOPORT_GETIRQ('B'), 5), pin_cb, "P13");
    avr_irq_register_notify(avr_io_getirq(avr, AVR_IOCTL_IOPORT_GETIRQ('B'), 4), pin_cb, "P12");

    uint32_t flags = 0;
    avr_ioctl(avr, AVR_IOCTL_UART_GET_FLAGS('0'), &flags);
    flags &= ~AVR_UART_FLAG_STDIO; avr_ioctl(avr, AVR_IOCTL_UART_SET_FLAGS('0'), &flags);
    avr_irq_t *uin  = avr_io_getirq(avr, AVR_IOCTL_UART_GETIRQ('0'), UART_IRQ_INPUT);
    avr_irq_register_notify(avr_io_getirq(avr, AVR_IOCTL_UART_GETIRQ('0'), UART_IRQ_OUTPUT), uart_out_cb, NULL);

    int srv = socket(AF_INET, SOCK_STREAM, 0), one = 1;
    setsockopt(srv, SOL_SOCKET, SO_REUSEADDR, &one, sizeof one);
    struct sockaddr_in a = { .sin_family = AF_INET, .sin_port = htons(atoi(argv[2])), .sin_addr.s_addr = htonl(INADDR_LOOPBACK) };
    if (bind(srv, (void *)&a, sizeof a) || listen(srv, 1)) { perror("bind"); return 1; }
    fcntl(srv, F_SETFL, O_NONBLOCK);
    fprintf(stderr, "simavr: ATmega328P @16MHz running %s, UART0 on tcp://127.0.0.1:%s\n", argv[1], argv[2]);

    unsigned char q[512]; int qn = 0, qi = 0; avr_cycle_count_t next_feed = 0;
    const avr_cycle_count_t per_byte = 16000000UL / 115200 * 10;
    double t0 = now_s();
    for (;;) {
        double target = (now_s() - t0) * avr->frequency;
        while ((double)avr->cycle < target) {
            int st = avr_run(avr);
            if (st == cpu_Done || st == cpu_Crashed) return 0;
            if (qi < qn && avr->cycle >= next_feed) { avr_raise_irq(uin, q[qi++]); next_feed = avr->cycle + per_byte; if (qi == qn) qi = qn = 0; }
        }
        if (cfd < 0) { cfd = accept(srv, NULL, NULL); if (cfd >= 0) fcntl(cfd, F_SETFL, O_NONBLOCK); }
        else if (qn < (int)sizeof q - 64) {
            ssize_t n = read(cfd, q + qn, sizeof q - qn);
            if (n > 0) qn += n; else if (n == 0) { close(cfd); cfd = -1; }
        }
        usleep(300);
    }
}

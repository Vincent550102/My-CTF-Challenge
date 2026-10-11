#include <fcntl.h>
#include <stdio.h>
#include <unistd.h>

int main(void) {
    char buf[4096];
    ssize_t n;
    int fd;

    if (setgid(0) != 0 || setuid(0) != 0) {
        perror("setuid");
        return 1;
    }

    fd = open("/flag", O_RDONLY);
    if (fd < 0) {
        perror("open");
        return 1;
    }

    while ((n = read(fd, buf, sizeof(buf))) > 0) {
        if (write(STDOUT_FILENO, buf, (size_t)n) != n) {
            perror("write");
            close(fd);
            return 1;
        }
    }

    close(fd);
    return n < 0;
}

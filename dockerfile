FROM ubuntu:22.04

RUN apt update && apt install -y openssh-server sudo curl iputils-ping && \
    useradd -m vpsuser && echo "vpsuser:password123" | chpasswd && \
    mkdir /var/run/sshd

EXPOSE 22 80 443 8080 2022 5080 3001

CMD ["/usr/sbin/sshd", "-D"]

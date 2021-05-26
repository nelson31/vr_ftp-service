FROM ubuntu:20.04

# Atualizar os pacotes
RUN apt-get update &&\
 apt-get install -y software-properties-common &&\
 add-apt-repository universe &&\
 apt-get install -y php-apcu

# Instalar as dependencias necessarias
RUN apt-get install -y python3.7
RUN apt-get install -y python3-pip
RUN pip3 install pyftpdlib
RUN pip3 install pyjwt
RUN pip3 install requests

# Pacotes adicionais
RUN apt-get install -y iputils-ping
RUN apt-get install -y net-tools

# Copiar esta o conteudo desta diretoria para o container
COPY . ftp-server/

# Correr o ftp
CMD [ "python3", "ftp-server/appftp.py" ]

# Expor uma porta
EXPOSE 2121

  

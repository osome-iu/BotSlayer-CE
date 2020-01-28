FROM library/postgres:11.5

# set system locale
ENV LANG C.UTF-8

# system dependencies
##### add testing source for python3.7
RUN echo "deb http://ftp.de.debian.org/debian testing main" | \
        tee -a /etc/apt/sources.list && \
    apt-get -qq update && \
    apt-get install -y curl gnupg vim build-essential supervisor libcairo2-dev pkg-config libgirepository1.0-dev && \
    apt-get -t testing install -y python3.7 python3.7-dev python3.7-distutils openssl libssl-dev && \
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3.7 get-pip.py && rm get-pip.py && \
    python3 --version && python3.7 --version && which pip3

# install nodejs and npm
RUN curl -sL https://deb.nodesource.com/setup_12.x | bash -
RUN apt-get -y install nodejs && node -v && npm -v

# obtain source code
RUN apt-get install -y git && \
    git clone https://github.com/IUNetSci/BotSlayer-CE.git --single-branch --branch major_update /root/bev && \
    # REMOVE GIT FROM IMAGE
    apt-get purge -y git

# install requirements
WORKDIR /root/bev/backend/
RUN pip3 install -r requirements.txt

# link install backend
WORKDIR /root/bev/backend/bev_backend
RUN pip3 install -e . && python3 -m spacy download en

# build and install frontends
WORKDIR /root/bev/frontend
RUN ln -s /root/bev/frontend/dist /root/bev/middleware/frontend && \
    npm -v && nodejs -v && \
    npm install && npm run build && npm i frontail -g

# prepare entrypoint and configure system
WORKDIR /root/bev
RUN cp backend/bev_backend/bev_backend/database/psql/create_table.sql /docker-entrypoint-initdb.d/
RUN cp supervisord.conf /etc/supervisor/conf.d/supervisord.conf
ENV POSTGRES_USER bev
ENV POSTGRES_PASSWORD bev
ENV POSTGRES_DB bev
ENTRYPOINT ["/usr/bin/supervisord"]
EXPOSE 5432
EXPOSE 5000
EXPOSE 9001
EXPOSE 9002

FROM library/postgres

# system dependencies
RUN apt-get -qq update
RUN apt-get install -y python3 python3-dev python3-pip git vim curl build-essential openssl libssl-dev supervisor unzip

# install nodejs and npm
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.34.0/install.sh | bash
RUN /bin/bash -c "source ~/.bashrc && nvm install node 12.4"

# obtain source code
RUN git clone https://github.com/IUNetSci/BotSlayer-CE.git /root/bev 
# REMOVE GIT FROM IMAGE
RUN apt-get purge -y git

# link install backend
WORKDIR /root/bev/backend/bev_backend
RUN pip3 install -e .

# install middleware
WORKDIR /root/bev/middleware
RUN pip3 install -r requirements.txt && ln -s ../frontend/dist frontend

# build and install frontends
WORKDIR /root/bev/frontend
RUN /bin/bash -c "source ~/.bashrc \
    && npm install && npm run build \
    && npm i frontail -g"

# prepare entrypoint and configure system
WORKDIR /root/bev
run cp backend/bev_backend/bev_backend/database/psql/create_table.sql /docker-entrypoint-initdb.d/
run cp supervisord.conf /etc/supervisor/conf.d/supervisord.conf
ENV POSTGRES_USER bev
ENV POSTGRES_PASSWORD bev
ENV POSTGRES_DB bev
ENTRYPOINT ["/usr/bin/supervisord"]
EXPOSE 5432
EXPOSE 5000
EXPOSE 9001

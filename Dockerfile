FROM programmingerror/ultroid:b0.1

ENV TZ=Asia/Kolkata
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN git clone https://github.com/idzero23/SakuraUserbot.git /root/levina-lab/
WORKDIR /root/idzero23/

COPY requirements.txt /deploy/
RUN pip3 install --no-cache-dir -r /deploy/requirements.txt

RUN wget -O /deploy/addons.txt https://git.io/J8UCB
RUN pip3 install --no-cache-dir -r /deploy/addons.txt

CMD ["bash", "resources/startup/startup.sh"]

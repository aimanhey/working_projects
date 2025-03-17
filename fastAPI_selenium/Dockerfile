FROM python:3.10

#FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

COPY requirements.txt .

COPY ./gambar /gambar/

RUN mkdir gambar1

RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -

RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'

RUN apt-get -y update

RUN apt-get install -y google-chrome-stable -f

# install chromedriver
RUN apt-get install -yqq unzip

RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip

RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

COPY chromedriver .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

RUN pip install "uvicorn[standard]"

COPY ./app /app/

CMD  ["uvicorn", "app.selenium:app","--proxy-headers", "--host", "0.0.0.0","--port","80" ,"--workers", "4","--timeout-keep-alive","300"]
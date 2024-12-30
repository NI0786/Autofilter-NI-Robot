FROM python:3.12-slim
WORKDIR /Autofilter-NI-Robot 
COPY . /Autofilter-NI-Robot 
RUN pip install --upgrade pip \
    && pip install -r requirements.txt
EXPOSE 8080
CMD ["python", "bot.py"]

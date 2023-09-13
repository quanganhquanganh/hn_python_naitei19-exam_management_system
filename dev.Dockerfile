FROM lambci/lambda:build-python3.8
ENV PYTHONUNBUFFERED 1
RUN yum install -y mariadb-devel

COPY requirements/dev.txt /code/requirements.txt

RUN --mount=dst=/root/.cache/pip,type=cache pip install --upgrade pip \
  && pip install --no-deps -r /code/requirements.txt

COPY . /var/task

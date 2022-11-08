FROM python:3.8


# Step 1: Install any Python packages
# ----------------------------------------

ENV PYTHONUNBUFFERED 1
RUN mkdir /var/app
WORKDIR  /var/app
COPY requirements.txt /var/app/requirements.txt
RUN pip install -r requirements.txt

# Step 2: Copy Django Code
# ----------------------------------------

COPY . /var/app/.

EXPOSE 8000

CMD ["python", "manage.py", "migrate"]
CMD ["python", "manage.py", "collectstatic", "--no-input"]
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "game.asgi:application"]

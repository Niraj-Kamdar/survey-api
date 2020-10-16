FROM python:3.8
RUN pip install pipenv
EXPOSE 80
COPY ./ ./
RUN pipenv install
CMD ["pipenv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
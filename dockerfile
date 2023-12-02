FROM python:3.9

# 
WORKDIR /python-news

# 
COPY ./ /python-news/



# 
RUN pip install --no-cache-dir --upgrade -r /python-news/requirements.txt

COPY ./app /python-news/app

# 
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
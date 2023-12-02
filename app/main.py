from pipes import quote
from fastapi import FastAPI, Request, Depends, requests
import pandas as pd
import requests
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
from bs4 import BeautifulSoup
import csv


# Increase CSV field size limit to accommodate large content
csv.field_size_limit(131072 * 10)

# Initialize FastAPI and templates
app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Define the endpoint to retrieve community posts from a CSV file
@app.get("/", response_class=HTMLResponse)
def get_community_posts(request: Request):
    csv_file_path = "posts_data.csv"
    csv_columns = ["title", "link", "author", "date", "content"]

    posts_data = []
    try:
        with open(csv_file_path, mode="r", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file, fieldnames=csv_columns)
            next(reader)  # Skip the first row (headers)
            posts_data = [row for row in reader]
    except FileNotFoundError:
        return templates.TemplateResponse("index.html", {"request": request, "posts": []})

    return templates.TemplateResponse("index.html", {"request": request, "posts": posts_data})

# Define the endpoint to retrieve a specific post by ID
@app.get("/post/{post_id}", response_class=HTMLResponse)
def get_post(request: Request, post_id: int):
    csv_file_path = "posts_data.csv"
    csv_columns = ["title", "link", "author", "date", "content"]

    try:
        with open(csv_file_path, mode="r", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file, fieldnames=csv_columns)
            next(reader)  # Skip the first row (headers)
            posts_data = [row for row in reader]
    except FileNotFoundError:
        return templates.TemplateResponse("post.html", {"request": request, "post": None})

    if 0 <= post_id < len(posts_data):
        post = posts_data[post_id]
        return templates.TemplateResponse("post.html", {"request": request, "post": post})

    return templates.TemplateResponse("post.html", {"request": request, "post": None})

# Define the endpoint to scrape community posts from a website and save them to a CSV file
@app.get("/get_community_posts", response_class=HTMLResponse)
def get_community_posts(request: Request):
    global posts_data
    url = "https://huggingface.co/blog/community"

    response = requests.get(url)
    html_content = response.content

    soup = BeautifulSoup(html_content, "html.parser")
    post_elements = soup.find_all("a", class_="flex flex-col rounded-xl border bg-white px-3 py-2 hover:bg-gray-100 dark:hover:bg-gray-900 border-0")

    posts_data = []
    for element in post_elements:
        title = element.find("h4").text.strip()
        link = element["href"]
        author = element.find("object").find("a").text.strip()
        date = element.find("time")["datetime"]

        # Scrape the content of each post
        post_url = f"https://huggingface.co{link}"
        post_response = requests.get(post_url)
        post_html_content = post_response.content
        post_soup = BeautifulSoup(post_html_content, "html.parser")
        post_content = str(post_soup.find("main", class_="flex flex-1 flex-col"))

        post_data = {
            "title": title,
            "link": link,
            "author": author,
            "date": date,
            "content": post_content
        }
        posts_data.append(post_data)

    # Save the scraped data to a CSV file
    csv_file_path = "posts_data.csv"
    csv_columns = ["title", "link", "author", "date", "content"]
    with open(csv_file_path, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=csv_columns)
        writer.writeheader()
        for post_data in posts_data:
            writer.writerow(post_data)

    return JSONResponse(content={"message": "Data scraped and saved to CSV"})








if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)






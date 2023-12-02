from pipes import quote
from fastapi import FastAPI, Request
import pandas as pd
import requests
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn
from bs4 import BeautifulSoup
import csv


app = FastAPI()

templates = Jinja2Templates(directory="template")

posts_data = []


# Configuracion CORS
origins = ["*"]  # Agrega los orígenes permitidos aquí

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
def get_community_posts(request: Request):
    global posts_data
    url = "https://huggingface.co/blog/community"

    # Realizar la solicitud HTTP y obtener el contenido de la página
    response = requests.get(url)
    html_content = response.content

    # Parsear el contenido HTML utilizando BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")

    # Encontrar los elementos que contienen la información de las publicaciones
    post_elements = soup.find_all("a", class_="flex flex-col rounded-xl border bg-white px-3 py-2 hover:bg-gray-100 dark:hover:bg-gray-900 border-0")

    # Extraer títulos, enlaces, autores y fechas de las publicaciones
    posts_data = []
    for element in post_elements:
        title = element.find("h4").text.strip()
        link = element["href"]
        author = element.find("object").find("a").text.strip()
        date = element.find("time")["datetime"]

        post_data = {
            "title": title,
            "link": link,
            "author": author,
            "date": date
        }
        posts_data.append(post_data)
    
    
    # Guardar los datos en un archivo CSV
    csv_file_path = "posts_data.csv"
    csv_columns = ["title", "link", "author", "date"]  
    with open(csv_file_path, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=csv_columns)
        writer.writeheader()
        for post_data in posts_data:
            writer.writerow(post_data)   
        
   

    return templates.TemplateResponse("index.html", {"request": request, "posts": posts_data})



@app.get("/post/{post_id}", response_class=HTMLResponse)
def get_post_content(request: Request, post_id: str):
    global posts_data
    post = next((p for p in posts_data if p['link'] == f"/blog{post_id}"), None)

    if post:
        post_url = f"https://huggingface.co{post['link']}"
        response = requests.get(post_url)

        if response.status_code == 200:
            html_content = response.content

            soup = BeautifulSoup(html_content, "html.parser")
            post_content = soup.find("main", class_="flex flex-1 flex-col")

            return templates.TemplateResponse("post.html", {"request": request, "post_content": str(post_content)})
    return HTMLResponse(content="Post not found", status_code=404)






if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)






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
import replicate
import os




# Increase CSV field size limit to accommodate large content
csv.field_size_limit(131072 * 10)


# Initialize FastAPI and templates
app = FastAPI()
templates = Jinja2Templates(directory="templates")





# Define the endpoint to retrieve community posts from a CSV file
@app.get("/", response_class=HTMLResponse)
def get_community_posts(request: Request):
    csv_file_path = "posts_data.csv"
    csv_columns = ["title", "link", "author", "date", "content","summary"]

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


@app.get("/summary/{post_id}", response_class=HTMLResponse)
async def get_summary(request: Request, post_id: int):
    # Lee los datos desde el archivo CSV
    csv_file_path = "posts_data.csv"
    csv_columns = ["title", "link", "author", "date", "content", "clean_content", "summary"]

    try:
        with open(csv_file_path, mode="r", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file, fieldnames=csv_columns)
            next(reader)  # Saltar la primera fila (encabezados)
            posts_data = list(reader)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="CSV file not found")

    # Verifica si el ID del post está dentro de los límites
    if 0 <= post_id < len(posts_data):
        post = posts_data[post_id]
        return templates.TemplateResponse("summary.html", {"request": request, "post": post})

    # Lanza una excepción HTTP 404 si el ID del post está fuera de los límites
    raise HTTPException(status_code=404, detail="Post not found")


# Función para limpiar el contenido HTML
def clean_html(html_content):
    # Implementa la lógica para limpiar el contenido HTML según tus necesidades
    # Puedes usar bibliotecas como BeautifulSoup u otras herramientas de procesamiento de texto
    # En este ejemplo, simplemente se eliminan las etiquetas HTML
    clean_text = BeautifulSoup(html_content, "html.parser").text
    return clean_text

# Define el endpoint para scrapear publicaciones de la comunidad desde un sitio web y guardarlas en un archivo CSV
@app.get("/get_community_posts", response_class=HTMLResponse)
def get_community_posts(request: Request):
    global posts_data
    url = "https://huggingface.co/blog/community"
    
    load_dotenv()
    replicate_api_token = os.environ.get("REPLICATE_API_TOKEN")

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

        # Scrape el contenido de cada publicación y límpielo
        post_url = f"https://huggingface.co{link}"
        post_response = requests.get(post_url)
        post_html_content = post_response.content
        post_soup = BeautifulSoup(post_html_content, "html.parser")
        post_content = str(post_soup.find("main", class_="flex flex-1 flex-col"))

        # Limpieza de datos: Eliminar etiquetas HTML y otros elementos no textuales
        clean_content = clean_html(post_content)

        # Usa el modelo de replicate para generar texto basado en el contenido limpio
        # Prompts
        pre_prompt = "create a summary shorty in spanish."
        prompt_input = title

        # Generate LLM response
        output = replicate.run("meta/llama-2-13b-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5", # LLM model
                        input={"prompt": f"{pre_prompt} {prompt_input} Assistant: ", # Prompts
                        "temperature":0.1, "top_p":0.9, "max_length":128, "repetition_penalty":1})
        
        generated_text = ""
        for item in output:
            generated_text += item
         
        

    
        post_data = {
            "title": title,
            "link": link,
            "author": author,
            "date": date,
            "content": post_content,  # Mantén el contenido original
            "clean_content": clean_content,  # Nuevo campo con el contenido limpio
            "summary": generated_text,  # Nuevo campo con el resumen
        }
        posts_data.append(post_data)

    # Guarda los datos scrapeados, limpios y resumidos en un archivo CSV
    csv_file_path = "posts_data.csv"
    csv_columns = ["title", "link", "author", "date", "content", "clean_content", "summary"]
    with open(csv_file_path, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=csv_columns)
        writer.writeheader()
        for post_data in posts_data:
            writer.writerow(post_data)

    return JSONResponse(content={"message": "Data scraped, cleaned, and summarized, and saved to CSV"})







if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)






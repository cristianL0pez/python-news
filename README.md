# Community Posts Web Scraper

This FastAPI application provides an interface to retrieve and display community posts from a CSV file and scrape new posts from a website.

## Features

- **Get Community Posts**: Retrieve a list of community posts from a CSV file.
- **Get Specific Post**: Retrieve the details of a specific post by its ID.
- **Scrape Community Posts**: Scrape new community posts from a website and save them to a CSV file.

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/cristianL0pez/python-news.git
    ```

2. **Install the required dependencies:**
   
    ```bash
    pip install -r requirements.txt
    ```

3. **Run the FastAPI application:**
   
    ```bash
    uvicorn main:app --reload
    ```

   The application will be running at [http://127.0.0.1:8000](http://127.0.0.1:8000).

## Usage

- **Get Community Posts**: Open your browser and go to [http://127.0.0.1:8000/](http://127.0.0.1:8000/).
- **Get Specific Post**: Replace `{post_id}` with the desired post ID in the URL [http://127.0.0.1:8000/post/{post_id}](http://127.0.0.1:8000/post/{post_id}).
- **Scrape Community Posts**: Open your browser and go to [http://127.0.0.1:8000/get_community_posts](http://127.0.0.1:8000/get_community_posts).

## Code Snippets

### Get Community Posts

    ```python
    # FastAPI endpoint to retrieve community posts from a CSV file
    @app.get("/", response_class=HTMLResponse)
    def get_community_posts(request: Request):
        # ... (your code snippet)

    # FastAPI endpoint to scrape community posts from a website and save them to a CSV file
    @app.get("/get_community_posts", response_class=HTMLResponse)
    def get_community_posts(request: Request):
        # ... (your code snippet)



## Dependencies
- Jinja2
- Requests
- Beautiful Soup
- FastAPI
License
This project is licensed under the MIT License - see the LICENSE file for details.
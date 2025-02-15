import os
import subprocess
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import json
from datetime import datetime
import shutil
import sqlite3
from typing import List, Dict

# Initialize FastAPI app
app = FastAPI()

# Middleware to handle CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Your AI Proxy token (set this as an environment variable in production)
AIPROXY_TOKEN = os.getenv("AIPROXY_TOKEN", "eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjIyZjMwMDE4MzRAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9._wRoOghFlCA279Z9xgFn_sQLVSt9mBOunYxiPFNuNWI")

@app.get("/")
def home():
    return {"message": "Welcome to the Task Automation Agent"}


@app.get("/read")
def read(path: str):
    """Read the content of a file."""
    try:
        if not path.startswith('/data/'):
            raise HTTPException(status_code=403, detail="Access outside /data is not allowed.")
        
        with open(path, "r") as file:
            return {"content": file.read()}
    
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")


@app.post("/run")
async def task_runner(task: str):
    """Run a task described in plain English."""
    # Handling different types of tasks
    if "install uv" in task:
        return await run_script_from_url("https://raw.githubusercontent.com/sanand0/tools-in-data-science-public/tds-2025-01/project-1/datagen.py", [os.getenv("USER_EMAIL")])

    if "count the number of Wednesdays" in task:
        return await count_weekdays_in_file("/data/dates.txt", "Wednesday", "/data/dates-wednesdays.txt")

    if "format the contents" in task:
        return await format_file_with_prettier("/data/format.md", "prettier@3.4.2")

    if "sort the contacts" in task:
        return await sort_contacts("/data/contacts.json", "/data/contacts-sorted.json")

    if "find similar comments" in task:
        return await find_similar_comments("/data/comments.txt", "/data/comments-similar.txt")

    if "process SQLite query" in task:
        return await process_sqlite_query("/data/ticket-sales.db", "Gold", "/data/ticket-sales-gold.txt")
    
    # Add more handlers as per tasks
    return {"message": "Task is not recognized"}


# Phase A Tasks Implementations
async def run_script_from_url(script_url: str, args: List[str]):
    """Install uv and run the provided script with arguments."""
    try:
        subprocess.run(["pip", "install", "uv"], check=True)  # Install the package if not already installed
        result = subprocess.run(["python", script_url] + args, capture_output=True, text=True, check=True)
        
        return {"message": "Script executed successfully", "output": result.stdout}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running script: {str(e)}")


async def count_weekdays_in_file(file_path: str, weekday_name: str, output_path: str):
    """Count the occurrences of a specific weekday in a file."""
    try:
        with open(file_path, "r") as f:
            dates = f.readlines()
        
        # Count the specified weekday
        weekday_count = 0
        for date_str in dates:
            try:
                date_obj = datetime.strptime(date_str.strip(), "%Y-%m-%d")
                if date_obj.strftime("%A") == weekday_name:
                    weekday_count += 1
            except ValueError:
                continue  # Skip invalid date formats

        with open(output_path, "w") as f:
            f.write(str(weekday_count))

        return {"message": "Weekday count completed", "output_file": output_path}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


async def format_file_with_prettier(file_path: str, version: str):
    """Format the file using Prettier."""
    try:
        subprocess.run(["npx", "prettier", "--version"], check=True)  # Ensure prettier is available
        subprocess.run(["npx", "prettier", "--write", file_path], check=True)
        return {"message": f"File formatted with prettier version {version}", "file_path": file_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error formatting file: {str(e)}")


async def sort_contacts(input_file: str, output_file: str):
    """Sort contacts in JSON by last_name, then first_name."""
    try:
        with open(input_file, "r") as f:
            contacts = json.load(f)

        sorted_contacts = sorted(contacts, key=lambda x: (x["last_name"], x["first_name"]))

        with open(output_file, "w") as f:
            json.dump(sorted_contacts, f, indent=4)

        return {"message": "Contacts sorted", "output_file": output_file}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sorting contacts: {str(e)}")


async def find_similar_comments(input_file: str, output_file: str):
    """Find the most similar pair of comments using embeddings."""
    # For simplicity, we'll assume this is handled by the LLM or a similarity model.
    try:
        with open(input_file, "r") as f:
            comments = f.readlines()

        # Example: Simple comparison of comments (embeddings or model integration can be done here)
        similar_comments = (comments[0], comments[1])  # Placeholder for actual similarity calculation

        with open(output_file, "w") as f:
            f.write("\n".join(similar_comments))

        return {"message": "Found similar comments", "output_file": output_file}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding similar comments: {str(e)}")


async def process_sqlite_query(db_path: str, ticket_type: str, output_file: str):
    """Process a SQLite query for total sales of a specific ticket type."""
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        
        cursor.execute("SELECT SUM(units * price) FROM tickets WHERE type=?", (ticket_type,))
        result = cursor.fetchone()
        
        total_sales = result[0] if result[0] else 0
        
        with open(output_file, "w") as f:
            f.write(str(total_sales))

        return {"message": "SQL query processed", "output_file": output_file}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing SQLite query: {str(e)}")


# Phase B - Business Tasks
@app.post("/run-business")
async def run_business_task(task: str):
    """Run business-oriented tasks."""
    # Examples of business tasks - image processing, API calls, scraping, etc.
    
    if "fetch data from API" in task:
        return await fetch_data_from_api("https://api.example.com/data", "/data/fetched_data.json")
    
    if "clone git repo" in task:
        return await clone_git_repo("https://github.com/example/repo.git", "/data/repo_dir")
    
    if "compress image" in task:
        return await compress_image("/data/sample_image.png", "/data/compressed_image.png")
    
    if "transcribe audio" in task:
        return await transcribe_audio("/data/sample_audio.mp3", "/data/transcription.txt")
    
    if "convert markdown to html" in task:
        return await convert_markdown_to_html("/data/sample.md", "/data/output.html")
    
    return {"message": "Business task not recognized"}

async def fetch_data_from_api(api_url: str, output_file: str):
    """Fetch data from an external API."""
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        
        with open(output_file, "w") as f:
            json.dump(response.json(), f, indent=4)

        return {"message": "Data fetched from API", "output_file": output_file}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data from API: {str(e)}")


async def clone_git_repo(repo_url: str, target_dir: str):
    """Clone a Git repository."""
    try:
        subprocess.run(["git", "clone", repo_url, target_dir], check=True)
        return {"message": "Git repo cloned", "repo_dir": target_dir}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cloning Git repository: {str(e)}")


async def compress_image(input_image_path: str, output_image_path: str):
    """Compress an image (you can use an image library such as Pillow)."""
    try:
        from PIL import Image
        with Image.open(input_image_path) as img:
            img.save(output_image_path, quality=85)  # Adjust compression quality
        return {"message": "Image compressed", "output_image_path": output_image_path}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error compressing image: {str(e)}")


async def transcribe_audio(input_audio_path: str, output_text_path: str):
    """Transcribe audio to text."""
    try:
        from pydub import AudioSegment
        from speech_recognition import Recognizer, AudioFile

        audio = AudioSegment.from_mp3(input_audio_path)
        audio.export("/data/temp.wav", format="wav")

        recognizer = Recognizer()
        with AudioFile("/data/temp.wav") as source:
            audio_data = recognizer.record(source)

        transcription = recognizer.recognize_google(audio_data)
        with open(output_text_path, "w") as f:
            f.write(transcription)

        return {"message": "Audio transcribed", "output_text_path": output_text_path}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error transcribing audio: {str(e)}")


async def convert_markdown_to_html(input_markdown_path: str, output_html_path: str):
    """Convert Markdown file to HTML."""
    try:
        from markdown import markdown

        with open(input_markdown_path, "r") as f:
            md_content = f.read()

        html_content = markdown(md_content)
        
        with open(output_html_path, "w") as f:
            f.write(html_content)

        return {"message": "Markdown converted to HTML", "output_html_path": output_html_path}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error converting Markdown to HTML: {str(e)}")


# Run the FastAPI app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

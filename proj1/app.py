# ///script
# requires-python = ">=3.13"
# dependencies = [
# "flask",
# "fastapi",
# "requests",
# "uvicorn"
# ]
# ///
import os
from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=['GET','POST'],
    allow_headers=["*"],
)

tools=[
    {
        "type":"function",
        "function":{
            "name":"script_runner",
            "description":"Install a pakage and run a script from a url with provided arguments",
            "parameters":{
                "type":"object",
                "properties":{
                    "script_url":{
                        "type":"string",
                        "description":"URL of the script to be executed."
                    },
                    "args":{
                        "type":"array",
                        "items":{
                            "type":"string"
                        },
                        "description":"Arguments to be passed to the script."
                    }
                },
                "required":["script_url","args"]
            }
        }
    }
]

#AIPROXY_TOKEN =os.getenv("AIPROXY_TOKEN")
AIPROXY_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjIyZjMwMDE4MzRAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9._wRoOghFlCA279Z9xgFn_sQLVSt9mBOunYxiPFNuNWI"
@app.get("/")
def home():
    return {"Hello":"World"}

@app.get("/read")
def read(path:str):
    try:
        with open(path)as f:
            return f.read()
    except Exception as e:
        return HTTPException(status_code=404,detail="File not found")
    
@app.post("/run")
def task_runner(task:str):
    url="https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
    headers={
        "Content-Type":"application/json",
        "Authorization":f"Bearer {AIPROXY_TOKEN}"
    }
    data={
        "model":"gpt-4o-mini",
        "messages":[
            {
                "role":"system",
                "content":"""You are an assistant who has to do a variety of tasks.
                If your task involves running a script, you can use the script_runner tool.
                If your task involves writing a code, you can use the task_runner tool."""
            },
            {
                "role":"user",
                "content":task
            }
        ],
        "tools":"tools",
        "tools_choice":"auto"
    }
    response=requests.post(url,headers=headers,json=data)
    return response.json()



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app,host="0.0.0.0",port=8000)
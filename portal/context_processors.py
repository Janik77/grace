import os
def app_config(request):
    return {"APP_CONFIG": {
        "TRELLO_KEY": os.getenv("TRELLO_KEY", ""),
        "TRELLO_TOKEN": os.getenv("TRELLO_TOKEN", ""),
        "SHEETS_API_KEY": os.getenv("SHEETS_API_KEY", ""),
    }}

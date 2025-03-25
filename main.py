from flask import Flask, render_template
import dropbox
import os
import dotenv

dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)

access_token = os.environ['DROPBOX_ACCESS_CODE']
dropbox_path = '/recognitions.txt'

app = Flask(__name__)

@app.route('/')
def hello():
    # Define the context data
    dbx = dropbox.Dropbox(access_token)
    try:
        metadata, response = dbx.files_download(dropbox_path)
        data = response.content.decode()
        data = data.split('\n')
    except dropbox.exceptions.HttpError as err:
        print(f"Error downloading file: {err}")
    context = {'data': data}
    # Render the index.html template with the provided context
    return render_template('index.html', **context)

if __name__ == '__main__':
    app.run()

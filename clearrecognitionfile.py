import dropbox
import os
import dotenv
dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)

access_token = os.environ['DROPBOX_ACCESS_CODE']

def append_to_file(dropbox_path, new_content):
    dbx = dropbox.Dropbox(access_token)
    try:
        # Download the current content of the file
        # _, existing_content = dbx.files_download(dropbox_path)
        # existing_content_str = existing_content.content.decode()

        # Append the new content
        updated_content = new_content

        # Upload the updated content back to Dropbox
        dbx.files_upload(updated_content.encode(), dropbox_path, mode=dropbox.files.WriteMode('overwrite'))
        print("uploaded to dropbox")
    except dropbox.exceptions.HttpError as err:
        print(f"Error adding new content: {err}")

append_to_file('/recognitions.txt', '')
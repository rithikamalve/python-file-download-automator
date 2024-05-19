import json
import logging
import os
from os import scandir, rename
from os.path import splitext, exists, join
from shutil import move
from time import sleep

import requests
from tqdm import tqdm
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from concurrent.futures import ThreadPoolExecutor

# Load configuration from file
def load_config(config_file):
    with open(config_file, 'r') as file:
        return json.load(file)

config = load_config('config.json')

source_dir = config['source_dir']
dest_dir_sfx = config['dest_dir_sfx']
dest_dir_music = config['dest_dir_music']
dest_dir_video = config['dest_dir_video']
dest_dir_image = config['dest_dir_image']
dest_dir_documents = config['dest_dir_documents']

image_extensions = config['image_extensions']
video_extensions = config['video_extensions']
audio_extensions = config['audio_extensions']
document_extensions = config['document_extensions']

# Ensure directories exist
directories = [
    source_dir,
    dest_dir_sfx,
    dest_dir_music,
    dest_dir_video,
    dest_dir_image,
    dest_dir_documents
]

for directory in directories:
    if not os.path.exists(directory):
        os.makedirs(directory)
        logging.info(f"Created directory: {directory}")

def make_unique(dest, name):
    filename, extension = splitext(name)
    counter = 1
    while exists(f"{dest}/{name}"):
        name = f"{filename}({str(counter)}){extension}"
        counter += 1
    return name

def move_file(dest, entry, name):
    if exists(f"{dest}/{name}"):
        unique_name = make_unique(dest, name)
        oldName = join(dest, name)
        newName = join(dest, unique_name)
        rename(oldName, newName)
    move(entry.path, dest)

class MoverHandler(FileSystemEventHandler):
    def on_modified(self, event):
        with scandir(source_dir) as entries:
            with ThreadPoolExecutor(max_workers=5) as executor:
                for entry in entries:
                    name = entry.name
                    executor.submit(self.process_file, entry, name)

    def process_file(self, entry, name):
        if any(name.endswith(ext) or name.endswith(ext.upper()) for ext in audio_extensions):
            self.check_audio_files(entry, name)
        elif any(name.endswith(ext) or name.endswith(ext.upper()) for ext in video_extensions):
            self.check_video_files(entry, name)
        elif any(name.endswith(ext) or name.endswith(ext.upper()) for ext in image_extensions):
            self.check_image_files(entry, name)
        elif any(name.endswith(ext) or name.endswith(ext.upper()) for ext in document_extensions):
            self.check_document_files(entry, name)

    def check_audio_files(self, entry, name):
        for audio_extension in audio_extensions:
            if name.endswith(audio_extension) or name.endswith(audio_extension.upper()):
                if entry.stat().st_size < 10_000_000 or "SFX" in name:
                    dest = dest_dir_sfx
                else:
                    dest = dest_dir_music
                move_file(dest, entry, name)
                logging.info(f"Moved audio file: {name}")

    def check_video_files(self, entry, name):
        for video_extension in video_extensions:
            if name.endswith(video_extension) or name.endswith(video_extension.upper()):
                move_file(dest_dir_video, entry, name)
                logging.info(f"Moved video file: {name}")

    def check_image_files(self, entry, name):
        for image_extension in image_extensions:
            if name.endswith(image_extension) or name.endswith(image_extension.upper()):
                move_file(dest_dir_image, entry, name)
                logging.info(f"Moved image file: {name}")

    def check_document_files(self, entry, name):
        for documents_extension in document_extensions:
            if name.endswith(documents_extension) or name.endswith(documents_extension.upper()):
                move_file(dest_dir_documents, entry, name)
                logging.info(f"Moved document file: {name}")

def download_file(url, retries=3, delay=5):
    local_filename = url.split('/')[-1]
    for attempt in range(retries):
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            total_size = int(response.headers.get('content-length', 0))
            with open(local_filename, 'wb') as file, tqdm(
                desc=local_filename,
                total=total_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
            ) as bar:
                for data in response.iter_content(chunk_size=1024):
                    file.write(data)
                    bar.update(len(data))
            logging.info(f"Downloaded {url}")
            return
        except requests.RequestException as e:
            logging.error(f"Error downloading {url}: {e}")
            if attempt < retries - 1:
                logging.info(f"Retrying in {delay} seconds...")
                sleep(delay)
            else:
                logging.error("Max retries reached. Skipping.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = source_dir
    event_handler = MoverHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            sleep(10)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

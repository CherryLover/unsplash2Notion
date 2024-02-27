import json
import sys
import os
import random
import requests
import datetime
import time

orientation_list = ["landscape", "portrait", "squarish"]


def prepare_img_dir():
    dir_path = os.path.join(os.getcwd(), "unsplash_img")
    os.makedirs(dir_path, exist_ok=True)
    return dir_path


def download_img_pure(url, file_name):
    img_response = requests.get(url)
    img_file_path = os.path.join(prepare_img_dir(), f"{file_name}.jpg")
    with open(img_file_path, "wb") as img_file:
        img_file.write(img_response.content)
    img_file.close()
    return img_file_path


def download_img(img_id, img_urls):
    prepare_img_dir()
    small_img_url = img_urls['full']

    small_img_response = requests.get(small_img_url)
    small_img_file_path = os.path.join(prepare_img_dir(), f"{img_id}_small.jpg")
    with open(small_img_file_path, "wb") as small_img_file:
        small_img_file.write(small_img_response.content)
    small_img_file.close()

    return {
        "full": small_img_file_path,
        "small": small_img_file_path
    }


def get_random_image(unsplash_key):
    orientation = random.choice(orientation_list)
    url = f'https://api.unsplash.com/photos/random?client_id={unsplash_key}&count=1&orientation={orientation}'
    response = requests.get(url)
    if response.status_code != 200:
        reponse_text = response.text
        raise Exception(f"Unexpected code {response.status_code} {reponse_text}")
    response_text = response.json()
    if len(response_text) == 0:
        raise Exception("No image found")
    img_id = response_text[0]['id']
    img_urls = response_text[0]['urls']
    author = response_text[0]['user']
    author_name = response_text[0]['user']['name']
    count_like = response_text[0]['likes']
    count_download = response_text[0]['downloads']
    share_info = f"Photo by {author['name']} on Unsplash"
    message = f"Likes: {count_like}\nDownloads: {count_download}\n{share_info}"
    link = response_text[0]['links']['html']
    # file_path_map = download_img(img_id, img_urls)
    prompt = response_text[0]['alt_description']

    return {
        # "file_path": file_path_map['small'],
        "file_urls": img_urls,
        "desc": prompt,
        "like": count_like,
        "download": count_download,
        "link": link,
        "author_name": author_name,
    }


# Press the green button in the gutter to run the script.
def create_notion_page(notion_token, notion_db_id, map, page_title):
    url = f"https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Content-Type": "application/json",
        "Notion-Version": "2021-05-13"
    }
    today = datetime.date.today()
    data = {
        "parent": {
            "database_id": notion_db_id
        },
        "cover": {
            "type": "external",
            "external": {
                "url": map["file_urls"]["full"]
            }
        },
        "properties": {
            "Day": {
                "title": [
                    {
                        "text": {
                            "content": page_title
                        }
                    }
                ]
            },
            "Desc": {
                "rich_text": [
                    {
                        "text": {
                            "content": map["desc"]
                        }
                    }
                ]
            },
            "Like": {
                "number": map["like"]
            },
            "Download": {
                "number": map["download"]
            },
            "Link": {
                "url": map["link"]
            }
        }
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    print(response.status_code)
    print(response.text)


if __name__ == '__main__':
    if len(sys.argv) < 4:
        raise Exception("Please input keys")

    unsplash_key = sys.argv[1]
    notion_token = sys.argv[2]
    notion_db_id = sys.argv[3]

    map = get_random_image(unsplash_key)
    create_notion_page(notion_token, notion_db_id, map, str(datetime.date.today()))

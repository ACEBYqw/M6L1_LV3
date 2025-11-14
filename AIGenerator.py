import json
import time
import requests
from config import API_KEY, SECRET_KEY

class FusionBrainAPI:
    def __init__(self, url, api_key, secret_key):
        self.URL = url
        self.AUTH_HEADERS = {
            'X-Key': f'Key {api_key}',
            'X-Secret': f'Secret {secret_key}',
        }

    def get_pipeline(self):
        response = requests.get(self.URL + 'key/api/v1/pipelines', headers=self.AUTH_HEADERS)
        data = response.json()
        return data[0]['id']

    def generate(self, prompt, pipeline, images=1, width=1024, height=1024):
        params = {
            "type": "GENERATE",
            "numImages": images,
            "width": width,
            "height": height,
            "generateParams": {"query": f"{prompt}"}
        }

        data = {
            'pipeline_id': (None, pipeline),
            'params': (None, json.dumps(params), 'application/json')
        }
        response = requests.post(self.URL + 'key/api/v1/pipeline/run', headers=self.AUTH_HEADERS, files=data)
        data = response.json()
        return data['uuid']

    def check_generation(self, request_id, attempts=10, delay=10):
        while attempts > 0:
            response = requests.get(self.URL + 'key/api/v1/pipeline/status/' + request_id, headers=self.AUTH_HEADERS)
            data = response.json()
            if data['status'] == 'DONE':
                return data['result']['files']
            attempts -= 1
            time.sleep(delay)
        return None


def generate_image_from_text(prompt, api_url, api_key, secret_key):
    api = FusionBrainAPI(api_url, api_key, secret_key)
    pipeline_id = api.get_pipeline()
    uuid = api.generate(prompt, pipeline_id)
    files = api.check_generation(uuid)

    if not files:
        print("❌ Görüntü oluşturulamadı.")
        return None

    # 🩵 Eğer sonuç string veya listeyse her ikisini destekle
    image_url = files[0] if isinstance(files, list) else files

    response = requests.get(image_url)  
    if response.status_code == 200: 
        with open("output.png", "wb") as f: 
            f.write(response.content)   
        print("✅ Görüntü kaydedildi: output.png")  
    else:   
        print("❌ Görüntü indirilemedi.")   

    # JSON olarak da kaydet 
    with open("output.json", "w", encoding="utf-8") as f:   
        json.dump(files, f, indent=4, ensure_ascii=False)   

    return image_url    


if __name__ == '__main__':  
    image_link = generate_image_from_text(  
        "A futuristic city at sunset with flying cars", 
        "https://api-key.fusionbrain.ai/",  
        API_KEY,
        SECRET_KEY
    )
    print("Görsel bağlantısı:", image_link)

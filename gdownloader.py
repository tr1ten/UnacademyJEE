import requests
from tqdm import tqdm

def downloadfile(id,path):
    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL,params = { 'id' : id }, stream = True)
    token = get_token(response)
    if token:
        params = {'id' : id , 'confirm' : token }
        response = session.get(URL, params = params, stream = True)

    SaveResponse(response,path)

def get_token(response):
        for key, value in response.cookies.items():
            if key.startswith('download_warning'):
                return value

        return None
def SaveResponse(response,path):
    CHUNK_SIZE = 32768
    with open(path, "wb") as f:
         with tqdm(unit='B', unit_scale=True, unit_divisor=1024) as bar:
            for chunk in response.iter_content(CHUNK_SIZE):
                if chunk:
                    f.write(chunk)
                    bar.update(CHUNK_SIZE)

if __name__ == '__main__':
    downloadfile(input('id :'),input('filename :'))

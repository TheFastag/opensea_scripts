import json
import requests
import webbrowser
import os
from dotenv import load_dotenv

load_dotenv()

# Autenticación de usuario
print("Iniciando sesión en OpenSea...")
auth_url = "https://api.opensea.io/oauth/authorize?client_id={}&redirect_uri={}&response_type=code&scope={}".format(os.getenv("CLIENT_ID"), os.getenv("REDIRECT_URI"), os.getenv("SCOPE"))
webbrowser.open(auth_url)
auth_code = input("Ingresa el código de autenticación: ")

print("Obteniendo token de acceso...")
auth_token_url = "https://api.opensea.io/oauth/token"
auth_token_payload = {
    "client_id": os.getenv("CLIENT_ID"),
    "client_secret": os.getenv("CLIENT_SECRET"),
    "grant_type": "authorization_code",
    "redirect_uri": os.getenv("REDIRECT_URI"),
    "code": auth_code,
    "scope": os.getenv("SCOPE")
}
response = requests.post(auth_token_url, data=auth_token_payload)
access_token = json.loads(response.text)["access_token"]

# Carga de metadata del NFT
with open("nft_metadata.json", "r") as f:
    metadata = json.load(f)

# Carga de imagen del NFT a IPFS
print("Cargando imagen a IPFS...")
image_file = metadata["image"].split("/")[-1]
image_url = metadata["image"]
image_data = requests.get(image_url).content
files = {'file': (image_file, image_data, 'multipart/form-data')}
image_upload_response = requests.post("https://api.pinata.cloud/pinning/pinFileToIPFS", headers={"Authorization": "Bearer {}".format(os.getenv("PINATA_API_KEY"))}, files=files)
image_ipfs_hash = json.loads(image_upload_response.text)["IpfsHash"]
metadata["image"] = "https://ipfs.io/ipfs/{}".format(image_ipfs_hash)

# Creación de NFT en OpenSea
print("Creando NFT en OpenSea...")
url = "https://api.opensea.io/api/v1/assets"
headers = {"Content-Type": "application/json", "Accept": "application/json", "Authorization": "Bearer {}".format(access_token)}
response = requests.post(url, headers=headers, data=json.dumps(metadata))
print(response.text)
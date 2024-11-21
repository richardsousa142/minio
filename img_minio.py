from minio import Minio
from datetime import timedelta
import requests
from fastapi import FastAPI, Depends, HTTPException, Response, Request, status
from sqlmodel import Session, select
from images import Images
from db import create_db_and_tables, get_session
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
import uuid
from images import Images
from sqlmodel import Session, select


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # Permite requisições dessa origem
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos HTTP (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos os cabeçalhos
)

# Create the database tables when the app starts
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/")
async def index(): 
    return {"Hello" : "World"}

@app.post('/signedurl')
async def get_signed_url(request: Request, session: Session = Depends(get_session)):
    # Create a client with the MinIO server playground, its access key
    # and secret key.
    client = Minio(
        #endpoint="console.s3.paas.ic.unicamp.br", 
        endpoint= "s3.paas.ic.unicamp.br",
        access_key="test",
        secret_key="YbAYsTStVhX6Ur2UWPC9jWnZdpPyjFJbZKs0zRGU",
        secure=True
    )
    bucket_name = "test"
        
    if not client.bucket_exists(bucket_name):
        print(f"{bucket_name} não existe")
    
    # ------------------------------- FASE 1 --------------------------------------------
    #receber do front os tipos dos arquivos que serao enviados
    #nao precisa do nome, apenas dos tipos entao filtrar
    data = await request.json()
    extensions = data.get('extensions')
    
    #criar um valor aleatorio para ser o id, esse valor eu vou concatenar com o tipo da 
    #imagem e inserir esses valores no banco de dados
    #e também vou usar esse valor aleatorio concatenado com o tipo
    #e usar para gerar a url assinada
    file_names = {}
    for ext in extensions:
        unique_id = str(uuid.uuid4())       # Gera um UUID aleatório
        file_name = f"{unique_id}.{ext}"    # Concatena o UUID com a extensão
        file_names[unique_id] = file_name   # Armazena no dicionário
    #print(f'\n\n\n{file_names}\n\n\n')

    #* percerrer file_names e inserir no bd
    #* percorrer file_names e gerar a url presigned
    # ** nao é necessario passar um path, apenas o id.tipo no objectname    
    url_presigned = []
    for unique_id, file_name in file_names.items():
        print(f'{unique_id} e {file_name}')
        statement = select(Images).where(Images.id == unique_id)
        image = session.exec(statement).first()

        if image is None:
            new_image = Images(id_image=unique_id, uploaded=False, name_img='')
            session.add(new_image)
            session.commit()
            session.refresh(new_image)
        dict_url_file = {}
        url = client.presigned_put_object(bucket_name, file_name, expires=timedelta(hours=1))
        dict_url_file[file_name] = url
        url_presigned.append(dict_url_file)

    #apos gerar a url pre assinada mandar ela de volta para o front e com isso o front 
    #vai poder realizar o upload do arquivo
    return {"url_presigned": url_presigned}
    
    # ------------------------------- FASE 2 --------------------------------------------
    #apos o processo acima estive pronto, pode-se ir para o proximo level
    #o proximo level seria limitar os tipos de arquivos que o usuario poderia enviar
    
    # ------------------------------- FASE 3 --------------------------------------------
    #limitar o tamanho do arquivo que o usuario pode mandar

    
    
    
    #url_presigned = client.presigned_put_object(bucket_name, object_name, expires=timedelta(hours=1))
@app.post('confirm_upload')
def confirm_upload(request: Request):
    #essa funcao so sera chamada apos receber a confirmaçao que os uploads no front deram certo 
    #receber o nome do arquivo ou seja, id.extensao
    #usar o id para buscar o elemento no banco e modificar o upload para True
    pass

'''
def main():
    # Create a client with the MinIO server playground, its access key
    # and secret key.
    client = Minio(
        #endpoint="console.s3.paas.ic.unicamp.br", 
        endpoint= "s3.paas.ic.unicamp.br",
        access_key="test",
        secret_key="YbAYsTStVhX6Ur2UWPC9jWnZdpPyjFJbZKs0zRGU",
        secure=True
    )

    bucket_name = "test"
    object_name = "img\\minio-logo.jpg"
    file_path = object_name
    
    if not client.bucket_exists(bucket_name):
        print(f"{bucket_name} não existe")
    
    
    url_presigned = client.presigned_put_object(bucket_name, object_name, expires=timedelta(hours=1))
    print(url_presigned)
    
    # Fazer o upload do arquivo usando a URL pré-assinada
    with open(file_path, 'rb') as image_data:
        headers = {"Content-Type": "image/jpeg"}
        response = requests.put(url_presigned, data=image_data, headers=headers)

    # Verificar o status do upload
    if response.status_code == 200:
        print(f"Upload de {object_name} foi bem-sucedido!")
    else:
        print(f"Falha no upload: {response.status_code}")


if __name__ == "__main__":
    try:
        main()
    except KeyError as exc:
        print("error occured", exc)
'''
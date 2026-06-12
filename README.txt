SISTEMA DE DETECÇÃO DE ROSTO - FOTO 3x4
Computação Distribuída

CONCEITOS USADOS:
- API (Django) que recebe o upload e responde em JSON
- Mensageria (RabbitMQ): a imagem entra numa fila para ser processada
- Cache (Redis): guarda o status do processamento

COMO RODAR:

1) Instalar dependencias:
   pip install -r requirements.txt

2) Subir RabbitMQ e Redis:
   docker-compose up -d

3) Criar o banco:
   python manage.py migrate

4) Rodar (2 terminais):
   Terminal 1: python manage.py runserver
   Terminal 2: python consumer.py

5) Abrir no navegador:
   http://localhost:8000

PAINEL DO RABBITMQ:
   http://localhost:15672  (login: guest / senha: guest)

OBS: a imagem precisa ter um rosto humano de frente.

ENDEREÇOS DA API:
   POST /upload/              -> envia a imagem
   GET  /lista/               -> lista as imagens
   GET  /status/<id>/         -> status (tenta o Redis primeiro)

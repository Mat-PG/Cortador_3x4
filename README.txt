Matheus Pereira Garbossa - 1120451

Gabriel Gomes Estery - 1129513

O sistema recebe uma imagem pelo navegador, coloca ela numa fila (RabbitMQ) e um
worker processa em segundo plano: detecta o rosto com OpenCV e gera um recorte
no formato de foto 3x4. O status do processamento é guardado num cache (Redis)
para leitura rápida.

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

Parar:
   docker-compose down

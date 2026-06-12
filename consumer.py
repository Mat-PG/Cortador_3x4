import os
import django
import pika
import cv2
import redis

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.conf import settings
from imagens.models import Imagem


# Conecta no Redis (se nao tiver, segue sem cache)
try:
    cache = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True)
    cache.ping()
except Exception:
    cache = None

# Carrega o detector de rosto que vem com o OpenCV
detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')


# Detecta o rosto e salva a foto recortada em 3x4
def gerar_foto_3x4(entrada, saida):
    imagem = cv2.imread(entrada)
    if imagem is None:
        return False

    cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    rostos = detector.detectMultiScale(cinza, 1.1, 5)
    if len(rostos) == 0:
        return False

    # pega o maior rosto
    x, y, w, h = max(rostos, key=lambda r: r[2] * r[3])

    # margem de 50% em volta do rosto
    mx, my = int(w * 0.5), int(h * 0.5)
    y1 = max(0, y - my)
    y2 = min(imagem.shape[0], y + h + my)
    x1 = max(0, x - mx)
    x2 = min(imagem.shape[1], x + w + mx)
    recorte = imagem[y1:y2, x1:x2]

    # ajusta para proporcao 3x4 (0.75)
    altura, largura = recorte.shape[:2]
    if largura / altura > 0.75:
        nova = int(altura * 0.75)
        corte = (largura - nova) // 2
        recorte = recorte[:, corte:corte + nova]
    else:
        nova = int(largura / 0.75)
        corte = (altura - nova) // 2
        recorte = recorte[corte:corte + nova, :]

    cv2.imwrite(saida, recorte)
    return True


# Chamada para cada imagem que chega na fila
def processar(ch, method, properties, body):
    imagem_id = int(body)
    print('Processando imagem', imagem_id)

    imagem = Imagem.objects.get(id=imagem_id)

    pasta = os.path.join(settings.MEDIA_ROOT, 'processed')
    os.makedirs(pasta, exist_ok=True)
    saida = os.path.join(pasta, f'{imagem_id}.jpg')

    if gerar_foto_3x4(imagem.imagem_original.path, saida):
        imagem.imagem_processada.name = f'processed/{imagem_id}.jpg'
        imagem.rosto_detectado = True
        imagem.status = 'concluido'
    else:
        imagem.status = 'erro'
    imagem.save()

    # guarda o status no Redis
    if cache:
        cache.set(f'status:{imagem_id}', imagem.status)

    print('Status:', imagem.status)
    ch.basic_ack(delivery_tag=method.delivery_tag)


# Conecta no RabbitMQ e fica escutando a fila
credenciais = pika.PlainCredentials('guest', 'guest')
conexao = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5672, credentials=credenciais))
canal = conexao.channel()
canal.queue_declare(queue='fila_imagens', durable=True)
canal.basic_consume(queue='fila_imagens', on_message_callback=processar)

print('Aguardando imagens... (CTRL+C para sair)')
canal.start_consuming()

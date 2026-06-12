import pika
import redis
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from imagens.models import Imagem


# Envia o id da imagem para a fila do RabbitMQ
def enviar_para_fila(imagem_id):
    credenciais = pika.PlainCredentials(settings.RABBITMQ_USER, settings.RABBITMQ_PASS)
    conexao = pika.BlockingConnection(
        pika.ConnectionParameters(settings.RABBITMQ_HOST, settings.RABBITMQ_PORT, credentials=credenciais)
    )
    canal = conexao.channel()
    canal.queue_declare(queue='fila_imagens', durable=True)
    canal.basic_publish(exchange='', routing_key='fila_imagens', body=str(imagem_id))
    conexao.close()


# POST /upload/ - recebe a imagem e manda para a fila
@csrf_exempt
def upload(request):
    if request.method != 'POST':
        return JsonResponse({'erro': 'use POST'}, status=400)

    arquivo = request.FILES.get('imagem')
    if not arquivo:
        return JsonResponse({'erro': 'nenhuma imagem enviada'}, status=400)

    imagem = Imagem.objects.create(imagem_original=arquivo)

    try:
        enviar_para_fila(imagem.id)
    except Exception as e:
        imagem.status = 'erro'
        imagem.save()
        return JsonResponse({'erro': str(e)}, status=500)

    return JsonResponse({'id': imagem.id, 'status': imagem.status})


# GET /lista/ - lista todas as imagens
def lista(request):
    imagens = Imagem.objects.all().order_by('-id')
    dados = []
    for img in imagens:
        dados.append({
            'id': img.id,
            'status': img.status,
            'rosto_detectado': img.rosto_detectado,
            'original': img.imagem_original.url if img.imagem_original else None,
            'processada': img.imagem_processada.url if img.imagem_processada else None,
        })
    return JsonResponse({'imagens': dados})


# GET /status/<id>/ - status da imagem (tenta o Redis primeiro)
def status(request, imagem_id):
    try:
        cache = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True)
        valor = cache.get(f'status:{imagem_id}')
        if valor:
            return JsonResponse({'status': valor, 'fonte': 'redis'})
    except Exception:
        pass

    imagem = Imagem.objects.get(id=imagem_id)
    return JsonResponse({'status': imagem.status, 'fonte': 'banco'})

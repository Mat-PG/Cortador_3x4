from django.db import models


class Imagem(models.Model):
    imagem_original = models.ImageField(upload_to='uploads/')
    imagem_processada = models.ImageField(upload_to='processed/', null=True, blank=True)
    status = models.CharField(max_length=20, default='pendente')
    rosto_detectado = models.BooleanField(default=False)

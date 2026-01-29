from django.db import models

class PedidoAcesso(models.Model):
    texto = models.TextField()
    contem_dados_pessoais = models.BooleanField(default=False)
    analisado = models.BooleanField(default=False)
import csv
from django.core.management.base import BaseCommand
from pedidos.services.ml_model import train_model

class Command(BaseCommand):
    help = "Treina o modelo de detecção de dados pessoais"

    def handle(self, *args, **kwargs):
        texts = []
        labels = []

        with open("ml/dataset.csv", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                texts.append(row["texto"])
                labels.append(int(row["label"]))

        train_model(texts, labels)
        self.stdout.write(self.style.SUCCESS("Modelo treinado com sucesso"))
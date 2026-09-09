from django.db import models

class Pais(models.Model):
    nome = models.CharField(max_length=200)
    sigla = models.CharField(max_length=2)
    class Meta:
        db_table = "pais"
    def __str__(self):
        return self.nome



# Create your models here.
class Estado(models.Model):
    nome = models.CharField(max_length=200)
    sigla = models.CharField(max_length=2)
    pais = models.ForeignKey(Pais, on_delete=models.CASCADE,null=True)
    class Meta:
        db_table = "estado"
    def __str__(self):
        return self.nome
    


class Cidade(models.Model):
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE)
    nome = models.CharField(max_length=200)
    ddd = models.CharField(max_length=3)
    class Meta:
        db_table = "cidade"
    def __str__(self):
        return self.nome


class Campus(models.Model):
    cidade = models.ForeignKey(Cidade, on_delete=models.CASCADE)
    nome = models.CharField(max_length=200)
    class Meta:
        db_table = "campus"
    def __str__(self):
        return self.nome


class Sistema(models.Model):
    STATUS = (("S" , "Sim"),("N", "Não"))
    nome = models.CharField(max_length=200)
    url = models.CharField(max_length=200)
    statusPublico = models.CharField(max_length=1, choices=STATUS)
    class Meta:
        db_table = "sistema"
    def __str__(self):
        return self.nome
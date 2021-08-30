from __future__ import unicode_literals
from django.db import models
from datetime import date
import datetime
import re

def calculate_age(born):
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


class UserManager(models.Manager):
    def validador_basico(self, postData):
        EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
        SOLO_LETRAS = re.compile(r'^[a-zA-Z. ]+$')

        errors = {}

        if len(postData['name']) < 3:
            errors['name_len'] = "nombre debe tener al menos 3 caracteres de largo"

        if len(postData['alias']) < 3:
            errors['alias_len'] = "el alias debe tener al menos 3 caracteres de largo"

        if not EMAIL_REGEX.match(postData['email']):
            errors['email'] = "correo invalido"

        if not SOLO_LETRAS.match(postData['name']):
            errors['solo_letras'] = "solo letras en el nombre porfavor"

        if len(postData['password']) < 8:
            errors['password'] = "contraseña debe tener al menos 8 caracteres"

        if postData['password'] != postData['password_check']:
            errors['password_confirm'] = "las contraseña no son iguales."

        birthday = datetime.datetime.strptime(postData['born'], "%Y-%m-%d").date()

        if calculate_age(birthday) < 16:
            errors['menoredad'] = "El usuario debe tener al menos 16 años."


        #hoy = datetime.date.today()
        #release =datetime.datetime.strptime(postData['release_date'], '%Y-%m-%d').date()
        return errors


class User(models.Model):
    name = models.CharField(max_length=255)
    alias = models.CharField(max_length=255)
    # se puede usar models.EmailField
    email = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=70)
    born = models.DateField(null=True) 
    cant_pokes = models.IntegerField()
    rol = models.CharField(max_length=10, default='NORMAL')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()


    def __str__(self):
        return f"{self.name}"


    def __repr__(self):
        return f"{self.name}"


class Poke(models.Model):
    poked_by = models.ForeignKey(User, related_name="poked_by", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="pokes", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


from django.shortcuts import render
from Pokes_App.models import User, Poke
from django.shortcuts import redirect, render, HttpResponse
from time import gmtime, strftime, localtime
from datetime import datetime
from django.contrib import messages
import bcrypt
from itertools import chain
from django.db.models import Count


def index(request):
    if 'usuario' not in request.session:
        return redirect("/login")

    user = User.objects.get(id = request.session['usuario']['id'])
    #cant_my_pokes = user.pokes.all().count() 
    #my_pokes = Poke.objects.filter(user = user.id)   #order_by(user.desc())
    #my_pokes2 = Poke.objects.values('user').annotate(dcount=Count('user'))
    my_pokes= Poke.objects.values('poked_by__name','poked_by').annotate(Count('poked_by')).filter(user = user.id).order_by('-poked_by__count')
    cant_my_pokes = my_pokes.all().count() 

    other_users = User.objects.exclude(id = user.id).all()

    context = {
        'cant_my_pokes':  cant_my_pokes,
        'my_pokes': my_pokes,
        'other_users' : other_users,
    }

    return render(request, 'index.html', context)


def logout(request):
    if 'usuario' in request.session:
        del request.session['usuario']
    
    return redirect("/login")

def login(request):
    if request.method == 'POST':
        #buscamos el nombre de usuario ingresado en la base de datos (si existe) y asignamos a la variable user
        user = User.objects.filter(email=request.POST['email_login'])
        
        if user: #una lista vacía devolverá falso
            #si existe tomamos el primer elemento de la lista user (devuelto por filter)
            log_user = user[0]

            #validamos la contraseña ingresada por el usuario 
            if bcrypt.checkpw(request.POST['password_login'].encode(), log_user.password.encode()):
                # si obtenemos True después de validar la contraseña, podemos poner la identificación del usuario en la sesión
                usuario = {
                    "id" : log_user.id,
                    "name" : f"{log_user}", # usamos el "def __str__(self)" definido en el modelo con return f"{self.firstname} {self.lastname}"
                    "alias" : log_user.alias,
                    "email" : log_user.email,
                    "born" : log_user.born.strftime("%Y-%m-%d"),
                    "rol" : log_user.rol
                }

                request.session['usuario'] = usuario
                delsession(request)#vaciamos las variables de sesión del registro

                messages.success(request, "Logueado correctamente.")

                if request.session['usuario']['rol'] == "ADMIN" :
                    return redirect("/admin")
                
                else :
                    return redirect("/")

            else:#si la contraseña no coincide enviamos un mensaje de error al usuario
                messages.error(request, "Email o Contraseña invalidos.")
        
        else:#si la lista esta vacia significa que no se encontro el email ingresado
            #enviamos un mensaje de error al usuario
            messages.error(request, "Email o Contraseña invalidos.")

        return redirect("/login")#redirigimos al login


    else: #metodo GET
        return render(request, 'login.html')


def new_user (request):
    if request.method == 'POST':
        print(request.POST)
        #traemos el diccionario con errores para verificar si existen
        errors = User.objects.validador_basico(request.POST)
        print(errors)

        if len(errors) > 0:
            #si el diccionario de errores contiene algo, recorra cada par clave-valor y cree un mensaje flash
            for key, value in errors.items():
                messages.error(request, value);

                request.session['registro_name'] =  request.POST['name']
                request.session['registro_alias'] =  request.POST['alias']
                request.session['registro_email'] =  request.POST['email']

            # redirigir al usuario al formulario para corregir los errores
            return redirect(f'login')

        else:
            # si el objeto de errores está vacío, eso significa que no hubo errores.
            delsession(request)#vaciamos las variables de sesión del registro

            #encriptación de la contraseña ingresada por el usuario
            password_encryp = bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt()).decode()

            new_user = User.objects.create(
                                            name = request.POST['name'],
                                            alias = request.POST['alias'],
                                            email = request.POST['email'],
                                            born = request.POST['born'],
                                            cant_pokes = 0,
                                            password = password_encryp,
                                            )
            usuario = {
                    "id" : new_user.id,
                    "name" : f"{new_user}", # usamos el "def __str__(self)" definido en el modelo con return f"{self.firstname} {self.lastname}"
                    "alias" : new_user.alias,
                    "email" : new_user.email,
                    "born" : new_user.born,
                    "cant_pokes" : new_user.cant_pokes,
                    "rol" : new_user.rol
                }

            request.session['usuario'] = usuario
            
            messages.success(request, f'Se realizado el registro con exito.')
            #redirigimos a la ruta según el rol del uuario
            if request.session['usuario']['rol'] == "ADMIN" :
                    return redirect("/admin")
                
            else :
                return redirect("/")

    if request.method == 'GET':
        context = {
                    'saludo': 'Hola'
                    }
        return render(request, 'registro.html', context)


def admin(request):
    if 'usuario' not in request.session:
        return redirect("/login")

    if request.session['usuario']['rol'] != 'ADMIN':
        messages.error(request, "Estimado usuario no tiene acceso permitido al área de administración.")
        return redirect("/")

    users = User.objects.all()

    context = {
        'users': users
    }
    return render(request, 'admin/index.html', context)

def delsession(request):
    request.session['registro_name'] = ""
    request.session['registro_alias'] = ""
    request.session['registro_email'] = ""

    return


def edit_perfil(request, id_user):
    user =  User.objects.get(id=id_user)
    if request.method == 'GET':
        context = {
                'user':  user,
                }
        return render(request, 'editar_perfil.html', context)
    
    elif request.method == 'POST':
        user.name = request.POST['name'] 
        user.alias = request.POST['alias']
        user.email =  request.POST['email']
        user.save()

        request.session['usuario']['name'] = request.POST['name'] 

        print(request.session['usuario']['name'])


        return redirect(f'/')

def give_poked(request, id_user):
    
    user = User.objects.get(id=id_user)
    user_poked_by = User.objects.get(id = request.session['usuario']['id']) 

    new_poke = Poke.objects.create(
                                    poked_by = user_poked_by,
                                    user = user
                                    )

    user.cant_pokes = user.cant_pokes + 1 
    user.save()
    

    return redirect(f'/')
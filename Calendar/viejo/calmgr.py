# TODO: Mejorar sábado
#! python3.10.5
import datetime
import os.path
import json
import re
from Evento import Evento

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Si se modifican los SCOPES hay que borrar token.json
SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/drive'
]
días = {0:"lunes", 1:"martes", 2:"miércoles", 3:"jueves", 4:"viernes", 5:"sábado", 6:"domingo"}

def qh(x):
    hora = x // 60
    minuto = x % 60
    horafinal = f"{hora:02}:{minuto:02}"
    return horafinal

def qr (h,m):
    horaR = h*60+m
    return horaR

def calendario_vacío (ini,fin):
    fechas = []
    i = datetime.datetime(*ini)
    f = datetime.datetime(*fin)
    delta = (f-i).days
    for día in range(delta):
        fecha = i + datetime.timedelta(days=día)
        if fecha.weekday() == 5 or fecha.weekday() == 6: continue
        día = días[fecha.weekday()]
        fecha_str = f"{día} {fecha.day}/{fecha.month}"
        fechas.append(fecha_str)
    return fechas

def dic_horarios_tomados (lista_eventos):

    clases_por_fecha = {}
    for evento in lista_eventos:
        if not "Clase" in evento.nombre_evento and evento.esFinde: continue
        día = días[evento.iniDT.weekday()]
        fecha = f"{día} {evento.iniD}/{evento.iniM}"
        clases_por_fecha.setdefault(fecha,[]).append((evento.iniReal,evento.finReal))
    return clases_por_fecha

def dic_horarios_disp (ini, fin,tomado,i=540,f=1290,sf=720):
    relleno = calendario_vacío(ini,fin)
    disponible = {}
    inicio = i
    final = f
    for fecha,clases in tomado.items():
        for clase in clases:
            ini_clase = clase[0]
            fin_clase = clase[1]
            if ini_clase - inicio < 60:
                inicio = fin_clase +5
                continue
            disponible.setdefault(fecha,[]).append((qh(inicio),qh(ini_clase-5)))
            inicio = fin_clase + 5
        if fecha.startswith("sábado") and sf - inicio > 60:
            disponible.setdefault(fecha,[]).append((qh(inicio),qh(sf)))
            continue
        elif final - inicio > 60 and not fecha.startswith("sábado"):
            disponible.setdefault(fecha,[]).append((qh(inicio),qh(final)))
        inicio = i
    for fecha in relleno:
        if not fecha in disponible.keys():
            disponible[fecha] = [(qh(i),qh(f))]
    return disponible

def clases_alumno(lista_eventos,*nombres):
    clases = {}
    for alumno in lista_eventos:
        for nombre in nombres:
            if nombre in alumno.nombre_evento:
                hora_inicio = qh(qr(alumno.iniH,alumno.iniMin))
                hora_fin =qh(qr(alumno.finH,alumno.finMin))
                clases.setdefault(alumno.nombre_evento,[]).append(f"{alumno.iniD}/{alumno.iniM} - de {hora_inicio} a {hora_fin}")
    return clases

def main():

    creds = None
    if os.path.exists('D:\\code\\gcloud\\token.json'):
        creds = Credentials.from_authorized_user_file('D:\\code\\gcloud\\token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Intentando refrescar el token")
            creds.refresh(Request())
        else:
            print("No había credenciales o no pudo refrescarse el token")
            flow = InstalledAppFlow.from_client_secrets_file(
                'D:\\code\\gcloud\\credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('D:\\code\\gcloud\\token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)

    except HttpError as error:
        print(f'error: {error}')

    while True:
        ah = datetime.datetime.utcnow()
        try:
            modo = input("[f]echa | [d]ías | [a]lumno \n")
            if len(modo) == 0: break

            cambiar_fecha = input ("cambiar fecha inicial? [s|n]")

            if cambiar_fecha == "s":
                d, m = eval(input("buscar desde [día, mes]:\n"))
                fecha = datetime.datetime(ah.year, m, d)
                # después = ah
                if modo == "d":
                    ventana = int(input("días: "))
                else:
                    ventana = (ah - fecha).days
            else:
                fecha = ah

            cambiar_horarios = "n"

            if not modo == "a":
                cambiar_horarios = input ("cambiar horario de inicio y finalización? [s|n]")

            if cambiar_horarios == "s":
                ini_semana = eval(input("inicio semana -> hora,minuto:\n"))
                ini_semana = qr(*ini_semana)
                fin_semana = eval(input("fin semana -> hora,minuto\n"))
                fin_semana = qr(*fin_semana)
                fin_sábado = eval(input("fin sábado -> hora,minuto\n"))
                fin_sábado = qr(*fin_sábado)

            if modo == "a":
                alumno = input("alumnos separados por coma: ")

            if not cambiar_fecha == "s":
                if modo == "f":
                    d,m = eval(input("buscar hasta [día,mes]:\n"))
                    fecha_tope = datetime.datetime(ah.year,m,d,ah.hour,ah.minute,ah.second)
                    ventana = (fecha_tope - fecha).days
                else:
                    ventana = int(input("días: "))

            después = fecha + datetime.timedelta(days = (ventana+2))

        except:
            print ("tocaste mal")
            terminar = input("enter para continuar, alguna letra para terminar.")
            if terminar == "":
                continue
            else:
                quit()

        now = fecha.isoformat() + 'Z'
        then = después.isoformat() + 'Z'

        events = service.events().list(
                                        calendarId='primary',
                                        timeMin=now,
                                        timeMax=then,
                                        singleEvents=True,
                                        orderBy='startTime'
                                        ).execute()

        if not events:
            print('No hay eventos.')
            return

        lista_eventos = []
        for i in events["items"]:
            lista_eventos.append(Evento(i))

        if modo == "a":
            alumnos = alumno.split(",")
            alumnos = [x.lstrip().capitalize() for x in alumnos]
            dic_alumnos = clases_alumno(lista_eventos, *alumnos)
            for nombre, clases in dic_alumnos.items():
                print (f"\n{nombre}:")
                [print(x) for x in clases]

        horarios_tomados = dic_horarios_tomados(lista_eventos)

        ini = (fecha.year, fecha.month, fecha.day)
        fin = (después.year, después.month, después.day)

        if modo != "a":
            if cambiar_fecha != "s" and cambiar_horarios == "s":
                horarios_disponibles = dic_horarios_disp(ini, fin, horarios_tomados, i=ini_semana, f=fin_semana, sf=fin_sábado)

            else:
                horarios_disponibles = dic_horarios_disp(ini, fin, horarios_tomados)

            with open ("C:\\Users\\Mariano\\Desktop\\horarios disponibles.txt","w") as f:
                f.write("Horarios disponibles (FORMATO = hora mínima de comienzo - hora máxima de finalización):\n\n")
                print("Horarios disponibles (FORMATO = hora mínima de comienzo - hora máxima de finalización):")
                for fecha,horarios in horarios_disponibles.items():
                    f.write (f"    {fecha}:\n")
                    print (f"\n    {fecha}:")
                    for inter in horarios:
                        f.write(f"        de {inter[0]} a {inter[1]}\n")
                        print(f"        de {inter[0]} a {inter[1]}")
                    f.write("\n")

if __name__ == '__main__':
    main()

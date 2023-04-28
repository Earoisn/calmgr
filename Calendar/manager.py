from event import Event
from datetime import datetime as dt, timedelta as delta, timezone as tz
import json
import sys
sys.path.extend(["D:\\code\\gcloud","D:\\code\\gcloud\\Calendar"])
from Google import glogin, get_service
from event import Event

días = {0:"lunes", 1:"martes", 2:"miércoles", 3:"jueves", 4:"viernes", 5:"sábado", 6:"domingo"}

def n2a(datetime:dt):
    "toma un datetime y lo hace offset aware para Arg"
    return datetime.replace(tzinfo=tz(delta(hours=-3)))

def s2d(datetime:str):
    "wrapper para datetime.datetime.fromisoformat()"
    return dt.fromisoformat(datetime)

def t2d(datetime:tuple):
    "(año,mes,día,hora,minuto) -> offset aware datetime para Arg"
    return n2a(dt(datetime[0],datetime[1],datetime[2],datetime[3],datetime[4]))

def tinter():
    """
    Pide al usuario día, mes y año o toma fecha actual y cantidad de días por delante.
    Devuelve tupla (tmin,tmax) de fechas en formato iso para usar la API de Google Calendar
    """
    def check_fecha(fecha):
        if len(fecha.split(","))==2:
            año = ahora.year
            día,mes = eval(fecha)
        else:
            día,mes,año=eval(fecha)
            if año<100: año+=2000
        return (día,mes,año)
    
    ahora = n2a(dt.now())
    desde = input("Dejar un espacio para cambiar fecha inicial, enter para fecha actual.\n")
    if desde == " ":
        fecha = input("desde día,mes[,año]:\n")
        día,mes,año = check_fecha(fecha)
        desde = ahora.replace(year=año, month=mes, day=día, hour=0, minute=0)     
    else:
        desde = ahora
    hasta = input("Dejar un espacio para cambiar fecha final, enter para fecha actual.\n")
    if hasta == " ":
        fecha = input("Espacio para fecha, enter para días\n")
        if fecha == " ":
            fecha = input("hasta día,mes[,año]:\n")
            día, mes, año = check_fecha(fecha)
            hasta = ahora.replace(year=año, month=mes, day=día, hour= 0, minute= 0)
        else:
            hasta = input("días\n")
            try:
                hasta = int(hasta)
            except:
                print("La cagaste, ventana de tiempo establecida por defecto a 10 días.\n")
                hasta = 10
            hasta = desde + delta(hasta)
    else:
        hasta = ahora
        if (hasta-desde).total_seconds()<=0:
            print("La cagaste. Las fechas de inicio y finalización son iguales o la ventana temporal es negativa.")
            return None
    tmax = hasta.isoformat()
    tmin = desde.isoformat()
    return (tmin,tmax)

def freebusy(intervalo:tuple):
    """
    Args:
        intervalo: tupla (fecha de inicio, fecha de finalización) ambas en isoformat.
    Returns:
        freebusy().query() de Google Calendar API
        o
        None, si no había eventos.
    """
    tmin, tmax = intervalo
    api = 'calendar'
    creds = glogin(api)
    calendar = get_service(creds,api)
    events_busy = calendar.freebusy().query(body={
                                        "items": [{'id': 'primary'}],
                                        "timeMax": tmax,
                                        "timeMin": tmin,
                                        "timeZone": "America/Argentina/Buenos_Aires"
                                        }).execute()

    if not events_busy:
        print('No hay eventos.')
        return None
    else:
        return events_busy

def disponible(intervalo,inidefault:tuple=(9,0),findefault:tuple=(21,30)):
    """
    Args:
        events_busy: freebusy().query() de la API de Google Calendar,
        inidefault: tupla (hora,minuto) para inicio default del día, 
        findefault: tupla (hora,minuto) para fin default del día 
    Returns:
        json en el escritorio con horarios disponibles: {'día de la semana d/m':[(datetime inicio,datetime fin)...]} 
        para intervalos de tiempo libre de 60 minutos o más, dejando 5 minutos libres entre eventos.
    Prints:
        Los resultados en formato amigable
    """
    cambiar = input("Cambiar hora de inicio y finalización del día laboral? Espacio para cambiar, enter para seguir.\n")
    if len(cambiar) != 0:
        try:
            ini_h,ini_min,fin_h,fin_min = eval(input("hora inicio, minuto inicio, hora fin, minuto fin. Todos números enteros.\n"))
            inidefault = (ini_h,ini_min)
            findefault = (fin_h,fin_min)
        except:
            print("La cagaste, valores establecidos por defecto a las 9:00 y las 21:30.\n")
    
    events_busy = freebusy(intervalo)["calendars"]["primary"]["busy"]
    ini_h,ini_min = inidefault
    fin_h,fin_min = findefault
    actual = None
    anterior = None
    horarios_disponibles = {}
    ahora = n2a(dt.now())
    for evento in events_busy:
        ini = s2d(evento["start"])
        fin = s2d(evento["end"])
        if actual == None or ini.date() != actual:
            actual = ini.date()
            inidefault = t2d((ini.year,ini.month,ini.day,ini_h,ini_min))
            if (ahora-inidefault).total_seconds() > 0:
                inidefault = ahora
            key = f"{días[actual.weekday()]} {actual.day}/{actual.month}"
            horarios_disponibles.setdefault(key,[])
            if anterior != None and (findefault-anterior).total_seconds()/60 > 60:
                horarios_disponibles[prevkey].append((anterior,findefault))
            if (ini-inidefault).total_seconds()/60 > 60:
                horarios_disponibles[key].append((inidefault,ini))
        elif (ini-anterior).total_seconds()/60 > 60:
            horarios_disponibles[key].append((anterior,ini))
        anterior = fin
        findefault = t2d((ini.year,ini.month,ini.day,fin_h,fin_min))
        prevkey = key
    
    print("Horarios disponibles (de hora de inicio mínima a hora de finalización máxima):")    
    texto = ""
    for k,v in horarios_disponibles.items():
        if not ("sábado" or "domingo") in k:
            texto += "  •"+k+":\n    "
            for ini,fin in v:
                if (ini.hour,ini.minute) == (inidefault.hour,inidefault.minute):
                    ini_h,ini_min = ini.hour, ini.minute 
                elif ini.minute != 55:
                    ini_h,ini_min = ini.hour, (ini.minute+5) 
                else:
                    ini_h,ini_min = (ini.hour+1),0
                if (fin.hour,fin.minute) == (findefault.hour,findefault.minute):
                    fin_h,fin_min = fin.hour, fin.minute 
                elif fin.minute != 0:
                    fin_h,fin_min = fin.hour, (fin.minute-5) 
                else:
                    fin_h,fin_min = (fin.hour-1),55
                texto += f"de {ini_h:02}:{ini_min:02} a {fin_h:02}:{fin_min:02}, "
        texto += "\n"
    texto = texto[0:-3]+"."
    print(texto)
    with open ("C:\\Users\\Mariano\\Desktop\\horarios.json","w") as fb:
        for día,intervalos in horarios_disponibles.items():
            horarios_disponibles[día]=[(str(horario[0]),str(horario[1])) for horario in intervalos]
        json.dump(horarios_disponibles,fb)

    return horarios_disponibles

def dic_alumnos(intervalo:tuple,precio=60):
    """ 
    Args:
        intervalo: tupla (tmin,tmax) para establecer ventana de búsqueda en Google Calendar.
        precio: precio por minuto de clase.
    Returns:
        alumnos: diccionario con nombre del o los alumnos (en caso de clase grupal) asociado a un objeto Event(). 
        Event().clases = lista de tuplas (d,m,ini_h,ini_min,fin_h,fin_min,precio) para cada clase.
    """
    page_token = None
    tmin,tmax = intervalo
    alumnos = dict()
    while True:
        api = "calendar"
        creds = glogin(api)
        calendar = get_service(creds,api)
        events = calendar.events().list(
                                        calendarId='primary',
                                        timeMin=tmin,
                                        timeMax=tmax,
                                        singleEvents=True,
                                        orderBy='startTime',
                                        pageToken = page_token
                                        ).execute()

        if not events:
                print('No hay eventos.')
                return

        lista_eventos = events.get('items', [])
        page_token = events.get('nextPageToken', None)

        for i in lista_eventos:
            evento = Event(i,precio)
            nombre = evento.nombre
            if "Clase" in nombre:
                alumnos.setdefault(nombre.split("Clase ")[1],evento).agrega_clase(
                                                                                evento.ini_d,evento.ini_m,
                                                                                evento.ini_h,evento.ini_min,
                                                                                evento.fin_h,evento.fin_min, 
                                                                                evento.precio
                                                                                )

        if page_token is None:
            break
    
    return alumnos

def info_alumnos(intervalo:tuple):
    """
    Pide al usuario lista de alumnos o enter para mostrar todos.
    
    Args:
        intervalo: tupla (tmin,tmax) para establecer ventana de búsqueda en Google Calendar.
    Prints:
        lista de alumnos con sus clases, el precio de cada una, la suma total del alumno y la suma total de todos los alumnos.
    Returns:
        dic_alumnos(intervalo)
    """
    plata = list()
    total = []
    alumnos = dic_alumnos(intervalo)
    lista_alumnos = input("Alumnos separados por coma.\n")
    if len(lista_alumnos) != 0:
        lista_alumnos = [alumno.strip().capitalize() for alumno in lista_alumnos.split(",")]
    else:
        lista_alumnos = alumnos.keys()

    for alumno in lista_alumnos:
        datos = alumnos.get(alumno,None)
        grupal = False
        if not datos:
            for clase, datos in alumnos.items():             
                if alumno in clase and "y" in clase:
                    print(f"\n{alumno} está en una clase grupal:")
                    grupal = True
                    break
            if not grupal:
                print(f"No se encontraron datos de {alumno}.\n")
                continue
        print(f"--------------------------------------------\n{datos.nombre}:")
        for clase in datos.clases:
            día,mes,ini_h,ini_min,fin_h,fin_min,precio=clase
            if grupal:
                precio /= 2
            print(f"Clase del {día:02}/{mes:02} de {ini_h:02}:{ini_min:02} a {fin_h:02}:{fin_min:02} --> ${precio:.0f}")
            plata.append(precio)
        print(f"Total: ${sum(plata):.0f}.\n--------------------------------------------\n")
        total.extend(plata)
        plata.clear()
    print(f"Total final: ${sum(total):.0f}")

    return alumnos

def calc_ingresos(intervalo:tuple):
    """
    Args:
        intervalo: tupla (tmin,tmax) para establecer ventana de búsqueda en Google Calendar.
    Prints:
        plata correspondiente al intervalo, basada en los eventos de Google Calendar.

    """
    precio = input ("Precio de la hora o enter para usar el valor por defecto.\n")
    if len(precio) != 0:
        try:
            precio = eval(precio)/60
        except:
            print("La cagaste, precio establecido por defecto.\n")
            precio = 60
        alumnos = dic_alumnos(intervalo,precio)
    else:
        alumnos = dic_alumnos(intervalo)
    plata = []
    for alumno in alumnos.values():
        for clase in alumno.clases:
            plata.append(clase[6])
    print (f"Total: ${sum(plata):.0f}.\n")

def main():
    while True: 
        ejecutar = "x"    
        while ejecutar not in "hac":
            ejecutar = input("[h]orarios | [a]lumnos | [c]alculadora de ingresos\n")
        if len(ejecutar) == 0: break
        intervalo = tinter()
        if not intervalo:
            print("Reiniciando script.\n")
            continue
        match ejecutar:
            case "h":
                disponible(intervalo)
            case "a":
                info_alumnos(intervalo)
            case "c":
                calc_ingresos(intervalo)
            case _:
                print("La cagaste.")
        
        terminar = input("Espacio para volver a usar, enter para terminar.\n")
        if len(terminar) == 0: break

if __name__ == '__main__':
    main()

from event import Event
from datetime import datetime as dt, timedelta as delta, timezone as tz
import json
import sys
from copy import deepcopy
sys.path.extend(["D:\\code\\gcloud","D:\\code\\gcloud\\Calendar"])
from Google import glogin, get_service
from alumno import Listado

def n2a(datetime:dt):
    "abrev. de 'naive to aware' - toma un datetime y lo hace offset aware para Arg"
    return datetime.replace(tzinfo=tz(delta(hours=-3)))

def s2d(datetime:str):
    "abrev. de 'string_to_date' - wrapper para datetime.datetime.fromisoformat()"
    return dt.fromisoformat(datetime)

def t2d(datetime:tuple):
    "abrev. de 'tuple_to_date' - (año, mes, día, hora, minuto) -> offset aware datetime para Arg"
    return n2a(dt(datetime[0], datetime[1], datetime[2], datetime[3], datetime[4]))

def d2t(datetime:dt):
    "abrev. de 'date_to_tuple' - datetime -> (año, mes, día, hora, minuto)"
    return (datetime.year, datetime.month, datetime.day, datetime.hour, datetime.minute)

def tinter(deuda = None):
    """
    Pide al usuario día, mes y año o toma fecha actual y cantidad de días por delante.
    Args:
        deuda (opcional): tupla (yyyy,m,d,H,M) - último pago del alumno. En caso de recibir este argumento, funciona como tmin en el return.
    Returns:
        tupla (tmin, tmax) de fechas en formato iso para usar la API de Google Calendar
    """

    def check_fecha(fecha):
        if len(fecha.split(",")) == 2:
            año = ahora.year
            día,mes = eval(fecha)
        else:
            día, mes, año = eval(fecha)
            if año < 100: año += 2000
        return (día, mes, año)
    
    ahora = n2a(dt.now())
    if deuda:
        desde = t2d(deuda)
    else:
        desde = input("Dejar un espacio para cambiar fecha inicial, enter para fecha actual.\n")
        if desde == " ":
            fecha = input("desde día, mes[, año]:\n")
            día, mes, año = check_fecha(fecha)
            desde = ahora.replace(year = año, month = mes, day = día, hour = 0, minute = 0)     
        else:
            desde = ahora
    
    hasta = input("Dejar un espacio para cambiar fecha final, enter para fecha actual.\n")
    if hasta == " ":
        fecha = input("Espacio para fecha, enter para días\n")
        if fecha == " ":
            fecha = input("hasta día, mes[, año]:\n")
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
        if (hasta - desde).total_seconds() <= 0:
            print("La cagaste. Las fechas de inicio y finalización son iguales o la ventana temporal es negativa.")
            return None
    tmax = hasta.isoformat()
    tmin = desde.isoformat()
    return (tmin, tmax)

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
    calendar = get_service(creds, api)
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

def disponible(intervalo, inidefault:tuple=(9,0), findefault:tuple=(21,30)):
    """
    Args:
        events_busy: freebusy().query() de la API de Google Calendar,
        inidefault: tupla (hora, minuto) para inicio default del día, 
        findefault: tupla (hora,minuto) para fin default del día 
    Returns:
        json en el escritorio con horarios disponibles: {'día de la semana d/m':[(datetime inicio, datetime fin)...]} 
        para intervalos de tiempo libre de 60 minutos o más, dejando 5 minutos libres entre eventos.
    Prints:
        Los resultados en formato amigable
    """
    días = {0: "lunes", 1: "martes", 2: "miércoles", 3: "jueves", 4: "viernes", 5: "sábado", 6: "domingo"}
    cambiar = input("Cambiar hora de inicio y finalización del día laboral? Espacio para cambiar, enter para seguir.\n")
    if len(cambiar) != 0:
        try:
            ini_h, ini_min, fin_h, fin_min = eval(input("hora inicio, minuto inicio, hora fin, minuto fin. Todos números enteros.\n"))
            inidefault = (ini_h, ini_min)
            findefault = (fin_h, fin_min)
        except:
            print("La cagaste, valores establecidos por defecto a las 9:00 y las 21:30.\n")
    
    events_busy = freebusy(intervalo)["calendars"]["primary"]["busy"]
    ini_h, ini_min = inidefault
    fin_h, fin_min = findefault
    actual = None
    anterior = None
    horarios_disponibles = {}
    ahora = n2a(dt.now())
    for evento in events_busy:
        ini = s2d(evento["start"])
        fin = s2d(evento["end"])
        if actual == None or ini.date() != actual:
            actual = ini.date()
            inidefault = t2d((ini.year, ini.month, ini.day, ini_h, ini_min))
            if (ahora - inidefault).total_seconds() > 0:
                inidefault = ahora
            key = f"{días[actual.weekday()]} {actual.day}/{actual.month}"
            horarios_disponibles.setdefault(key, [])
            if anterior != None and (findefault - anterior).total_seconds() / 60 > 60:
                horarios_disponibles[prevkey].append((anterior, findefault))
            if (ini - inidefault).total_seconds() / 60 > 60:
                horarios_disponibles[key].append((inidefault, ini))
        elif (ini - anterior).total_seconds() / 60 > 60:
            horarios_disponibles[key].append((anterior, ini))
        anterior = fin
        findefault = t2d((ini.year, ini.month, ini.day, fin_h, fin_min))
        prevkey = key
    
    print("Horarios disponibles (de hora de inicio mínima a hora de finalización máxima):")    
    texto = ""
    for k,v in horarios_disponibles.items():
        if not ("sábado" or "domingo") in k:
            texto += f"  •{k}:\n    "
            for ini, fin in v:
                if (ini.hour, ini.minute) == (inidefault.hour, inidefault.minute):
                    ini_h, ini_min = ini.hour, ini.minute 
                elif ini.minute != 55:
                    ini_h, ini_min = ini.hour, (ini.minute + 5) 
                else:
                    ini_h, ini_min = (ini.hour + 1), 0
                if (fin.hour, fin.minute) == (findefault.hour, findefault.minute):
                    fin_h, fin_min = fin.hour, fin.minute 
                elif fin.minute != 0:
                    fin_h, fin_min = fin.hour, (fin.minute - 5) 
                else:
                    fin_h, fin_min = (fin.hour - 1), 55
                texto += f"de {ini_h:02}:{ini_min:02} a {fin_h:02}:{fin_min:02}, "
        texto += "\n"
    texto = texto[0:-3]+"."
    print(texto)
    with open("C:\\Users\\Mariano\\Desktop\\horarios.json","w") as fh:
        for día, intervalos in horarios_disponibles.items():
            horarios_disponibles[día]=[(str(horario[0]), str(horario[1])) for horario in intervalos]
        json.dump(horarios_disponibles, fh)

    return horarios_disponibles

def dic_alumnos(intervalo:tuple, precio = 60):
    """ 
    Args:
        intervalo: tupla (tmin, tmax) para establecer ventana de búsqueda en Google Calendar.
        precio: precio por minuto de clase.
    Returns:
        alumnos: diccionario con nombre del alumno asociado a un objeto Event(). 
        Event().clases = lista de tuplas (d, m, ini_h, ini_min, fin_h, fin_min, precio) para cada clase.
    """
    page_token = None
    tmin, tmax = intervalo
    alumnos = dict()
    while True:
        api = "calendar"
        creds = glogin(api)
        calendar = get_service(creds, api)
        events = calendar.events().list(
                                        calendarId ='primary',
                                        timeMin = tmin,
                                        timeMax = tmax,
                                        singleEvents = True,
                                        orderBy = 'startTime',
                                        pageToken = page_token
                                        ).execute()

        if not events:
                print('No hay eventos.')
                return

        lista_eventos = events.get('items', [])
        page_token = events.get('nextPageToken', None)

        for i in lista_eventos:
            evento = Event(i, precio)
            if evento.es_clase:
                clase = evento
                for alumno in clase.alumno:
                    alumnos.setdefault(alumno, evento if not clase.es_grupal else deepcopy(evento)).agrega_clase(
                                evento.ini_d, evento.ini_m,
                                evento.ini_h, evento.ini_min,
                                evento.fin_h, evento.fin_min, 
                                evento.precio
                                )

        if page_token is None:
            break
    return alumnos

def info_alumnos(intervalo:tuple, base = None):
    """
    Pide al usuario lista de alumnos o enter para mostrar todos.
    
    Args:
        intervalo: tupla (tmin, tmax) para establecer ventana de búsqueda en Google Calendar.
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
        for i in lista_alumnos:
            print(i)

    encontrado = False
    for alumno in lista_alumnos:
        datos = alumnos.get(alumno, None)
        if not datos:
            print(f"No se encontró información de {alumno} en el calendario.\n")
            continue
        encontrado = True
        print(f"--------------------------------------------\n{alumno}:")
        for clase in datos.clases:
            día, mes, ini_h, ini_min, fin_h, fin_min, precio = clase
            if base:
                if not base.alumnos.get(alumno):
                    print (f"No se encontró información de {alumno} en la base, comprobá manualmente su situación.")
                    break
                if t2d((dt.now().year,mes,día,ini_h,ini_min)) < t2d(base.alumnos[alumno]["fecha_pago"]):
                    continue
            print(f"Clase del {día:02}/{mes:02} de {ini_h:02}:{ini_min:02} a {fin_h:02}:{fin_min:02} --> ${precio:.0f}")
            plata.append(precio)
        
        print(f"Total: ${sum(plata):.0f}.\n--------------------------------------------\n")
        total.extend(plata)
        plata.clear()
    if encontrado:
        print(f"Total final: ${sum(total):.0f}")

    return alumnos

def calc_ingresos(intervalo:tuple):
    """
    Args:
        intervalo: tupla (tmin, tmax) para establecer ventana de búsqueda en Google Calendar.
    Prints:
        plata correspondiente al intervalo, basada en los eventos de Google Calendar.

    """
    precio = input("Precio de la hora o enter para usar el valor por defecto.\n")
    if len(precio) != 0:
        try:
            precio = eval(precio) / 60
        except:
            print("La cagaste, precio establecido por defecto.\n")
            precio = 60
        alumnos = dic_alumnos(intervalo, precio)
    else:
        alumnos = dic_alumnos(intervalo)
    plata = []
    for alumno in alumnos.values():
        for clase in alumno.clases:
            plata.append(clase[6])
    print(f"Total: ${sum(plata):.0f}.\n")

def main():
    while True: 
        ejecutar = "x"    
        while ejecutar not in "hac":
            ejecutar = input("[h]orarios | [a]lumnos | [c]alculadora de ingresos\n")
        if len(ejecutar) == 0: break
        if ejecutar != "a":
            intervalo = tinter()
            if not intervalo:
                print("Reiniciando script.\n")
                continue
        match ejecutar:
            
            case "h":
                disponible(intervalo)

            case "a":
                base = None
                opt = "x"
                while opt not in "cdpm":
                    opt = input("[c]onsulta manual, [d]euda, [p]ago, [m]odificar listado.\n")
                
                match opt:
                    case "c":
                        consulta = "x"
                        while consulta not in "cd":
                            consulta = input("[d]ata fiscal, [c]lases. \n")
                        if consulta == "d":
                            dic = Listado.load()
                            alumno = input("Alumno: ")
                            alumno = alumno.capitalize()
                            data = dic.alumnos.get(alumno)
                            if not data:
                                print (f"No se econtró información de {alumno} en la base.\n")
                                return None
                            else:
                                print(data.get("data_fiscal"))
                            continue
                        if consulta == "c":
                            intervalo = tinter()
                    
                    case "d":
                        base = Listado.load()
                        tmin = (min([t2d(v["fecha_pago"]) for v in base.alumnos.values()]))
                        intervalo = tinter(d2t(tmin))
                                        
                    case "p":
                        alumno = input("nombre del alumno.\n")
                        alumno = alumno.capitalize()
                        fecha = input("Espacio para introducir fecha de último pago, enter para fecha actual.\n")
                        if fecha != "":
                            try:
                                d, m = eval(input("día, mes: "))
                                Listado.pago(alumno, (m, d))
                                continue
                            except:
                                print("La cagaste.\n")
                        Listado.pago(alumno)
                        continue
                    
                    case "m":
                        alumno = input("Alumno: ")
                        alumno = alumno.capitalize()
                        opt = input("Espacio para agregar, enter para eliminar.\n")
                        if opt == " ":
                            data = input("Espacio para ingresar data fiscal, enter para 'Consumidor Final'.\n")
                            if data == " ":
                                cuit = input("CUIT sin guiones ni espacios: \n")
                                cond = input("Condición frente al IVA: \n")
                                data = cuit + " " + cond
                            else:
                                data = "Consumidor Final"
                            Listado.agregar_alumno(alumno, data)
                        else:
                            Listado.eliminar_alumno(alumno)
                        
                        continue

                if not intervalo:
                    print("Reiniciando script.\n")
                    continue
                
                if base:
                    info_alumnos(intervalo, base)
                else:
                    info_alumnos(intervalo)

            case "c":
                calc_ingresos(intervalo)
        
        terminar = input("Espacio para volver a usar, enter para terminar.\n")
        if len(terminar) == 0: break

if __name__ == '__main__':
    main()

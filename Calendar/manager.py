from datetime import datetime as dt, timedelta as delta, timezone as tz
from copy import deepcopy
import sys
sys.path.extend(["D:\\code\\gcloud", "D:\\code\\gcloud\\Calendar"])
from google_ import glogin, get_service
from event import Event
from alumno import Listado

def n2a(datetime: dt):
    """abrev. de 'naive to aware' - toma un datetime y lo hace offset aware para Arg"""
    return datetime.replace(tzinfo=tz(delta(hours=-3)))


def s2d(datetime: str):
    """abrev. de 'string_to_date' - wrapper para datetime.datetime.fromisoformat()"""
    return dt.fromisoformat(datetime)


def t2d(datetime: tuple):
    """
    abrev. de 'tuple_to_date' - (año, mes, día, hora, minuto) -> offset aware datetime para Arg
    """
    return n2a(dt(datetime[0], datetime[1], datetime[2], datetime[3], datetime[4]))


def d2t(datetime:dt):
    """abrev. de 'date_to_tuple' - datetime -> (año, mes, día, hora, minuto)"""
    return (datetime.year, datetime.month, datetime.day, datetime.hour, datetime.minute)


def tinter(tmin=None, tmax=None):
    """
    Pide al usuario día, mes y año o toma fecha actual y cantidad de días por delante.
    Args:
        tmin (opcional): tupla (yyyy,m,d,H,M) - En caso de recibir este argumento,funciona como tmin en el return. 
        (Puede ser utilizado para calcular la deuda de un alumno introduciendo el útlimo
        pago registrado).
        tmax (opcional): idem tmin, pero tmax. 

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
    
    if tmin:
        desde = t2d(tmin)
    else:
        desde = input(
            "Dejar un espacio para cambiar fecha inicial, enter para fecha actual.\n"
        )

        if desde == " ":
            fecha = input("desde día, mes[, año]:\n")
            día, mes, año = check_fecha(fecha)
            desde = ahora.replace(
                year=año,
                month=mes,
                day=día,
                hour=0,
                minute=0
            )     
        else:
            desde = ahora    

    if tmax:
        hasta = t2d(tmax)
    else:    
        if not (desde == ahora or ((ahora-desde).total_seconds() < 60)):
            hasta = input(
                "Dejar un espacio para cambiar fecha final, enter para fecha actual.\n"
            )
        else:
            hasta = " "
    
    if hasta == " ":
        fecha = input(
            "Espacio para fecha final, enter para días desde la fecha inicial.\n"
        )

        if fecha == " ":
            fecha = input("hasta día, mes[, año]:\n")
            día, mes, año = check_fecha(fecha)
            hasta = ahora.replace(
                year=año,
                month=mes,
                day=día,
                hour=23,
                minute=59
            )
        else:
            hasta = input("días\n")
            try:
                hasta = int(hasta)
            except:
                print(
                    "La cagaste, ventana de tiempo establecida por defecto a 10 días.\n"
                )
                hasta = 10
            hasta = (desde.replace(hour=23, minute=59) + delta(hasta))
    elif not tmax:
        hasta = ahora
    
    if (hasta - desde).total_seconds() <= 0:
        print(
            "La cagaste. Las fechas de inicio y finalización son iguales "\
            + "o la ventana temporal es negativa."
        )
        return None
    
    tmax = hasta.isoformat()
    tmin = desde.isoformat()
    
    return (tmin, tmax)


def freebusy(intervalo: tuple):
    """
    Args:
        intervalo: tupla (tmin, tmax) en isoformat para establecer ventana de búsqueda en
        Google Calendar. Se puede usar tinter() para generarla.
    Returns:
        freebusy().query() response de Google Calendar API
        o
        None, si no había eventos.
    """
    
    tmin, tmax = intervalo
    api = 'calendar'
    creds = glogin(api)
    calendar = get_service(creds, api)
    events_busy = calendar.freebusy().query(
        body={
            "items": [{'id': 'primary'}],
            "timeMax": tmax,
            "timeMin": tmin,
            "timeZone": "America/Argentina/Buenos_Aires"
        }
    ).execute()

    if not events_busy:
        print('No hay eventos.')
        return None
    else:
        return events_busy


def disponible(
        intervalo: tuple,
        inidefault: tuple = (9, 0),
        findefault: tuple = (21, 30)
    ):
    """
    Args:
        intervalo: tupla (tmin, tmax) en isoformat para establecer ventana de búsqueda en
        Google Calendar. Se puede usar tinter() para generarla.
        events_busy: freebusy().query() de la API de Google Calendar,
        inidefault: tupla (hora, minuto) para inicio default del día,
        findefault: tupla (hora,minuto) para fin default del día

    Returns:
        .txt en el escritorio con horarios disponibles

    Prints:
        horarios disponibles.
    """
    
    días = {
        0: "lunes",
        1: "martes",
        2: "miércoles",
        3: "jueves",
        4: "viernes",
        5: "sábado",
        6: "domingo"
    }
    cambiar = input("Cambiar hora de inicio y finalización del día laboral? Espacio para cambiar, enter para seguir.\n")
    
    if len(cambiar) != 0:
        try:
            ini_h, ini_min, fin_h, fin_min = eval(input("hora inicio, minuto inicio, hora fin, minuto fin. Todos números enteros.\n"))
            inidefault = (ini_h, ini_min)
            findefault = (fin_h, fin_min)
        except:
            print(
                "La cagaste, valores establecidos por defecto a las 9:00 y las 21:30.\n"
            )
    
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
    
    if anterior != None and (findefault - anterior).total_seconds() / 60 > 60:
        horarios_disponibles[prevkey].append((anterior, findefault))
    
    texto = "Horarios disponibles (de hora de inicio mínima "\
            + "a hora de finalización máxima):\n"    
    
    for k,v in horarios_disponibles.items():
        if any(día in k for día in ["sábado", "domingo"]): continue
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
    
    with open("C:\\Users\\Mariano\\Desktop\\horarios.txt","w") as fh:
        fh.write(texto)

    return horarios_disponibles


def dic_alumnos(intervalo: tuple, precio=60):
    """ 
    Args:
        intervalo: tupla (tmin, tmax) en isoformat para establecer ventana de búsqueda en Google Calendar. Se puede usar tinter() para generarla.
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
            calendarId='primary',
            timeMin=tmin,
            timeMax=tmax,
            singleEvents=True,
            orderBy='startTime',
            pageToken=page_token
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


def info_alumnos(intervalo: tuple, base=None):
    """
    Pide al usuario lista de alumnos o enter para mostrar todos.
    
    Args:
        intervalo: tupla (tmin, tmax) en isoformat para establecer ventana de búsqueda en
        Google Calendar. Se puede usar tinter() para generarla.
        base (opcional): base de datos local (instancia de Listado) que hay que pasar cuando se quiere chequear deuda de uno o más alumnos.

    Prints:
        lista de alumnos con sus clases, el precio de cada una, la suma total del alumno y la suma total de todos los alumnos.

    Returns:
        dic_alumnos(intervalo)
    """
    from alumno import Listado
    plata = list()
    total = []
    alumnos = dic_alumnos(intervalo)
    lista_alumnos = Listado.buscar()
    
    if not lista_alumnos:
        lista_alumnos = alumnos.keys()

    encontrado = False
    
    for alumno in lista_alumnos:
        datos = alumnos.get(alumno, None)
        txt = ""

        if not datos:
            print(f"No se encontró información de {alumno} en el calendario.\n")
            continue
        
        encontrado = True
                
        for clase in datos.clases:
            día, mes, ini_h, ini_min, fin_h, fin_min, precio = clase
            
            if base:
                if not base.alumnos.get(alumno):
                    print (f"No se encontró información de {alumno} en la base, comprobá manualmente su situación.")
                    break
                
                fecha_clase = t2d((dt.now().year, mes, día, ini_h, ini_min))
                fecha_pago = t2d(base.alumnos[alumno]["fecha_pago"])

                if fecha_clase < fecha_pago:
                    continue
            
            txt += f"Clase del {día:02}/{mes:02} de {ini_h:02}:{ini_min:02} a {fin_h:02}:{fin_min:02} --> ${precio:.0f}\n"
            plata.append(precio)
        
        if base and (sum(plata) == 0): 
            print(f"--------------------------------------------\n"\
                + f"{alumno} no registra deuda.\n"\
                + f"--------------------------------------------\n")

            continue

        print(f"--------------------------------------------\n{alumno}:")
        print(txt)
        print(f"Total: ${sum(plata):.0f}.\n--------------------------------------------\n")
        total.extend(plata)
        plata.clear()
    
    if encontrado:
        print(f"\nTotal final: ${sum(total):.0f}\n")

    return alumnos


def calc_ingresos(intervalo: tuple):
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
    print("Actualizando base de datos")
    Listado.sync()
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
                    opt = input(
                        "[c]onsulta manual, [d]euda, [p]ago, [m]odificar listado.\n"
                    )
                
                match opt:

                    case "c":
                        consulta = "x"
                        
                        while consulta not in "cd":
                            consulta = input("[d]ata fiscal y último pago, [c]lases.\n")
                        
                        match consulta:
                            
                            case "d":
                                alumnos = Listado.buscar()
                                
                                if len(alumnos) == 0: 
                                    todos = input("Espacio para mostrar todos, enter para continuar.\n")
                                    
                                    if todos == " ":
                                        alumnos = Listado.load().alumnos
                                    else: continue

                                elif len(alumnos) == 1:
                                    consulta_modifica = input(
                                    "Espacio para modificar, enter para consultar.\n"
                                )

                                    if consulta_modifica == " ":
                                        if not len(alumnos) == 1:
                                            print("La cagaste.")
                                            continue
                                        
                                        Listado.agregar(alumnos[0], mod=True)
                                        continue
                                    
                                Listado.data_pago(alumnos)
                                continue
                            
                            case "c":
                                intervalo = tinter()
                    
                    case "d":
                        base = Listado.load()
                        # establece la fecha de último pago más antigua de entre las de
                        # todos los alumnos como tmin.
                        tmin = (
                            min(
                            [t2d(datos["fecha_pago"]) for datos in base.alumnos.values()]
                            )
                        )
                        intervalo = tinter(d2t(tmin))
                                        
                    case "p":
                        alumno = Listado.buscar()
                        
                        if len(alumno) == 0: continue

                        if not len(alumno) == 1: 
                            print("La cagaste. Te dije uno solo.\n")
                            continue
                        
                        fecha = input("Espacio para introducir fecha de último pago, enter para fecha actual.\n")
                        
                        if fecha != "":
                            try:
                                d, m = eval(input("día, mes: "))
                                Listado.pago(alumno[0], (m, d))
                                Listado.data_pago(alumno)
                                continue
                            except:
                                print("La cagaste. Eran número de día y número de mes separados con coma.\n")
                                continue
                        
                        Listado.pago(alumno[0])
                        Listado.data_pago(alumno)
                        continue
                    
                    case "m":
                        opt = input("Espacio para eliminar, enter para agregar.\n")
                        
                        if opt == "":
                            alumno = Listado.buscar(mod = True)
                            
                            if not len(alumno) == 1:
                                print("La cagaste.\n")
                                continue

                            Listado.agregar(alumno[0])                        
                        elif opt == " ":
                            alumno = Listado.buscar()
                            
                            if not alumno: continue
                            
                            ok = input(f"Seguro que deseás eliminar a {alumno[0]}? Escribí 'sí' para confirmar.\n")
                            
                            if ok == "sí":
                                Listado.eliminar(alumno[0])
                        else:
                            print("Reiniciando.")
                                                    
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


if __name__ == '__main__':
    main()
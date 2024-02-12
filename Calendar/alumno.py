from datetime import datetime as dt, timedelta as delta
import pickle


class Listado:
    """
    Clase utilizada para modificar la base de datos de alumnos. Puede agregar o borrar a un alumno, modificar la última fecha de pago, la data fiscal y agregar notas.
    Methods:

        backup(): crea un backup de la base en el directorio predeterminado

        load(): carga del directorio predeterminado y devuelve la base de datos como un objeto de esta clase

        save(base): guarda el objeto que se pasa como argumento en el directorio por defecto, sobreescribiendo el anterior. Crea un backup que también se sobreescribirá con la próxima modificación.

        sync(): compara alumnos del calendario con los asentados en la base local. Si encuentra diferencias, hace un backup y actualiza.

        buscar(): búsqueda inteligente a partir del input del usuario.

        datagen(): produce string con data fiscal a partir del input del usuario.

        agregar(nombre, fecha de último pago (yyyy,m,d,H,M), data_fiscal, nota): agrega alumno a la base local.

        eliminar(nombre): elimina alumno de la base local.
        
        pago(alumno[, (yyyy,m,d)]): asigna la fecha actual o la tupla opcional como último pago de ese alumno en la base local.

        data_pago(alumnos): imprime todos los datos de los alumnos del argumento.
    """

    def __init__(self, base=dict()):
        self.alumnos = base
    
    def backup():
        listado = Listado.load()
        
        with open("D:\\code\\gcloud\\Calendar\\base_backup.pickle", "wb") as b:
            pickle.dump(listado, b)
    
    def load(base=None):
        if not base:
            base = "base"
        
        with open(f"D:\\code\\gcloud\\Calendar\\{base}.pickle", "rb") as b:
            lista = pickle.load(b)

        return lista
    
    def save(base):
        Listado.backup()
        
        with open("D:\\code\\gcloud\\Calendar\\base.pickle", "wb") as b:
            pickle.dump(base, b)
            return
        
    def sync():
        from manager import tinter, n2a, d2t, dic_alumnos
        Listado.backup()
        listado = Listado.load()
        ahora = n2a(dt.now().replace(hour=23, minute=59))
        dif = delta(days=30)
        tmin = d2t(ahora - dif)
        tmax = d2t(ahora)
        intervalo = tinter(tmin, tmax)
        alumnos_calendario = list(dic_alumnos(intervalo).keys())
        alumnos_base = list(listado.alumnos.keys())
        nuevos = [alumno for alumno in alumnos_calendario if alumno not in alumnos_base]
        if len(nuevos) == 0:
            print("La base se encontraba actualizada.")
            return None
        else:
            for alumno in nuevos:
                Listado.agregar(nombre=alumno, sync=True)
                print(f"Se agregó a {alumno} a la base")
            print(f"Se completó la actualización de la base de datos.")
            return None

    def buscar(mod=False, base=None):
        """
        Pide al usuario lista de alumnos separados por coma, pero acepta a partir de una
        letra para buscar en la base de datos si existen coincidencias.
        En caso de tipear los alumnos completos, devuelve la lista, de lo contrario, ofrece
        las posibilidades para elegir.
        
        Args:
            mod: flag para pasar nombres sin alterarlos, solo haciendo split(",") en el input string.
            base: diccionario con datos de los alumnos - Listado.load().alumnos por defecto.
        
        Returns:
            lista con los nombres completos de los alumnos | 
            lista vacía cuando:

            1) no hay coincidencias

            2) en la selección de coincidencias:
                a) se comete un error al poner números separados por coma

                b) se deja vacía la selección.
        """
        
        if not base:
            base = Listado.load().alumnos
        
        buscar = input(
            "Nombres separados por coma, puede buscar a partir de una sola letra.\n"\
            + "Si es para asentar un pago o para modificar la base de datos, "\
            + "introducir un solo nombre.\n"
        )
        nombres = [nombre.strip().lower() for nombre in buscar.split(",")]
        encontrados = [
            nombre for nombre in base.keys() 
            for b in nombres if nombre.lower().startswith(b)
        ]
        exactos = [
            nombre for nombre in base.keys() 
            for b in nombres if nombre.lower() == b.lower()
        ]
        
        if mod: return sorted([nombre.capitalize() for nombre in nombres])

        if len(encontrados) == 0:
            print("No se encontró información para está búsqueda en la base de datos.")
            return []
        elif len(encontrados) == len(exactos):
            return sorted(encontrados)
        else:
            encontrados.sort()
            print("Posibles coincidencias:")
            
            for i, alumno in enumerate(encontrados):
                print(f"{i+1}. {alumno}")

            selec = input("Números separados por coma.\n")
            
            if selec == "": return []
            
            try:
                selec = [int(n.strip()) for n in selec.split(",")]
            except:
                print("La cagaste.")
                return []
            
            alumnos = [encontrados[n-1] for n in selec]

        return sorted(alumnos)

    def datagen():
        opc = input("[s]in información, [c]onsumidor final, [d]ata fiscal.\n")
        
        if opc == "s":
            data_fiscal = "Sin información"
        elif opc == "c":
            data_fiscal = "Consumidor Final"
        else:
            nombre = input("Nombre y apellido: \n")
            cuit = input("CUIT sin guiones ni espacios: \n")
            cond = input("Condición frente al IVA: \n")
            data_fiscal = f"{nombre}, {cond}, CUIT: {cuit}"
        
        return data_fiscal

    def agregar(
        nombre: str = None,
        fecha_pago: tuple = (),
        pago_anterior: tuple = (),
        data_fiscal: str = "Sin información",
        nota: str = "",
        mod: bool = False,
        sync: bool = False
    ):
        
        if not nombre:
            return None
        
        if not fecha_pago:
            fecha_remota = dt.now() - delta(days=90)
            fecha_pago = (fecha_remota.year, fecha_remota.month, fecha_remota.day, 0, 0)

        pago_anterior = fecha_pago
        listado = Listado.load()
        data = listado.alumnos.get(nombre)
        
        if data:
            if not mod:
                print("El alumno ya se encuentra en la base.")
                return None
            else:
                fecha_pago = data["fecha_pago"]
                data_fiscal = data["data_fiscal"]
                nota = data["nota"]
                agrega_cambia = input(
                    f"Data fiscal: {data_fiscal}.\n"\
                    + "Espacio para sobreescribir, enter para conservar.\n"
                )
                
                if agrega_cambia == " ":
                    data_fiscal = Listado.datagen()
                
                agrega_cambia = input(
                    f"Nota: '{nota}'.\n"\
                    + "Espacio para sobreescribir, enter para conservar.\n"
                )
                
                if agrega_cambia == " ":
                    nota = input("Nota: ")
        elif not sync:
                ingreso_manual = input(
                    "Espacio para ingresar data manualmente, enter para parámetros predeterminados.\n"
                )
                if ingreso_manual == " ":
                    print("Data fiscal:")
                    data_fiscal = Listado.datagen()
                    nota = input("Nota: ")

        listado.alumnos[nombre] = {
            "fecha_pago": fecha_pago,
            "data_fiscal": data_fiscal,
            "nota": nota,
            "pago_anterior": pago_anterior
        }
        Listado.save(listado)
     
    def eliminar(nombre: str):
        listado = Listado.load()
        
        if not listado.alumnos.get(nombre):
            print("El alumno no se encuentra en la base.")
            return None
        
        del listado.alumnos[nombre]
        print(f"Se eliminó a {nombre} de la base.")
        Listado.save(listado)
    
    def pago(nombre, fecha=None):
        listado = Listado.load()
        y = dt.now().year
        
        if not listado.alumnos.get(nombre):
            print("El alumno no se encuentra en la base.")
            return None
        
        if not fecha:
            m, d, y = dt.now().month, dt.now().day, dt.now().year
        else:
            m, d, y = fecha
        
        listado.alumnos[nombre]["pago_anterior"] = listado.alumnos[nombre]["fecha_pago"]
        listado.alumnos[nombre]["fecha_pago"] = (y,m,d,23,59)
        Listado.save(listado)
        print("Guardado.")
        return None

    def data_pago(alumnos=None):
        from manager import t2d
        """
        Prints:
            data fiscal, fecha de último pago y notas asociadas a uno o más alumnos según figura en la base local.
        """
        diccionario = Listado.load().alumnos
        if not alumnos and not isinstance(alumnos,list): # para distinguir entre una búsqueda que no arrojó resultados y la búsqeda vacía que pretende obtener todos los resultados.
            alumnos = Listado.buscar()

        if alumnos:
            diccionario = {alumno: diccionario.get(alumno) for alumno in alumnos}

        for alumno, datos in diccionario.items():
            print("--------------------------------------------\n"\
                + f"{alumno}\n"\
                + f"Data fiscal: {datos.get('data_fiscal')}\n"\
                + f"Fecha de pago: {t2d(datos.get('fecha_pago')).strftime('%d/%m/%Y')}\n"\
                + f"Pago anterior: {t2d(datos.get('pago_anterior')).strftime('%d/%m/%Y')}\n"\
                + f"Nota: {datos.get('nota')}\n"
                + "--------------------------------------------\n"
            )


# ejemplo de lista de alumnos cargada en base.alumnos:
# alumnos = {
#     'Katia': {
#         'fecha_pago': (2023, 6, 1, 23, 59),
#         'data_fiscal': 'Consumidor Final',
#         'nota': 'Colocar "honorarios" en el concepto.',
#         'pago_anterior': (2023, 6, 1, 23, 59)
#     },
#     'Mica 7': {
#         'fecha_pago': (2023, 6, 9, 23, 59),
#         'data_fiscal': 'Consumidor Final',
#         'nota': '',
#         'pago_anterior': (2023, 6, 9, 23, 59)
#     }
# }






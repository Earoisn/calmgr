from datetime import datetime as dt, timedelta as delta
import pickle


class Listado:
    """
    Clase utilizada para modificar la base de datos de alumnos. Puede agregar o borrar a un alumno, modificar la última fecha de pago, la data fiscal y agregar notas.
    Methods:

        load(): carga del directorio predeterminado y devuelve la base de datos como un objeto de esta clase

        save(base): guarda el objeto que se pasa como argumento en el directorio por defecto, sobreescribiendo el anterior. Crea un backup que también se sobreescribirá con la próxima modificación.

        agregar(nombre, fecha de último pago (yyyy,m,d,H,M), data_fiscal en str, nota en str)

        eliminar(nombre)

        pago(alumno[, (yyyy,m,d)]) asigna la fecha actual o la tupla opcional como último pago.
    """

    def __init__(self,base = dict()):
        self.alumnos = base
    
    def backup():
        listado = Listado.load()
        
        with open("D:\\code\\gcloud\\Calendar\\base_backup.pickle", "wb") as b:
            pickle.dump(listado, b)
    
    def load(base = None):
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
        ahora = n2a(dt.now().replace(hour = 23, minute = 59))
        dif = delta(days = 30)
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
                Listado.agregar(nombre = alumno, sync = True)
                print(f"Se agregó a {alumno} a la base")
            print(f"Se completó la actualización de la base de datos.")
            return None

    def buscar(mod = False, base = None):
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
        
        if mod: return [nombre.capitalize() for nombre in nombres]

        if len(encontrados) == 0:
            print("No se encontró información para está búsqueda en la base de datos.")
            return []
        elif len(encontrados) == len(exactos):
            return encontrados
        else:
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

        return alumnos

    def datagen():
        nombre = input("Nombre y apellido: \n")
        cuit = input("CUIT sin guiones ni espacios: \n")
        cond = input("Condición frente al IVA: \n")
        data_fiscal = f"{nombre}, {cond}, CUIT: {cuit}"
        return data_fiscal

    def agregar(
        nombre: str = None, 
        fecha_pago: tuple = (), 
        data_fiscal: str = "Sin información", 
        nota: str = "",
        mod: bool = False,
        sync: bool = False
    ):
        
        if not nombre:
            return None
        
        if not fecha_pago:
            fecha_remota = dt.now()-delta(days = 90)
            fecha_pago = (fecha_remota.year, fecha_remota.month, fecha_remota.day, 0, 0)
        
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
            "nota": nota
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
    
    def pago(nombre,fecha = None):
        listado = Listado.load()
        y = dt.now().year
        
        if not listado.alumnos.get(nombre):
            print("El alumno no se encuentra en la base.")
            return None
        
        if not fecha:
            m, d = dt.now().month, dt.now().day
        else:
            m, d = fecha
        
        listado.alumnos[nombre]["fecha_pago"] = (y,m,d,23,59)
        Listado.save(listado)
        print("Guardado.")
        return None

    def data_pago(alumnos = None):
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
                + f"Nota: {datos.get('nota')}\n"
                + "--------------------------------------------\n"
            )


# ejemplo de lista de alumnos cargada en base.alumnos:
# alumnos = {
#     'Lucas 2': {
#         'fecha_pago': (2023, 5, 4, 0, 0), 
#         'data_fiscal': 'Consumidor Final', 
#         'nota': ''
#     }, 
#     'Katia': {
#         'fecha_pago': (2023, 4, 30, 0, 0), 
#         'data_fiscal': 'Consumidor Final', 
#         'nota': ''
#     }, 
#     'Mica 7': {
#         'fecha_pago': (2023, 4, 30, 0, 0), 
#         'data_fiscal': 'Consumidor Final', 
#         'nota': ''
#     }, 
#     'Pedro 3': {
#         'fecha_pago': (2023, 5, 4, 0, 0), 
#         'data_fiscal': 'Consumidor Final', 
#         'nota': ''
#     }, 
#     'Pedro 2': {
#         'fecha_pago': (2023, 5, 4, 0, 0), 
#         'data_fiscal': 'Consumidor Final', 
#         'nota': ''
#     }, 
#     'Mía 2': {
#         'fecha_pago': (2023, 5, 16, 0, 0), 
#         'data_fiscal': 'Consumidor Final', 
#         'nota': ''
#     }, 
#     'Felipe 6': {
#         'fecha_pago': (2023, 5, 5, 0, 0), 
#         'data_fiscal': 'Consumidor Final', 
#         'nota': ''
#     }, 
#     'Ame': {
#         'fecha_pago': (2023, 4, 25, 0, 0), 
#         'data_fiscal': 'Consumidor Final', 
#         'nota': ''
#     }, 
#     'Félix': {
#         'fecha_pago': (2023, 4, 26, 0, 0), 
#         'data_fiscal': 'Garfunkel Griselda Lorena, '\
#                         + 'IVA Responsable Inscripto, '\
#                         + 'CUIT 27214776230.', 
#         'nota': "Colocar 'honorarios' en el concepto de la factura."
#     }, 
#     'Mateo 4': {
#         'fecha_pago': (2023, 4, 30, 0, 0), 
#         'data_fiscal': 'Consumidor Final', 
#         'nota': ''
#     }, 
#     'Nicolás 14': {
#         'fecha_pago': (2023, 5, 2, 0, 0), 
#         'data_fiscal': 'Consumidor Final', 
#         'nota': ''
#     }, 
#     'Benjamín 2': {
#         'fecha_pago': (2023, 5, 5, 0, 0), 
#         'data_fiscal': 'Consumidor Final', 
#         'nota': ''
#     }, 
#     'Martina 5': {
#         'fecha_pago': (2023, 4, 27, 0, 0), 
#         'data_fiscal': 'Consumidor Final', 
#         'nota': ''
#     }, 
#     'Tomás 10': {
#         'fecha_pago': (2023, 5, 2, 0, 0), 
#         'data_fiscal': 'Curchmar Ivana, Responsable Monotributo, CUIT 27243142003', 'nota': ''
#     }, 
#     'Maxi': {
#         'fecha_pago': (2023, 5, 31, 0, 0), 
#         'data_fiscal': 'Consumidor Final', 
#         'nota': ''
#     }, 
#     'Olivia': {
#         'fecha_pago': (2023, 5, 1, 0, 0), 
#         'data_fiscal': 'Consumidor Final', 
#         'nota': ''
#     }, 
#     'Lucía 5': {'fecha_pago': (2023, 5, 1, 0, 0), 
#         'data_fiscal': 'Consumidor Final', 
#         'nota': ''
#     }, 
#     'Amalia 2': {'fecha_pago': (2023, 5, 5, 0, 0), 
#         'data_fiscal': 'Andreucci Paula, IVA Responsable Inscripto, CUIT 27228170785', 'nota': ''
#     }, 
#     'Delfina 3': {
#         'fecha_pago': (2023, 5, 1, 0, 0), 
#         'data_fiscal': 'Consumidor Final', 
#         'nota': ''
#     }, 
#     'Julia 4': {
#         'fecha_pago': (2023, 5, 1, 0, 0), 
#         'data_fiscal': 'Consumidor Final', 
#         'nota': ''
#     }, 
#     'Lucía 6': {
#         'fecha_pago': (2023, 5, 1, 0, 0), 
#         'data_fiscal': 'Consumidor Final', 
#         'nota': ''
#     }, 
#     'Lucas 7': {
#         'fecha_pago': (2023, 5, 3, 0, 0), 
#         'data_fiscal': 'Consumidor Final', 
#         'nota': ''
#     }, 
#     'Clara 2': {
#         'fecha_pago': (2023, 4, 26, 0, 0), 
#         'data_fiscal': 'Consumidor Final', 
#         'nota': ''
#     }, 
#     'Mica 5': {
#         'fecha_pago': (2023, 5, 8, 0, 0), 
#         'data_fiscal': 'Consumidor Final', 
#         'nota': ''
#     }, 
#     'Matilda': {
#         'fecha_pago': (2023, 5, 8, 0, 0), 
#         'data_fiscal': 'Consumidor Final', 
#         'nota': ''
#     }
# }
# lista = Listado(alumnos)
# Listado.save(lista)
# lista = Listado.load()
# print(lista.alumnos)
# Listado.sync()




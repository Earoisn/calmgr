from datetime import datetime as dt
import pickle

class Listado:
    """
    Clase utilizada para modificar la base de datos de alumnos. Puede agregar o borrar a un alumno y puede modificar la última fecha de pago o la data fiscal.
    Methods:

        load(): carga del directorio predeterminado y devuelve la base de datos como un objeto de esta clase

        save(base): guarda el objeto que se pasa como argumento en el directorio por defecto, sobreescribiendo el anterior. Crea un backup que también se sobreescribirá con la próxima modificación.

        agregar_alumno(nombre, fecha de último pago (yyyy,m,d,H,M), data_fiscal en str)
        eliminar_alumno(nombre)

        pago(alumno[, (yyyy,m,d)]) asigna la fecha actual o la tupla opcional como último pago.
    """

    def __init__(self,base = dict()):
        self.alumnos = base
    
    def load():
        with open("D:\\code\\gcloud\\Calendar\\base.pickle", "rb") as b:
            lista = pickle.load(b)
            return lista
    
    def save(base):
        backup = Listado.load()
        with open("D:\\code\\gcloud\\Calendar\\base_backup.pickle", "wb") as b:
            pickle.dump(backup, b)
            print("Se hizo un backup de la base.")
        with open("D:\\code\\gcloud\\Calendar\\base.pickle", "wb") as b:
            pickle.dump(base, b)
            return

    def agregar_alumno(nombre: str = None, 
                       fecha_pago: tuple = (dt.now().year, dt.now().month, dt.now().day, 0, 0), 
                       data_fiscal: str = "Consumidor Final"):
        listado = Listado.load()
        if listado.alumnos.get(nombre):
            print("El alumno ya se encuentra en la base.")
            return None
        if not nombre:
            return None
        listado.alumnos[nombre] = {"fecha_pago": fecha_pago, "data_fiscal": data_fiscal}
        Listado.save(listado)
    
    def eliminar_alumno(nombre: str):
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
            m,d = dt.now().month, dt.now().day
        else:
            m,d = fecha
        listado.alumnos[nombre]["fecha_pago"] = (y,m,d,0,0)
        Listado.save(listado)
        print("Guardado.")
        return None

       

# ejemplo de lista de alumnos cargada en base.alumnos:
# alumnos = {
#             "Lucas 2":    {"fecha_pago": (2023, 5, 4, 0, 0),  "data_fiscal": "Consumidor Final"}, 
#             "Katia":      {"fecha_pago": (2023, 4, 30, 0, 0), "data_fiscal": "Consumidor Final"}, 
#             "Mica 7":     {"fecha_pago": (2023, 4, 30, 0, 0), "data_fiscal": "Consumidor Final"}, 
#             "Pedro 3":    {"fecha_pago": (2023, 5, 4, 0, 0),  "data_fiscal": "Consumidor Final"}, 
#             "Pedro 2":    {"fecha_pago": (2023, 5, 4, 0, 0),  "data_fiscal": "Consumidor Final"}, 
#             "Mía 2":      {"fecha_pago": (2023, 5, 4, 0, 0),  "data_fiscal": "Consumidor Final"}, 
#             "Felipe 6":   {"fecha_pago": (2023, 5, 1, 0, 0),  "data_fiscal": "Consumidor Final"}, 
#             "Ame":        {"fecha_pago": (2023, 4, 25, 0, 0), "data_fiscal": "Consumidor Final"}, 
#             "Félix":      {"fecha_pago": (2023, 4, 3, 0, 0),  "data_fiscal": "Garfunkel Griselda Lorena, IVA Responsable Inscripto, CUIT 27214776230"}, 
#             "Mateo 4":    {"fecha_pago": (2023, 4, 3, 0, 0),  "data_fiscal": "Consumidor Final"}, 
#             "Nicolás 14": {"fecha_pago": (2023, 5, 2, 0, 0),  "data_fiscal": "Consumidor Final"}, 
#             "Benjamín 2": {"fecha_pago": (2023, 5, 2, 0, 0),  "data_fiscal": "Consumidor Final"}, 
#             "Martina 5":  {"fecha_pago": (2023, 4, 4, 0, 0),  "data_fiscal": "Consumidor Final"}, 
#             "Tomás 10":   {"fecha_pago": (2023, 5, 2, 0, 0),  "data_fiscal": "Curchmar Ivana, Responsable Monotributo, CUIT 27243142003"}, 
#             "Maxi":       {"fecha_pago": (2023, 5, 31, 0, 0), "data_fiscal": "Consumidor Final"}, 
#             "Olivia":     {"fecha_pago": (2023, 5, 1, 0, 0),  "data_fiscal": "Consumidor Final"}, 
#             "Lucía 5":    {"fecha_pago": (2023, 5, 1, 0, 0),  "data_fiscal": "Consumidor Final"}, 
#             "Amalia 2":   {"fecha_pago": (2023, 5, 1, 0, 0),  "data_fiscal": "Andreucci Paula, IVA Responsable Inscripto, CUIT 27228170785"}, 
#             "Delfina 3":  {"fecha_pago": (2023, 5, 1, 0, 0),  "data_fiscal": "Consumidor Final"}, 
#             "Julia 4":    {"fecha_pago": (2023, 5, 1, 0, 0),  "data_fiscal": "Consumidor Final"}, 
#             "Lucía 6":    {"fecha_pago": (2023, 5, 1, 0, 0),  "data_fiscal": "Consumidor Final"}, 
#             "Lucas 7":    {"fecha_pago": (2023, 5, 3, 0, 0),  "data_fiscal": "Consumidor Final"}, 
#             "Clara 2":    {"fecha_pago": (2023, 4, 3, 0, 0),  "data_fiscal": "Consumidor Final"}
#             }

# lista = Listado(alumnos)
# Listado.save(lista)
# lista = Listado.load()
# print(lista.alumnos)
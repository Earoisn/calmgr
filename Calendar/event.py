from datetime import datetime as dt

PRECIO = 18000

class Event:
    def __init__(self, stream, precio=(PRECIO/60)):
        días = {
            0: "lunes",
            1: "martes",
            2: "miércoles",
            3: "jueves",
            4: "viernes",
            5: "sábado",
            6: "domingo"
        }
        self.inicio = dt.fromisoformat(stream["start"]["dateTime"])
        self.fin = dt.fromisoformat(stream["end"]["dateTime"])
        self.nombre = stream["summary"]
        self.es_grupal = " y " in self.nombre
        self.es_clase = False
        
        if "Clase " in self.nombre:
            self.es_clase = True
            self.alumno = self.nombre.split("Clase ")[1:]
            
            if self.es_grupal:
                self.alumno = self.alumno[0].split(" y ")
        else:
            self.alumno = ["No es clase"]
        
        self.es_finde = False
        
        if self.inicio.weekday() == 5 or self.inicio.weekday() == 6:
            self.es_finde = True
        
        self.día = días[self.inicio.weekday()]
        self.ini_a = self.inicio.year
        self.ini_d = self.inicio.day
        self.ini_m = self.inicio.month
        self.ini_h = self.inicio.hour
        self.ini_min = self.inicio.minute
        self.fin_d = self.fin.day
        self.fin_m = self.fin.month
        self.fin_h = self.fin.hour
        self.fin_min = self.fin.minute
        self.durac = (self.fin - self.inicio).seconds / 60
        self.dur_hora = self.durac // 60
        self.dur_minuto = self.durac % 60
        self.precio = self.durac * precio
        
        if self.es_grupal:
            self.precio *= 0.8
        
        self.clases = []
    
    
    def agrega_clase(self, d, m, a, ini_h, ini_min, fin_h, fin_min, precio):
        self.clases.append((d, m, a, ini_h, ini_min, fin_h, fin_min, precio))

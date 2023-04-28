import datetime
class Evento:
    def __init__(self,stream):
        self._inicio = stream["start"]["dateTime"]
        self._fin = stream["end"]["dateTime"]
        self.nombre_evento = stream["summary"]

        self.iniDT = datetime.datetime.strptime(self._inicio, "%Y-%m-%dT%H:%M:%S-03:00")
        self.finDT = datetime.datetime.strptime(self._fin, "%Y-%m-%dT%H:%M:%S-03:00")

        self.esFinde = False
        if self.iniDT.weekday() == 5 or self.iniDT.weekday() == 6:
            self.esFinde = True
        self.iniD = self.iniDT.day
        self.iniM = self.iniDT.month
        self.iniH = self.iniDT.hour
        self.iniMin = self.iniDT.minute
        self.iniReal = self.iniH*60+self.iniMin
        self.finD = self.finDT.day
        self.finM = self.finDT.month
        self.finH = self.finDT.hour
        self.finMin = self.finDT.minute
        self.finReal = self.finH*60+self.finMin

        self.durac = (self.finReal) - (self.iniReal)

        self.durHORA = self.durac//60
        self.durMINUTO = self.durac%60

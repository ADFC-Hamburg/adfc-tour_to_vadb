import datetime
import enum
from dateutil import tz

def invmap(my_map:dict) -> dict:
    inv_map = {}
    for k, v in my_map.items():
        inv_map[v] = k
    return inv_map

class Status(enum.Enum):
    Published = 1
    Cannceld = 2

class Kategorie(enum.Enum):
    Tagestour = 1
    Mehrtagestour = 2
    Halbtagestour = 3
    Feierabendtour = 4
    Rad_Reise = 5


KATEGORIE_DICT = {
    'Tagestour': Kategorie.Tagestour,
    'Mehrtagestour': Kategorie.Mehrtagestour,
    'Halbtagestour': Kategorie.Halbtagestour,
    'Feierabendtour': Kategorie.Feierabendtour,
    'Rad-Reise': Kategorie.Rad_Reise
}


class RadTypEignung(enum.Enum):
    Alltagsrad = 1
    Mountainbike = 2
    Rennrad = 3
    Liegerad = 4
    Pedelec = 5
    Tandem = 6
    Anhaenger = 7


RADTYPEN_DICT = {
    'Alltagsrad': RadTypEignung.Alltagsrad,
    'Mountainbike': RadTypEignung.Mountainbike,
    'Rennrad': RadTypEignung.Rennrad,
    'Liegerad': RadTypEignung.Liegerad,
    'Pedelec': RadTypEignung.Pedelec,
    'Tandem': RadTypEignung.Tandem,
    'Anhänger / Dreirad': RadTypEignung.Anhaenger
}


class Zielgruppen(enum.Enum):
    Familien = 1
    Senioren = 2
    Menschen_mit_Behinderungen = 3
    Kinder = 4
    Jundendliche = 5


ZIELGRUPPEN_DICT = {
    'Familien': Zielgruppen.Familien,
    'Senioren': Zielgruppen.Senioren,
    'Menschen mit Behinderungen': Zielgruppen.Menschen_mit_Behinderungen,
    'Touren für Kinder (bis 14 Jahren)': Zielgruppen.Kinder,
    'Touren für Jugendliche (15-18 Jahren)': Zielgruppen.Jundendliche
}


class Thema(enum.Enum):
    Kultur = 1
    Natur = 2
    Stadt_erleben = 3
    Neubuerger = 4


THEMA_DICT = {
    'Kultur': Thema.Kultur,
    'Natur': Thema.Natur,
    'Stadt entdecken / erleben': Thema.Stadt_erleben,
    'Neubürger-/Kieztouren': Thema.Neubuerger,
}


class Eigenschaften(enum.Enum):
    Bahnfahrt = 1
    Einkehr = 2
    Picknik = 3
    Badepause = 4
    Zusatzkosten = 5


EIGENSCHAFTEN_DICT = {
    'Bahnfahrt': Eigenschaften.Bahnfahrt,
    'Einkehr in Restauration': Eigenschaften.Einkehr,
    'Picknik': Eigenschaften.Picknik,
    'Badepause': Eigenschaften.Badepause,
    'Zusatzkosten': Eigenschaften.Zusatzkosten
}


class ADFCTermin:
    def __init__(self,
                 id: str,
                 start: datetime.datetime,
                 ende: datetime.datetime,
                 status: str,
                 title: str,
                 shortDesc: str,
                 descr: str,
                 bookingLink: str,
                 laenge: str,
                 minPreis: float,
                 maxPreis: float,
                 adfcUrl: str,
                 imageUrl: str,
                 imageCopyright: str,
                 startLat: float,
                 startLon: float,
                 startName: str,
                 startStreet: str,
                 startCity: str,
                 startZipCode: str,
                 kategorie: Kategorie,
                 radTypen: list[RadTypEignung],
                 zielgruppen: list[Zielgruppen],
                 thema: list[Thema],
                 eigenschaften: list[Eigenschaften],
                 changedDate: datetime.datetime,
                 publishDate: datetime.datetime
                 ):
        self.id = id
        self.start = start
        self.ende = ende
        self.status = status
        self.title = title
        self.shortDesc = shortDesc
        self.desc = descr
        self.bookingLink = bookingLink
        self.laenge = laenge
        self.minPreis = minPreis
        self.maxPreis = maxPreis
        self.adfcUrl = adfcUrl
        self.imageUrl = imageUrl
        self.imageCopyright = imageCopyright
        self.startLat = startLat
        self.startLon = startLon
        self.startName = startName
        self.startStreet = startStreet
        self.startCity = startCity
        self.startZipCode =startZipCode
        self.kategorie = kategorie
        self.radTypen = radTypen
        self.zielgruppen = zielgruppen
        self.thema = thema
        self.eigenschaften = eigenschaften
        self.changedDate = changedDate
        self.publishDate = publishDate

    def getId(self) -> str:
        return self.id

    def getDurationInMinutes(self) -> int:
        return ((self.ende-self.start).total_seconds()/60)

    def getStartLocalTime(self) -> str:
        berlin_zone = tz.gettz('Europe/Berlin')
        return self.start.astimezone(berlin_zone)

    def isCannceld(self) -> bool:
        return (self.status == Status.Cannceld)

    def getTitle(self) -> str:
        return self.title

    def getShortDescr(self) -> str:
        return self.shortDesc

    def getKategoryAsString(self) -> str:
        return invmap(KATEGORIE_DICT)[self.kategorie]

    def getRadTypenAsStringList(self) -> list:
        rev_map= invmap(RADTYPEN_DICT)
        rtn=[]
        for ele in self.radTypen:
            rtn.append(rev_map[ele])
        #print(rtn)
        return rtn

    def getTourLaenge(self) -> str:
        return self.laenge

    def getZielgruppenAsStringList(self) -> list:
        rev_map= invmap(ZIELGRUPPEN_DICT)
        rtn=[]
        for ele in self.zielgruppen:
            rtn.append(rev_map[ele])
        return rtn

    def getAdfcUrl(self) -> str:
        return self.adfcUrl

    def getMinPreis(self) -> float:
        return self.minPreis

    def getMaxPreis(self) -> float:
        return self.maxPreis

    def getImageUrl(self) -> str:
        return self.imageUrl

    def getImageCopyright(self) -> str:
        return self.imageCopyright

    def getStartLat(self) -> float:
        return self.startLat

    def getStartLon(self) -> float:
        return self.startLon

    def getStartName(self) -> str:
        return self.startName

    def getStartStreet(self) -> str:
        return self.startStreet

    def getStartZipCode(self) -> str:
        return self.startZipCode

    def getStartCity(self) -> str:
        return self.startCity

    def getBookingLink(self) -> str:
        return self.bookingLink

    def getChangedDate(self) -> datetime:
        return self.changedDate

    def getPublishDate(self) -> datetime:
        return self.publishDate

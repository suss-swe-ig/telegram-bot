import shelve

class TelegramGroup:
    def __init__(self, db: shelve.Shelf, unitCode:str) -> None:
        self._db = db
        self._unitCode = unitCode
from typing import List

import shelve

def _validUnitCode(unitCode:str) -> bool:
    return len(unitCode) == 6 and unitCode[:3].isalpha() and unitCode[3:].isnumeric()

class MalformedUnitCodeException(Exception):
    def __init__(self, unitCode:str) -> None:
        Exception.__init__(self, f"{unitCode} is a malformed unit code")

class NoTelegramGroupException(Exception):
    def __init__(self, unitCode:str):
        Exception.__init__(self, f"No known telegram group for {unitCode}")

class TelegramGroup:

    def __init__(self, unitCode:str, unitName:str, link:str, db:shelve.Shelf) -> None:
        self._unitCode = unitCode.upper()
        self._unitName = unitName
        self._link = link
        self._db = db

    @property
    def unitCode(self) -> str:
        return self._unitCode
    
    @property
    def unitName(self) -> str:
        return self._unitName
    
    @property
    def link(self) -> str:
        return self._link
    
    @property
    def prefix(self) -> str:
        return self._unitCode[:3]
    
    def __lt__(self, other:"TelegramGroup") -> bool:
        return self._unitCode < other.unitCode
    
    def __eq__(self, other:"TelegramGroup") -> bool:
        return self._unitCode == other.unitCode
    
    def __gt__(self, other:"TelegramGroup") -> bool:
        return self._unitCode == other.unitCode

class Persistence:
    def __init__(self, db: shelve.Shelf):
        self._db = db
    
    def getTelegramGroup(self, unitCode:str) -> TelegramGroup:
        if _validUnitCode(unitCode):
            if unitCode in self:
                unitName, link = self._db[unitCode]
                return TelegramGroup(self._db, unitCode, unitName, link)
            raise NoTelegramGroupException(unitCode)
        raise MalformedUnitCodeException(unitCode)
    
    def __contains__(self, unitCode:str) -> bool:
        return unitCode.upper() in self._db
    
    def getTelegramGroups(self) -> List[str]:
        tgs = []
        for unitCode in self._db:
            unitName, link = self._db[unitCode]
            tgs.append(TelegramGroup(unitCode, unitName, link, self._db))
        return tgs
    
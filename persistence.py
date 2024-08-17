from typing import List, Tuple

import shelve

def _validUnitCode(unitCode:str) -> bool:
    return len(unitCode) == 6 and unitCode[:3].isalpha() and unitCode[3:].isnumeric()

class MalformedUnitCodeException(Exception):
    def __init__(self, unitCode:str) -> None:
        Exception.__init__(self, f"{unitCode} is a malformed unit code")

class NoTelegramGroupException(Exception):
    def __init__(self, unitCode:str) -> None:
        Exception.__init__(self, f"No known telegram group for {unitCode}")

class BadTelegramLinkException(Exception):
    def __init__(self, unitCode:str, link:str) -> None:
        Exception.__init__(self, f"Bad link {link} given for {unitCode}")

class BadUnitNameException(Exception):
    def __init__(self, unitCode:str):
        Exception.__init__(self, f"Bad Unit Name for {unitCode}")

class TelegramGroup:
    def __init__(self, unitCode:str, unitName:str, link:str, p:"Persistence") -> None:
        self._unitCode = unitCode.upper()
        self._unitName = unitName
        self._link = link
        self._p = p
        self._deleted = False
    
    def updateUnitName(self, unitName:str) -> None:
        if self._deleted:
            raise NoTelegramGroupException(self._unitCode)
        if len(unitName) == 0:
            raise BadUnitNameException(self._unitCode)
        try:
            _, link = self._db[self._unitCode] 
        except KeyError:
            raise NoTelegramGroupException(self._unitCode)
        else:
            self._db[self._unitCode] = (unitName, link)
            self._unitName = unitName

    def updateLink(self, link:str) -> None:
        if self._deleted:
            raise NoTelegramGroupException(self._unitCode)
        if not link.startswith("https://t.me/"):
            raise BadTelegramLinkException(self._unitCode, link)
        try:
            unitName, _ = self._db[self._unitCode]
        except KeyError:
            raise NoTelegramGroupException(self._unitCode)
        else:
            self._db[self._unitCode] = (unitName, link)

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
        return self._unitCode > other.unitCode
    
    def __del__(self):
        if not self._deleted:
            self._deleted = True
            self._p.deleteTelegramGroup(self) 

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
            tgs.append(TelegramGroup(unitCode, unitName, link, self))
        return tgs
    
    def addTelegramGroup(self, unitCode:str, unitName:str, link:str) -> TelegramGroup:
        if not _validUnitCode(unitCode):
            raise MalformedUnitCodeException(unitCode)
        if not link.startswith("https://t.me/"):
            raise BadTelegramLinkException(unitCode, link)
        if len(unitName) == 0:
            raise BadUnitNameException(unitCode)
        self._db[unitCode] = (unitName, link)
        return TelegramGroup(unitCode, unitName, link, self)
    
    def __getitem__(self, unitCode:str):
        if unitCode in self._db:
            return self._db[unitCode]
        raise KeyError()
    
    def __setitem__(self, unitCode:str, values:Tuple[str,str]):
        self._db[unitCode] = values
    
    def deleteTelegramGroup(self, tg: TelegramGroup) -> bool:
        try:
            del self._db[tg.unitCode]
        except KeyError:
            return False
        else:
            return True
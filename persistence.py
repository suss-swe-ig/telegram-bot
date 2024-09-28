from typing import List, Tuple

import shelve

from singleton import Singleton


_DATABASE: "SingletonDatabase" = None

def setup(dbname:str, admins:List[str]) -> None:
    global _DATABASE
    _DATABASE = SingletonDatabase(dbname, admins)

class DatabaseNotReadyException(Exception):
    pass

def getDatabase() -> "SingletonDatabase":
    global _DATABASE
    if _DATABASE is None:
        raise DatabaseNotReadyException()
    return _DATABASE

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
    def __init__(self, unitCode:str, unitName:str, link:str) -> None:
        self._unitCode = unitCode.upper()
        self._unitName = unitName
        self._link = link
        self._db = getDatabase()
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

    def delete(self):
        try:
            self._db.deleteTelegramGroup(self)
        except NoTelegramGroupException as e:
            raise e
        else:
            self._deleted = True

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

class SingletonDatabase(Singleton):
    def __init__(self, dbname:str, admins:List[str]):
        self._db = shelve.open(dbname)
        self._admins = admins
    
    def getAdmins(self) -> List[str]:
        return self._admins
    
    def getTelegramGroup(self, unitCode:str) -> TelegramGroup:
        unitCode = unitCode.upper()
        if _validUnitCode(unitCode):
            if unitCode in self._db:
                unitName, link = self._db[unitCode]
                return TelegramGroup(unitCode, unitName, link)
            raise NoTelegramGroupException(unitCode)
        raise MalformedUnitCodeException(unitCode)
    
   
    def getTelegramGroups(self) -> List[TelegramGroup]:
        tgs = []
        for unitCode in self._db:
            unitName, link = self._db[unitCode]
            tgs.append(TelegramGroup(unitCode, unitName, link))
        return tgs
    
    def addTelegramGroup(self, unitCode:str, unitName:str, link:str) -> TelegramGroup:
        if not _validUnitCode(unitCode):
            raise MalformedUnitCodeException(unitCode)
        if not link.startswith("https://t.me/"):
            raise BadTelegramLinkException(unitCode, link)
        if len(unitName) == 0:
            raise BadUnitNameException(unitCode)
        self._db[unitCode] = (unitName, link)
        return TelegramGroup(unitCode, unitName, link)
    
    def __getitem__(self, unitCode:str):
        if unitCode in self._db:
            return self._db[unitCode]
        raise KeyError()
    
    def __setitem__(self, unitCode:str, values:Tuple[str,str]):
        self._db[unitCode] = values
    
    def deleteTelegramGroup(self, tg: TelegramGroup) -> None:
        try:
            del self._db[tg.unitCode]
        except KeyError:
            raise NoTelegramGroupException()

    def getBlockedUsers(self) -> dict[str, str]:
        return self._db.get('rbac:blocked_user', {})

    def updateBlockedUsers(self, users: dict[str, str]) -> None:
        self._db['rbac:blocked_user'] = users

    def getRoles(self) -> dict[str, object]:
        return self._db.get('rbac:role', {})

    def updateRoles(self, roles: dict[str, object]) -> None:
        self._db['rbac:role'] = roles

    def getPermissions(self) -> dict[str, object]:
        return self._db.get('rbac:perm', {})

    def updatePermissions(self, perms: dict[str, object]) -> None:
        self._db['rbac:perm'] = perms

    def getUserRoleMap(self) -> dict[str, set[str]]:
        return self._db.get('rbac:role_perm', {})

    def updateUserRoleMap(self, userRoleMap: dict[str, set[str]]) -> None:
        self._db['rbac:role_perm'] = userRoleMap

    def getRolePermMap(self) -> dict[str, set[tuple[str, str]]]:
        return self._db.get('rbac:user_perm', {})

    def updateRolePermMap(self, rolePermMap: dict[str, set[tuple[str, str]]]) -> None:
        self._db['rbac:role_perm'] = rolePermMap

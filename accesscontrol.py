from persistence import getDatabase

from dataclasses import dataclass
from typing import Iterable, Optional


@dataclass
class Role:
    name: str
    desc: str


@dataclass
class Permission:
    name: str
    desc: str
    obj_name: str
    oper_name: str


class InvalidUserError(Exception):
    def __init__(self, user_name: str, msg: Optional[str] = None):
        if not msg:
            msg = f"User '{user_name}' is invalid." if user_name else "Invalid user."
        super().__init__(msg)
        self.user_name = user_name


class InvalidPermissionError(Exception):
    def __init__(self, perm: tuple[str, str], msg: Optional[str] = None):
        obj_name, oper_name = perm
        if not msg:
            msg = f"Permission {obj_name}:{oper_name} is invalid."
        super().__init__(msg)
        self.perm = perm


def _to_role_name(role: Role | str) -> str:
    match role:
        case Role(name):
            return name
        case str():
            return role
        case _:
            raise TypeError("Must be either a string or Role.")


def _to_perm_tuple(perm: Permission | tuple[str, str]) -> tuple[str, str]:
    match perm:
        case Permission(_, _, obj_name, oper_name):
            return obj_name, oper_name
        case (obj_name, oper_name):
            return obj_name, oper_name
        case _:
            raise TypeError("Must be either a string or Permission.")
        

def get_roles() -> dict[str, Role]:
    """Returns the list of available roles indexed by name."""
    return getDatabase().getRoles()


def get_role(role_name: str) -> Optional[Role]:
    if not role_name:
        raise ValueError('Role must be specified.')
    return get_roles().get(role_name)


def add_role(role: Role) -> None:
    """Adds a role."""
    db = getDatabase()

    roles = db.getRoles()
    if role.name not in roles:
        roles[role.name] = role

    db.updateRoles(roles)


def remove_role(role: Role | str) -> None:
    role_name = _to_role_name(role)
    if not role_name:
        raise ValueError('Role must be specified.')

    roles = get_roles()
    if role_name not in roles:
        return

    db = getDatabase()

    user_role_map = db.getUserRoleMap()
    role_perm_map = db.getRolePermMap()

    for _, user_roles in user_role_map.items():
        user_roles.remove(role_name)

    del role_perm_map[role_name]
    del roles[role_name]

    db.updateUserRoleMap(user_role_map)
    db.updateRolePermMap(role_perm_map)
    db.updateRoles(roles)


def get_permissions() -> dict[str, Permission]:
    """Returns the list of available permissions indexed by name."""
    return getDatabase().getPermissions()


def get_permission(perm_name: str) -> Optional[Permission]:
    if not perm_name:
        raise ValueError("Permission name must be specified.")

    perms = getDatabase().getPermissions()
    return perms.get(perm_name)


def add_permission(perm: Permission) -> None:
    """Adds a permission."""

    db = getDatabase()

    perms = db.getPermissions()
    if perm.name in perms:
        perm_tuple = _to_perm_tuple(perm)
        raise InvalidPermissionError(perm_tuple, f"Permission '{perm.name}' is already in database.")

    perms[perm.name] = perm

    db.updatePermissions(perms)


def remove_permission(perm: Permission | tuple[str, str]) -> None:
    perm_tuple = _to_perm_tuple(perm)
    if not perm_tuple[0] or not perm_tuple[1]:
        raise InvalidPermissionError(perm_tuple, "Permission is ill-defined.")

    db = getDatabase()

    perms = db.getPermissions()
    perm_name = next(n for n, p in perms.items() if p == perm_tuple)

    if not perm_name:
        raise InvalidPermissionError(perm_tuple, f"Permission {perm_tuple} does not exist.")

    role_perm_map = getDatabase().getRolePermMap()

    for _, role_perms in role_perm_map.items():
        role_perms.discard(perm_tuple)

    del perms[perm_name]

    db.updateRolePermMap(role_perm_map)
    db.updatePermissions(perms)


def get_role_perms(role: Role | str) -> Iterable[tuple[str, str]]:
    role_name = _to_role_name(role)
    if not role_name:
        raise ValueError('Role must be specified.')

    role_perm_map = getDatabase().getRolePermMap()
    return role_perm_map.get(role_name, set())


def add_role_perm(role: Role | str, perm: tuple[str, str]) -> None:
    role_name = _to_role_name(role)
    if not role_name:
        raise ValueError('Role must be specified.')

    if not perm[0] or not perm[1]:
        raise InvalidPermissionError(perm, "Permission is ill-defined.")

    db = getDatabase()

    role_perm_map = db.getRolePermMap()
    perms = role_perm_map.get(role_name, set())
    perms.add(perm)
    role_perm_map[role_name] = perms

    db.updateRolePermMap(role_perm_map)


def remove_role_perm(role: Role | str, perm: tuple[str, str]) -> None:
    role_name = _to_role_name(role)
    if not role_name:
        raise ValueError('Role must be specified.')

    if not perm[0] or not perm[1]:
        raise InvalidPermissionError(perm, "Permission is ill-defined.")

    db = getDatabase()

    role_perm_map = db.getRolePermMap()
    perms = role_perm_map.get(role_name, set())
    perms.remove(perm)
    role_perm_map[role_name] = perms

    db.updateRolePermMap(role_perm_map)


def get_user_roles(user_name: str) -> Iterable[str]:
    if not user_name:
        raise InvalidUserError(user_name, "User name must be specified.")

    user_role_map = getDatabase().getUserRoleMap()
    return user_role_map.get(user_name, [])


def get_user_perms(user_name: str) -> Iterable[tuple[str, tuple[str, str]]]:
    if not user_name:
        raise InvalidUserError(user_name, "User name must be specified.")

    db = getDatabase()

    role_perm_map = db.getRolePermMap()
    for role_name in get_user_roles(user_name):
        for perm in role_perm_map.get(role_name, set()):
            yield role_name, perm


def user_has_role(user_name: str, role: Role | str) -> bool:
    if not user_name:
        raise InvalidUserError(user_name, "User name must be specified.")

    role_name = _to_role_name(role)
    if not role_name:
        raise ValueError('Role must be specified.')

    return any(role_name == role_name2 for role_name2 in get_user_roles(user_name))


def user_has_perm(user_name: str, perm: tuple[str, str]) -> bool:
    if not user_name:
        raise InvalidUserError(user_name, "User name must be specified.")

    return any(perm == perm2 for perm2 in get_user_perms(user_name))


def user_is_blocked(user_name: str) -> bool:
    if not user_name:
        raise InvalidUserError(user_name, "User name must be specified.")

    blocked_users = getDatabase().getBlockedUsers()
    return any(user_name == name for name in blocked_users.keys())


def user_is_authorized(user_name: str, perm: tuple[str, str]) -> bool:
    if user_is_blocked(user_name):
        return False
    return user_has_perm(user_name, perm)


def block_user(user_name: str, reason: str) -> None:
    """Adds the given user to the block list."""

    if not user_name:
        raise InvalidUserError(user_name, "User name must be specified.")

    db = getDatabase()

    blocked_users = db.getBlockedUsers()

    if user_name in blocked_users:
        raise InvalidUserError(user_name, f"User {user_name} is already blocked.")

    blocked_users[user_name] = reason

    db.updateBlockedUsers(blocked_users)


def unblock_user(user_name: str) -> None:
    """Removes the given user from the block list."""

    if not user_name:
        raise InvalidUserError("User name must be specified.")

    db = getDatabase()

    blocked_users = db.getBlockedUsers()

    if user_name not in blocked_users:
        raise InvalidUserError(user_name, f"User {user_name} is not blocked.")

    del blocked_users[user_name]

    db.updateBlockedUsers(blocked_users)

class UKey: pass
class UPrimaryKey(UKey):pass
class UniqueKey(UKey):pass
class UIterableUniqueKey(UKey):pass

ALL_UKEYS = [
    UPrimaryKey,
    UniqueKey,
    UIterableUniqueKey,
]


class UError(Exception):pass
class U_ValidationError(UError):pass
class U_InvalidBehavior(UError):pass
from distutils.spawn import find_executable


class NotInstalledError(FileNotFoundError):
    pass


def where(name: str) -> str:
    path = find_executable(name)
    if not path:
        raise NotInstalledError(name)
    return path

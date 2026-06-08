def parseTagString(string: str) -> tuple[str, ...]:
    return tuple(map(str.strip, ('/' + string).split('/')[-2:]))

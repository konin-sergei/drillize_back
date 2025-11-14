def try_parse_int(val):
    try:
        val = int(val)
    except Exception as e:
        pass
    return val

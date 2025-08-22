def commafy(value):
    try:
        return f"{int(value):,}"
    except Exception:
        try:
            return f"{float(value):,}"
        except Exception:
            return str(value)


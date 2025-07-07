def snake_case_to_pascale_case(inp_text: str) -> str:
    next_up = True
    out = ""
    for char in inp_text:
        if char == "_":
            next_up = True
        elif next_up is True:
            out += char.upper()
        else:
            out += char.lower()
    return out

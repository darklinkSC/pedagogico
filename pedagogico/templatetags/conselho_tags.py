from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None

@register.filter
def nome_curto(nome_completo):
    """
    Retorna apenas o primeiro nome e o primeiro sobrenome.
    Ex: 'João Carlos da Silva' -> 'João Carlos'
    """
    if not nome_completo:
        return ''
    partes = nome_completo.strip().split()
    if len(partes) <= 2:
        return nome_completo
    return f"{partes[0]} {partes[1]}"
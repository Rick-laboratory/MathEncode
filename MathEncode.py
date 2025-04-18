#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Subtile Codierung und Decodierung durch sukzessive Wurzelung

Wenn ohne Argumente gestartet, wird eine Demo mit Beispieltext ausgeführt.
"""
from decimal import Decimal, getcontext, ROUND_FLOOR
import sys

# Globale Präzision setzen
getcontext().prec = 200

# Zeichentabellen: a–z:01–26, A–Z:27–52, ?:53, space:54
zeichen_tabelle = {chr(ord('a')+i): f"{i+1:02d}" for i in range(26)}
zeichen_tabelle.update({chr(ord('A')+i): f"{i+27:02d}" for i in range(26)})
zeichen_tabelle['?'] = '53'
zeichen_tabelle[' '] = '54'
reverse_tabelle = {int(v): k for k, v in zeichen_tabelle.items()}


def build_numeric_code(message: str) -> int:
    """Erzeuge numerischen Code aus Nachricht (mit Groß-/Kleinschreibung)."""
    code_str = ''.join(zeichen_tabelle.get(ch, '00') for ch in message)
    return int(code_str)


def _compute_full_factor(M: Decimal, threshold: Decimal) -> (Decimal, int):
    """Berechnet vollständig präzisen Root-Faktor und r für M."""
    r = 1
    f_full = M
    while f_full >= threshold:
        r += 1
        f_full = M ** (Decimal(1) / Decimal(r))
    return f_full, r


def encode_secret(message: str, threshold: Decimal = Decimal(10)) -> (Decimal, Decimal, Decimal):
    """
    Kodiert Nachricht in drei Faktoren:
      - f1: auf 4 Dezimalstellen gerundeter Wurzel-Faktor (< threshold)
      - f2: Kombination aus r*100 + L
      - f_full: vollständiger, ungerundeter Wurzel-Faktor
    """
    N = build_numeric_code(message)
    L = len(str(N))
    M = Decimal(N) * (Decimal(10) ** L) + L
    f_full, r = _compute_full_factor(M, threshold)
    f1 = f_full.quantize(Decimal('0.0001'), rounding=ROUND_FLOOR)
    f2 = Decimal(r * 100 + L)
    return f1, f2, f_full


def decode_secret(f1: Decimal, f2: Decimal) -> str:
    """Dekodiert Nachricht aus f1 und f2."""
    val = int(f2)
    r = val // 100
    L = val % 100
    M = (f1 ** Decimal(r)).to_integral_value(rounding=ROUND_FLOOR)
    N = int(M // (Decimal(10) ** L))
    code_str = str(N).zfill(L)
    message = ''
    for i in range(0, len(code_str), 2):
        code = int(code_str[i:i+2])
        message += reverse_tabelle.get(code, '?')
    return message


def demo():
    text = "Hallo wie geht es dir mir geht es gut?"
    print(f"Original: {text}")
    f1, f2, f_full = encode_secret(text)
    print(f"Encoded: f1={f1}, f2={f2}")
    decoded = decode_secret(f_full, f2)
    print(f"Decoded: {decoded}")


def print_help():
    print("Usage:")
    print("  secret_codec.py encode <Nachricht>")
    print("  secret_codec.py decode <f1> <f2>")
    print("Ohne Argumente: Demo mit Fall-sensitive Demo.")


def main():
    args = sys.argv[1:]
    if not args:
        demo()
        return
    cmd = args[0].lower()
    if cmd == 'encode' and len(args) >= 2:
        f1, f2, _ = encode_secret(' '.join(args[1:]))
        print(f"Encoded: f1={f1}, f2={f2}")
    elif cmd == 'decode' and len(args) == 3:
        try:
            f1, f2 = Decimal(args[1]), Decimal(args[2])
            decoded = decode_secret(f1, f2)
            print(f"Decoded: {decoded}")
        except Exception as e:
            print(f"Fehler: {e}")
    else:
        print_help()

if __name__ == '__main__':
    main()

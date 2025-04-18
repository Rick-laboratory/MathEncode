#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Subtile Codierung und Decodierung durch sukzessive Wurzelung mit erweitertem Zeichensatz.

Mit Unterstützung für Klein- und Großbuchstaben, Ziffern und gängige Sonderzeichen.
Wenn ohne Argumente gestartet, wird eine Demo ausgeführt.
"""
from decimal import Decimal, getcontext, ROUND_FLOOR
import sys

# Hohe Präzision für interne Rechnungen
getcontext().prec = 200

# Zeichentabellen: Klein-/Großbuchstaben, Ziffern und Sonderzeichen
zeichen_tabelle = {
    **{chr(ord('a')+i): f"{i+1:02d}" for i in range(26)},      # a–z: 01–26
    **{chr(ord('A')+i): f"{i+27:02d}" for i in range(26)},     # A–Z: 27–52
    '?': '53',                                                   # Fragezeichen
    ' ': '54',                                                   # Leerzeichen
    **{d: f"{55+i:02d}" for i, d in enumerate('0123456789')},    # Ziffern 0–9: 55–64
    **{'.': '65', ',': '66', '!': '67', ';': '68', ':': '69',      # Satzzeichen
       '-': '70', '_': '71', '(': '72', ')': '73', '[': '74',     
       ']': '75', '{': '76', '}': '77', '"': '78', "'": '79',   
       '/': '80', '\\': '81', '@': '82', '#': '83', '$': '84',  
       '%': '85', '&': '86', '*': '87', '+': '88', '=': '89',     
       '<': '90', '>': '91', '^': '92', '~': '93', '`': '94'}
}
reverse_tabelle = {int(v): k for k, v in zeichen_tabelle.items()}


def build_numeric_code(message: str) -> int:
    """Erzeuge numerischen Code aus Nachricht mit erweitertem Zeichensatz."""
    code_str = ''.join(zeichen_tabelle.get(ch, '00') for ch in message)
    return int(code_str) if code_str else 0


def _compute_full_factor(M: Decimal, threshold: Decimal) -> (Decimal, int):
    """Berechnet vollständig präzisen Wurzelfaktor und r."""
    r = 1
    f_full = M
    while f_full >= threshold:
        r += 1
        f_full = M ** (Decimal(1) / Decimal(r))
    return f_full, r


def encode_secret(message: str, threshold: Decimal = Decimal(10)) -> (Decimal, Decimal, Decimal):
    """
    Kodiert Nachricht in drei Werten:
      - f1: Wurzelfaktor gerundet auf 4 Dezimalstellen (< threshold)
      - f2: Kombination r*100 + L
      - f_full: vollständiger Wurzelfaktor (interne Genauigkeit)
    """
    N = build_numeric_code(message)
    L = len(str(N))
    M = Decimal(N) * (Decimal(10) ** L) + L
    f_full, r = _compute_full_factor(M, threshold)
    f1 = f_full.quantize(Decimal('0.0001'), rounding=ROUND_FLOOR)
    f2 = Decimal(r * 100 + L)
    return f1, f2, f_full


def decode_secret(f_full: Decimal, f2: Decimal) -> str:
    """Dekodiert Nachricht aus vollständigem Faktor und f2."""
    val = int(f2)
    r = val // 100
    L = val % 100
    M = (f_full ** Decimal(r)).to_integral_value(rounding=ROUND_FLOOR)
    N = int(M // (Decimal(10) ** L))
    code_str = str(N).zfill(L)
    message = ''
    for i in range(0, len(code_str), 2):
        code = int(code_str[i:i+2])
        message += reverse_tabelle.get(code, '?')
    return message


def demo():
    text = "Hallo, Welt! 123wer342342344534545645645675676786"
    print(f"Original: {text}")
    f1, f2, f_full = encode_secret(text)
    print(f"Encoded: f1={f1}, f2={f2}, full={f_full}")
    decoded = decode_secret(f_full, f2)
    print(f"Decoded: {decoded}")


def print_help():
    print("Usage:")
    print("  secret_codec.py encode <Nachricht>")
    print("  secret_codec.py decode <full> <f2>")
    print("Ohne Argumente: Demo mit erweitertem Zeichensatz.")


def main():
    args = sys.argv[1:]
    if not args:
        demo()
        return
    cmd = args[0].lower()
    if cmd == 'encode' and len(args) >= 2:
        f1, f2, f_full = encode_secret(' '.join(args[1:]))
        print(f"Encoded: f1={f1}, f2={f2}, full={f_full}")
    elif cmd == 'decode' and len(args) == 3:
        try:
            f_full = Decimal(args[1])
            f2 = Decimal(args[2])
            decoded = decode_secret(f_full, f2)
            print(f"Decoded: {decoded}")
        except Exception as e:
            print(f"Fehler: {e}")
    else:
        print_help()

if __name__ == '__main__':
    main()

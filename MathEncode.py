#!/usr/bin/env python3
"""Experimental decimal-root text encoding; neither compression nor encryption."""

from __future__ import annotations

import argparse
from decimal import Decimal, DecimalException, ROUND_FLOOR, ROUND_HALF_EVEN, localcontext
from typing import Sequence

ALPHABET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ? "
CHARACTER_CODES = {character: f"{index:02d}" for index, character in enumerate(ALPHABET, 1)}
CODE_CHARACTERS = {index: character for index, character in enumerate(ALPHABET, 1)}
MAX_CHARACTERS = 49  # The historical metadata reserves two decimal digits for length.
MAX_DEGREE = 4096
PREVIEW_QUANTUM = Decimal("0.0001")

# Compatibility aliases for callers of the original module.
zeichen_tabelle = CHARACTER_CODES
reverse_tabelle = CODE_CHARACTERS


def build_numeric_code(message: str) -> int:
    """Convert supported characters into two-digit codes; reject silent data loss."""
    if not 1 <= len(message) <= MAX_CHARACTERS:
        raise ValueError(f"Message length must be 1..{MAX_CHARACTERS} characters.")
    unsupported = set(message) - CHARACTER_CODES.keys()
    if unsupported:
        raise ValueError(f"Unsupported characters: {''.join(sorted(unsupported))!r}")
    return int("".join(CHARACTER_CODES[character] for character in message))


def _compute_full_factor(value: Decimal, threshold: Decimal) -> tuple[Decimal, int]:
    """Compute a sufficiently precise approximation in the caller's local context."""
    if not threshold.is_finite() or threshold <= 1:
        raise ValueError("Threshold must be finite and greater than one.")
    if value < threshold:
        return value, 1
    degree = int((value.ln() / threshold.ln()).to_integral_value(rounding=ROUND_FLOOR)) + 1
    if degree > MAX_DEGREE:
        raise ValueError("Threshold is too close to one for the supported root degree.")
    factor = value ** (Decimal(1) / Decimal(degree))
    while factor >= threshold:
        degree += 1
        if degree > MAX_DEGREE:
            raise ValueError("Required root degree exceeds the supported range.")
        factor = value ** (Decimal(1) / Decimal(degree))
    return factor, degree


def encode_secret(
    message: str, threshold: Decimal = Decimal(10)
) -> tuple[Decimal, Decimal, Decimal]:
    """Return (four-place display preview, metadata, reconstructable decimal root).

    The preview is lossy. Transmit str(root), not the preview or a binary float.
    Metadata remains degree * 100 + the full two-digit character-code length.
    """
    number = build_numeric_code(message)
    digits = 2 * len(message)  # Preserve the leading zero in codes 01..09.
    with localcontext() as context:
        context.prec = 2 * digits + 40
        embedded = Decimal(number) * (Decimal(10) ** digits) + digits
        root, degree = _compute_full_factor(embedded, threshold)
        preview = root.quantize(PREVIEW_QUANTUM, rounding=ROUND_FLOOR)
        metadata = Decimal(degree * 100 + digits)
        # Verify the actual representation returned to the caller.
        if decode_secret(root, metadata) != message:
            raise ArithmeticError("The chosen decimal precision did not preserve the message.")
        return preview, metadata, root


def decode_secret(root: Decimal, metadata: Decimal) -> str:
    """Reconstruct a message and validate the embedded marker and character codes."""
    if not metadata.is_finite() or metadata != metadata.to_integral_value():
        raise ValueError("Metadata must be a finite integer.")
    if metadata < 102 or metadata > MAX_DEGREE * 100 + 98:
        raise ValueError("Metadata is outside the supported range.")
    degree, digits = divmod(int(metadata), 100)
    if not 1 <= degree <= MAX_DEGREE or not 2 <= digits <= 98 or digits % 2:
        raise ValueError("Invalid root degree or character-code length.")
    if not root.is_finite() or root < 1 or len(root.as_tuple().digits) > 2048:
        raise ValueError("Root must be finite, at least one, and at most 2048 significant digits.")
    if root.adjusted() > 2 * digits:
        raise ValueError("Root is too large for the encoded length.")

    with localcontext() as context:
        context.prec = max(2 * digits + 40, len(root.as_tuple().digits) + 20)
        embedded = (root ** degree).to_integral_value(rounding=ROUND_HALF_EVEN)
        if embedded.adjusted() > 2 * digits:
            raise ValueError("Decoded value is too large for the encoded length.")
        number, marker = divmod(int(embedded), 10**digits)
    if marker != digits or number >= 10**digits:
        raise ValueError("Invalid representation: the root may have been rounded or truncated.")

    codes = str(number).zfill(digits)
    try:
        return "".join(CODE_CHARACTERS[int(codes[index:index + 2])] for index in range(0, digits, 2))
    except KeyError as error:
        raise ValueError("Decoded data contains an unsupported character code.") from error


def demo() -> None:
    message = "Hello how are you I am fine?"
    preview, metadata, root = encode_secret(message)
    print(f"Original: {message}")
    print(f"Preview (lossy): {preview}")
    print(f"Root: {root}")
    print(f"Metadata: {metadata}")
    print(f"Decoded: {decode_secret(root, metadata)}")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command")
    encode = commands.add_parser("encode", help="Print the full decimal root and metadata")
    encode.add_argument("message", help="1..49 characters: a-z, A-Z, space and ?")
    decode = commands.add_parser("decode", help="Decode an unrounded root and metadata")
    decode.add_argument("root")
    decode.add_argument("metadata")
    args = parser.parse_args(argv)

    try:
        if args.command == "encode":
            _, metadata, root = encode_secret(args.message)
            print(f"Root: {root}")
            print(f"Metadata: {metadata}")
        elif args.command == "decode":
            print(decode_secret(Decimal(args.root), Decimal(args.metadata)))
        else:
            demo()
    except (ValueError, DecimalException, ArithmeticError) as error:
        parser.exit(1, f"Error: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

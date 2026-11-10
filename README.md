# MathEncode

An experimental Python codec that embeds a short message in an integer and represents that integer through a **high-precision decimal root plus metadata**.

The interesting part is the representation. A small numerical value does not mean a small storage footprint: the root needs many decimal digits to preserve the message. This project provides **neither compression guarantees nor encryption**.

## Quick start

Python 3.10+; standard library only.

```sh
python MathEncode.py
python MathEncode.py encode "Hello how are you I am fine?"
python MathEncode.py decode "<full Root value>" "<Metadata value>"
python -m unittest discover -s tests -v
```

Copy the complete root printed by `encode`. Do not round it or convert it through a binary `float`.

For programmatic use:

```python
from MathEncode import encode_secret, decode_secret

preview, metadata, root = encode_secret("abc")
assert decode_secret(root, metadata) == "abc"
print(preview)  # Four decimal places: display only, usually not decodable.
```

## Representation

1. Map `a-z`, `A-Z`, `?` and space to two-digit codes `01..54`.
2. Keep the full code length `L = 2 * len(message)`, including leading zeroes.
3. Form `M = N * 10**L + L`.
4. Select a root degree `r` so that `M**(1/r)` is below the threshold (10 by default).
5. Store the decimal root and metadata `r * 100 + L`.

Decoding raises the root to `r`, rounds to the nearest integer, checks the length marker, and reconstructs the two-digit character codes. Local Decimal contexts supply guard digits without changing the importing application's global precision.

## Supported inputs and limits

- **1–49 characters**, because the historical metadata format reserves two digits for `L`.
- Only the 54 characters listed above. Unsupported characters produce an error rather than silently becoming `00`.
- A finite threshold greater than one, with a bounded root degree.
- The stored root is a finite approximation whose roundtrip is checked by the encoder.

There is no secret key. Anyone with the numbers and algorithm can decode the message. The length marker detects many malformed or truncated values, but it is not a checksum or authentication mechanism. The serialized representation may be considerably larger than the original text.

## What was corrected

The earlier command printed a four-place preview while the demo decoded a different, high-precision value. It also lost leading zeroes and used floor rounding during reconstruction. The CLI now emits the reconstructable value, and tests cover leading-zero codes, every supported character, maximum-length messages, custom thresholds and invalid data.

Previously generated values are not a versioned storage format and may already have lost information; compatibility with those broken encodings is not promised.

## Code guide

- [MathEncode.py](MathEncode.py) — mapping, root representation, validation and CLI.
- [tests/test_mathencode.py](tests/test_mathencode.py) — roundtrip and failure regressions.

## License

[MIT](LICENSE).

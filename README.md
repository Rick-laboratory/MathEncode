# MathEncode
"Encode natural language into two floating-point numbers using reversible root-based math. A new paradigm in information representation and density."

# 🧮 `secret_codec.py` – Lossless Message Encoding via Root Embedding

## 🔍 Summary
This project presents a novel, compact method for **losslessly encoding short messages** into just **two decimal numbers**: a fractional root approximation and a metadata tag. The approach uses **successive root operations** and precise numerical embedding to represent full ASCII messages in what appears to be **innocuous floating point values**.

Unlike traditional compression or encryption algorithms, this method is:
- **Lossless** and fully reversible  
- **Highly compressed** for structured or repetitive text  
- **Structurally minimal** (two numbers only)  
- **Mathematically obfuscated** (no apparent message format)  
- **Human-readable** (can be passed off as a floating point constant)

## 🚀 Key Features
- **Encode any text** (case-sensitive, A–Z, a–z, space, `?`) into:
  - `f1`: fractional root approximation (e.g., `9.9451`)
  - `f2`: a metadata code containing root depth and message length
- **Decode** the original message with full precision
- Supports Python CLI mode (`encode`, `decode`, or demo)
- Uses Python’s `decimal` module for high-precision computation

## 🧪 How It Works
1. The message is converted to a numeric code using a fixed 2-digit-per-character scheme.
2. This code is multiplied by a power of 10 and length-encoded into a number `M`.
3. A root `r` is chosen such that `M ** (1/r)` falls below a chosen threshold.
4. This root (`f1`) and a compact metadata tag (`f2`) are stored/transmitted.
5. Decoding involves reversing the root and reconstructing the message length from `f2`.

## 📦 Example
```bash
$ python secret_codec.py encode "Hello how are you I am fine?"
Encoded: f1=9.8917, f2=17692

$ python secret_codec.py decode 9.8917 17692
Decoded: Hello how are you I am fine?

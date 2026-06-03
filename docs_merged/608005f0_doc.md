<!--
VIGIA Academic Documentation
Module: 608005f0
Batch ID: vigia-doc-0068-608005f0
Generated: 2026-05-20T14:56:47.859121+00:00
-->

---

## ENGLISH

### What Is This Module?
`vigia/core/path_guard.py` is a deterministic access-control engine for digital forensics. It functions as a security checkpoint for files before they are opened or read. Rather than trusting a file path at face value, the module verifies that the filesystem object has not been substituted or altered between the moment it is inspected and the moment it is used. All verification relies on exact integer comparisons of kernel-reported metadata—inode numbers, byte sizes, and modification timestamps. Because filesystem states are discrete and countable, the module uses deterministic integer arithmetic exclusively; floating-point representations are neither necessary nor appropriate.

### Key Concepts

| Concept | Plain-Language Explanation | Scientific Relevance |
|---|---|---|
| **TOCTOU Hardening** | Closing the time window between "checking" a file and "using" it so an attacker cannot swap the file in between. | Prevents evidence tampering during acquisition. |
| **Symlink Detection (`lstat`)** | Inspecting a path’s own metadata without following shortcuts (symbolic links). | Ensures the examiner analyzes the true target, not a redirected decoy. |
| **Descriptor-Based Verification (`fstat`)** | Querying an already-open file handle for metadata, independent of the path string. | Eliminates race conditions because the handle points to a specific, immutable inode. |
| **Regular-File Check (`S_ISREG`)** | Confirming the object is a plain file—not a device, pipe, or socket—before reading. | Protects forensic workstations from unexpected system streams. |
| **Shared Lock (`flock`)** | Placing a non-exclusive lock on the file while reading so concurrent writers must wait. | Guarantees atomic integrity of integer metadata snapshots during acquisition. |
| **Deterministic Integer Metadata** | `inode`, `size`, and `mtime` are whole numbers reported by the kernel; equality is exact. | Floating-point math is excluded because filesystem identity is a countable, discrete state. |

### Glossary

- **PathValidationResult** — A structured record indicating whether a path passed all security checks.
- **PathGuard** — The primary controller class that orchestrates validation, opening, and reading.
- **SecurityException** — An alarm raised when a security rule is violated (e.g., symlink detected or TOCTOU mismatch).
- **validate()** — The initial checkpoint. Returns a result after checking for symlinks and regular-file status using integer metadata obtained via `lstat()`.
- **verify_no_toctou()** — The second checkpoint. Re-compares the `inode`, `size`, and `mtime` integers obtained *after* opening against those recorded *before* opening. Any mismatch signals an attack.
- **safe_open()** — A guarded open operation that chains validation, descriptor acquisition, and post-open TOCTOU verification using deterministic integer arithmetic.
- **safe_read()** — A guarded read operation that performs `safe_open()`, applies a shared `flock`, reads content, and confirms metadata integrity remained intact throughout.
- **lstat()** — A system call that inspects a path directly without traversing symbolic links.
- **fstat()** — A system call that inspects an already-open file descriptor, bypassing the path layer entirely.
- **inode** — An integer index that uniquely identifies a file object inside a filesystem.
- **mtime** — Modification time, recorded as an integer timestamp.
- **flock** — A kernel-managed advisory lock placed on a file descriptor.

### 【Scientific Note】
The terminology of Charles Sanders Peirce (semiotic signs), Umberto Eco (code and interpretation), and H. P. Grice (cooperative principles) appears in forensic literature as an analytical vocabulary, not as mysticism. Consider a digital sensor: a device transforms a physical state into an integer reading. In this module, the filesystem state is transformed into a triplet of exact integers—`inode`, `size`, and `mtime`. Peirce’s *indexical sign* is simply the kernel metadata that points directly to a file object. Eco’s *code* is the deterministic protocol that maps those integers to a
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

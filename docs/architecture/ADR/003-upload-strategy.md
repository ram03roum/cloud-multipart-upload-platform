# ADR-003: Multipart Upload Strategy

## Context
Files must be uploaded in chunks to support large file sizes, allow parallelization,
and enable resumability in case of network failure.

## Decision
We will implement a **client-driven chunked upload** using Azure Block Blob's native
two-phase commit pattern:
1. **Stage phase**: each chunk is uploaded independently via `Put Block`, identified
   by a unique Block ID
2. **Commit phase**: once all chunks are uploaded, `Put Block List` is called to
   assemble the blob in the correct order

## Justification
- Leverages Azure's native capability instead of building a custom assembly mechanism
- Each chunk upload is independent → supports parallel uploads and partial retries
- The commit phase guarantees atomicity: the blob only exists once all blocks are
  validated and ordered correctly
- Chunk size of **4-8 MiB** chosen as a balance between:
  - Network retry cost (smaller chunks = cheaper retries on failure)
  - HTTP overhead (larger chunks = fewer requests, less overhead)

## Alternatives Considered
- **Single full-file upload**: rejected — not viable for large files, no resumability, high risk of failure on unstable connections
- **Custom chunk reassembly (manual byte concatenation)**: rejected — reinvents what Azure already provides natively, adds unnecessary complexity and risk of corruption
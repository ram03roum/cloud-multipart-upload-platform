# ADR-002: Azure Storage Service Selection

## Context
The platform must store large files uploaded in chunks, support resumable uploads,
and scale to handle files up to several gigabytes in size.

## Decision
We will use **Azure Blob Storage** with **Block Blobs**.

## Justification
- Block Blobs are explicitly designed for this use case: large files uploaded as
  independent blocks (`Put Block`) and finalized as a single blob (`Put Block List`)
- Supports up to 50,000 blocks per blob, with each block up to 4000 MiB (practical
  recommendation: 4-8 MiB per block for optimal throughput/retry balance)
- Maximum blob size up to ~190.7 TiB — far beyond our functional needs
- Native integration with Azure SDK for Python, simplifying implementation
- Cost-effective compared to Azure Data Lake Gen2 or Premium tiers for this use case
- Built-in retry and resumability: failed blocks can be re-uploaded without
  restarting the entire file transfer

## Alternatives Considered
- **Azure Data Lake Storage Gen2**: rejected — designed for big data analytics workloads, unnecessary overhead for our use case
- **Azure Files**: rejected — optimized for SMB/file-share access patterns, not for chunked HTTP uploads
- **Append Blobs**: rejected — designed for append-only logging scenarios, not suited for parallel chunk uploads
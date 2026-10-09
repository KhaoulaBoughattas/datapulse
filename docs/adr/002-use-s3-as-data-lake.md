# ADR 002: Use S3 (via MinIO locally) as the Data Lake

## Context
Need object storage for bronze/silver/gold, runnable locally without a cloud account.

## Decision
S3-compatible storage: MinIO locally, real S3 in production, identical
application code against both.

## Alternatives Considered
- HDFS: genuine distributed storage, but too much local operational
  complexity for this data volume.
- Local filesystem: simplest, but teaches nothing transferable to production.

## Consequences
Zero code changes moving from MinIO to real S3 — only endpoint/credential
configuration differs.

# Synthetic A2.2 fixture

`artifact/` contains the checked-in bytes for a synthetic `andes@0.0.0` resolution. The repository URL and commit in the fixture are examples. The separate [manifest.sha256](manifest.sha256) file records the caller-trusted SHA-256 for these exact bytes. Tests use that value for the positive and tampering cases. Tests that exercise semantic rejection use disposable copies with a new synthetic pin. See the [contract and reproduction commands](../../../docs/release-contract.md).

# Third Party Notices

This repository is licensed under GPL-3.0-only. See `LICENSE`.

agent-remote is designed to manage or bundle selected external programs in release artifacts. The exact binary artifact, version, source URL, checksum, and license text must be recorded by the release process whenever a binary is shipped.

## Managed External Programs

| Component | Use in agent-remote | Upstream license notice |
| --- | --- | --- |
| WireGuard tools/helpers | Local-to-node tunnel setup and checks | `wireguard-tools` is distributed under GPL-2.0-only. Platform-specific WireGuard implementations can have different licenses; packaged artifacts must carry their exact upstream notice. Source: https://git.zx2c4.com/wireguard-tools/tree/COPYING |
| Mutagen | Workspace file synchronization | The Mutagen repository states that code is MIT unless otherwise specified, and also notes that official release builds from v0.17 onward include SSPL-licensed code by default. Packaged artifacts must identify whether they are official builds or custom MIT-only builds and include the matching upstream notices. Source: https://github.com/mutagen-io/mutagen/blob/master/LICENSE |

## Packaging Rule

Do not publish an agent-remote release artifact with embedded WireGuard or Mutagen binaries unless the artifact includes:

- the exact upstream component name and version;
- the source URL used to obtain or build it;
- the checksum of the packaged binary;
- the applicable upstream license text;
- any required source offer or source distribution instructions.

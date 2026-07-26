# Third-Party Notices

This repository is licensed under GPL-3.0-only. See `LICENSE`.

This deployment repository does not embed third-party executables. It references
container images and release artifacts maintained by their respective projects.

## Referenced Container Images

| Component | Use | License or notice |
| --- | --- | --- |
| PostgreSQL 17 Alpine image | Control-plane database | PostgreSQL License. Source: https://www.postgresql.org/about/licence/ |
| Redis 7 Alpine image | Cache, locks, and short-lived state | Redis licensing depends on the selected 7.x release. Pin an exact version and digest, then retain the notices shipped in that image. Source: https://github.com/redis/redis |
| Caddy 2 Alpine image | HTTPS reverse proxy | Apache-2.0. Source: https://github.com/caddyserver/caddy/blob/master/LICENSE |
| agent-remote server and admin images | Application services | GPL-3.0-only; see the corresponding repository notices. |

The optional browser runtime references `kasmweb/chrome:1.18.0`. It is pulled
as an external, configurable image and is not included in the deployment bundle.
Deployments that mirror or redistribute it must retain the notices from the
exact image digest. Source: https://hub.docker.com/r/kasmweb/chrome

## Distribution Requirements

When a release artifact redistributes third-party software, it must include:

- the exact component name and version;
- the source URL and checksum;
- the applicable license and notice text;
- any required source code, source offer, or relinking instructions.

Merely referencing an external image or download does not make it part of this
repository's release artifact. Mirrors and derived images are redistributions
and must satisfy the upstream terms.

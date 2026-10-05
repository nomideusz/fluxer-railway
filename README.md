# Deploy and Host Fluxer on Railway

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/new/template/fluxer-chat?utm_medium=integration&utm_source=button&utm_campaign=fluxer-chat)

[Fluxer](https://fluxer.app/) is an open-source alternative to Discord. It has communities (servers), text channels, replies, DMs and group DMs, roles and permissions, invites, emoji, file uploads with previews, link embeds and full-text message search, all in a fast web client. This template runs the official Fluxer images in **text-chat mode**, with every database and secret generated for you. Voice and video are switched off because Railway has no UDP.

## About Hosting Fluxer

Upstream's self-hosting setup is about 25 containers. This template collapses it into 13 Railway services while keeping each upstream image unchanged:

- **One public edge.** The `Fluxer` service is a Caddy server built on upstream's `fluxer-static` image. It serves the web client's assets itself and path-routes `/api`, `/gateway` (WebSocket), `/media` and `/admin` to the other services over Railway's private network. Only this service has a public domain.
- **Core services.** These run from the official `ghcr.io/fluxerapp/*` images:
  - `api` for REST
  - `worker` for background jobs and cron
  - `gateway`, the Erlang realtime WebSocket server
  - `media-proxy` for uploads, thumbnails and the presigned upload relay
  - `app-proxy`, which serves the web app
  - `admin`, the instance admin panel at `/admin`
- **Internal services in one container.** The snowflake, users, messages, GIF and link-unfurl services each run as a router plus a shard. The `svc` service bundles all ten processes from their official binaries and restarts the container if any of them exits.
- **Infrastructure.** Each of these has its own volume:
  - Postgres 16
  - Valkey 9
  - NATS 2.14 with JetStream
  - Meilisearch 1.53 for message search
  - SeaweedFS 4.47, the S3 store for attachments and avatars. Its first boot creates Fluxer's four buckets and an S3 identity with a generated key.
- **Pinned versions.** Every Fluxer image is pinned to the build that upstream's `v1` tag pointed to on 2026-10-05, so a redeploy never pulls an untested release.
- **Generated secrets.** Every signing key, RPC token, cookie and password is generated at deploy time, including:
  - the sudo, gateway, media-proxy, upload-relay and admin secrets
  - the Erlang cookie
  - the database, Valkey, Meilisearch and S3 passwords

  Web-push VAPID keys are derived at boot from a generated seed.

## Common Use Cases

- A private Discord-style community for a team, club, class or open-source project
- Chat you own: messages, files and search index stay in your own Railway project
- A self-hosted space for a community that wants to leave a hosted platform
- Trying Fluxer before running it on your own servers

## Dependencies for Fluxer Hosting

- Postgres 16 (included, private network only)
- Valkey 9 (included, private network only)
- NATS 2.14 with JetStream (included, private network only)
- Meilisearch 1.53 (included, private network only)
- SeaweedFS 4.47, S3-compatible (included, private network only)

### Deployment Dependencies

- [Fluxer self-hosting docs](https://docs.fluxer.app/)
- [Fluxer on GitHub](https://github.com/fluxerapp/fluxer)
- [Template source on GitHub](https://github.com/nomideusz/fluxer-railway)

### Implementation Details

**Register your account straight away.** Open the `Fluxer` service's domain and click Register. Registration is open on a new instance, and the first account becomes the instance admin. To stop anyone else signing up, change the registration mode in the instance settings of the admin panel at `/admin`.

**Text chat only.** Railway services can't receive UDP, so voice and video (LiveKit) are disabled with `FLUXER_LIVEKIT_ENABLED=false`. Push notifications are off too. Everything else works through the web client: communities, channels, DMs, uploads and search.

**No email by default.** Email verification and password reset need SMTP, so store your password safely. Railway only allows outbound SMTP on the Pro plan.

**Custom domain.** Add the domain to the `Fluxer` service, then set `FLUXER_BASE_DOMAIN` on that service to the bare hostname (for example `chat.example.com`). Every other service reads it, so redeploy them afterwards.

**Back up the secrets.** The root secrets live on the `Fluxer` service's Variables tab. Changing them later logs everyone out or breaks existing upload links, so copy them into your password manager and leave them unchanged.

**Resources.** In testing the whole stack used about 1.3 GB of RAM at idle and peaked at about 1.5 GB. The largest services were `api` (about 320 MB), Meilisearch (300 MB), `worker` (200 MB) and `gateway` (130 MB). Use the Hobby plan or above; the stack doesn't fit the Trial plan.

## Why Deploy Fluxer on Railway?

Railway is a singular platform to deploy your infrastructure stack. Railway will host your infrastructure so you don't have to deal with configuration, while allowing you to vertically and horizontally scale it.

By deploying Fluxer on Railway, you are one step closer to supporting a complete full-stack application with minimal burden. Host your servers, databases, AI agents, and more on Railway.

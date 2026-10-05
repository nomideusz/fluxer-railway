#!/usr/bin/env python3
"""Generate template-config.json (Railway serializedConfig) for the Fluxer template.

Upstream compose shares one env block across every Fluxer container; Railway has no
anchors, so it's built here once and stamped onto each service. `api` holds the root
values (domain, secrets) live on the edge service "Fluxer", and everything else references
`${{Fluxer.X}}`. Railway orders deploys by user-variable references (refs to RAILWAY_*_DOMAIN
don't count), so roots must sit on a service with no app deps, or deploys deadlock.
"""
import json, uuid

REPO = "https://github.com/nomideusz/fluxer-railway"
GH = "ghcr.io/fluxerapp"
TAG = {  # = what the floating `v1` tag pointed at on 2026-10-05
    "api": "2026.1004.160619", "gateway": "2026.1004.10845", "media-proxy": "2026.1003.110721",
    "app-proxy-self-hosted": "2026.1004.174950", "admin": "2026.1003.122521",
}
ALNUM = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
HEX = "0123456789abcdef"
ICON = "https://raw.githubusercontent.com/nomideusz/fluxer-railway/main/icon.svg"

def sid(name): return str(uuid.uuid5(uuid.NAMESPACE_URL, f"fluxer-railway/{name}"))
def secret(n, cs=ALNUM): return f'${{{{secret({n}, "{cs}")}}}}'
def priv(svc): return f"${{{{{svc}.RAILWAY_PRIVATE_DOMAIN}}}}"

DOMAIN = "${{Fluxer.FLUXER_BASE_DOMAIN}}"
ORIGIN = f"https://{DOMAIN}"

def v(value, desc, optional=False):
    return {"defaultValue": value, "description": desc, "isOptional": optional}

# Shared Fluxer env (x-fluxer-env in upstream docker-compose.yml).
COMMON = {
    "FLUXER_ENV": v("production", "Runtime environment"),
    "FLUXER_SELF_HOSTED": v("true", "Self-hosted mode"),
    "FLUXER_BASE_DOMAIN": v(DOMAIN, "Public hostname (set on the api service)"),
    "FLUXER_PUBLIC_SCHEME": v("https", "Public scheme"),
    "FLUXER_PUBLIC_PORT": v("443", "Public port"),
    "FLUXER_TRUST_CLIENT_IP_HEADER": v("true", "Trust X-Forwarded-For set by the edge"),
    "FLUXER_APP_ENDPOINT": v(ORIGIN, "Web app URL"),
    "FLUXER_MEDIA_ENDPOINT": v(f"{ORIGIN}/media", "Public media URL"),
    "FLUXER_MEDIA_PROXY_PUBLIC_ENDPOINT": v(f"{ORIGIN}/media", "Public media URL"),
    "FLUXER_ADMIN_ENDPOINT": v(f"{ORIGIN}/admin", "Admin dashboard URL"),
    "FLUXER_MARKETING_ENDPOINT": v(ORIGIN, "Marketing URL"),
    "FLUXER_DATABASE_BACKEND": v("postgres", "Database backend"),
    "FLUXER_POSTGRES_HOST": v(priv("Postgres"), "Postgres host"),
    "FLUXER_POSTGRES_PORT": v("5432", "Postgres port"),
    "FLUXER_POSTGRES_DATABASE": v("${{Postgres.POSTGRES_DB}}", "Postgres database"),
    "FLUXER_POSTGRES_USERNAME": v("${{Postgres.POSTGRES_USER}}", "Postgres user"),
    "FLUXER_POSTGRES_PASSWORD": v("${{Postgres.POSTGRES_PASSWORD}}", "Postgres password"),
    "FLUXER_KV_URL": v(f"redis://:${{{{Valkey.VALKEY_PASSWORD}}}}@{priv('Valkey')}:6379/0", "Valkey URL"),
    "FLUXER_NATS_URL": v(f"nats://{priv('NATS')}:4222", "NATS URL"),
    "FLUXER_NATS_JETSTREAM_URL": v(f"nats://{priv('NATS')}:4222", "NATS JetStream URL"),
    "FLUXER_SVC_NATS_URL": v(f"nats://{priv('NATS')}:4222", "NATS URL for internal services"),
    "FLUXER_SVC_SHARD_COUNT": v("1", "Internal service shard count"),
    "FLUXER_SEARCH_ENGINE": v("meilisearch", "Search engine"),
    "FLUXER_SEARCH_URL": v(f"http://{priv('Meilisearch')}:7700", "Meilisearch URL"),
    "FLUXER_SEARCH_API_KEY": v("${{Meilisearch.MEILI_MASTER_KEY}}", "Meilisearch master key"),
    "FLUXER_S3_ENDPOINT": v(f"http://{priv('SeaweedFS')}:8333", "S3 endpoint (SeaweedFS)"),
    "FLUXER_S3_PUBLIC_ENDPOINT": v(f"http://{priv('SeaweedFS')}:8333", "S3 endpoint used in presigned URLs (relayed via /media)"),
    "FLUXER_S3_REGION": v("us-east-1", "S3 region"),
    "FLUXER_S3_ACCESS_KEY_ID": v("${{SeaweedFS.S3_ACCESS_KEY}}", "S3 access key"),
    "FLUXER_S3_SECRET_ACCESS_KEY": v("${{SeaweedFS.S3_SECRET_KEY}}", "S3 secret key"),
    "FLUXER_S3_FORCE_PATH_STYLE": v("true", "Path-style S3 addressing"),
    "FLUXER_S3_BUCKET_CDN": v("fluxer", "Processed assets bucket"),
    "FLUXER_S3_BUCKET_UPLOADS": v("fluxer-uploads", "Raw uploads bucket"),
    "FLUXER_S3_BUCKET_REPORTS": v("fluxer-reports", "Abuse reports bucket"),
    "FLUXER_S3_BUCKET_HARVESTS": v("fluxer-harvests", "Data export bucket"),
    "FLUXER_API_PRESIGNED_HARVEST_DOWNLOADS_ENABLED": v("false", "Presigned data-export downloads"),
    "FLUXER_LIVEKIT_ENABLED": v("false", "Voice/video. Off: LiveKit needs UDP, which Railway does not offer"),
    "FLUXER_GATEWAY_PUSH_ENABLED": v("false", "Browser push notifications (push service not deployed)"),
    "FLUXER_EMAIL_ENABLED": v("false", "Email. Off = addresses auto-verified, no password reset mail"),
    "FLUXER_EMAIL_FROM_EMAIL": v(f"noreply@{DOMAIN}", "From address once SMTP is configured"),
    "FLUXER_SUDO_MODE_SECRET": v("${{Fluxer.FLUXER_SUDO_MODE_SECRET}}", "Sudo-mode JWT key"),
    "FLUXER_CONNECTION_INITIATION_SECRET": v("${{Fluxer.FLUXER_CONNECTION_INITIATION_SECRET}}", "Connection initiation token key"),
    "FLUXER_GATEWAY_RPC_AUTH_TOKEN": v("${{Fluxer.FLUXER_GATEWAY_RPC_AUTH_TOKEN}}", "API<->Gateway RPC token"),
    "FLUXER_MEDIA_PROXY_SECRET_KEY": v("${{Fluxer.FLUXER_MEDIA_PROXY_SECRET_KEY}}", "Media proxy URL signing key"),
    "FLUXER_MEDIA_PROXY_UPLOAD_RELAY_SECRET_BASE64": v("${{Fluxer.FLUXER_MEDIA_PROXY_UPLOAD_RELAY_SECRET_BASE64}}", "Upload relay token key"),
    "FLUXER_ADMIN_SECRET_KEY_BASE": v("${{Fluxer.FLUXER_ADMIN_SECRET_KEY_BASE}}", "Admin session key"),
    "FLUXER_ADMIN_OAUTH_CLIENT_SECRET": v("${{Fluxer.FLUXER_ADMIN_OAUTH_CLIENT_SECRET}}", "Admin OAuth client secret"),
    "FLUXER_VAPID_EMAIL": v(f"admin@{DOMAIN}", "Web push contact"),
    "FLUXER_PASSKEY_RP_ID": v(DOMAIN, "Passkey relying party"),
    "FLUXER_PASSKEY_ADDITIONAL_ALLOWED_ORIGINS": v(ORIGIN, "Passkey origins"),
    "FLUXER_INTERNAL_API_ENDPOINT": v(f"http://{priv('api')}:8080", "Internal API URL"),
    "FLUXER_INTERNAL_MEDIA_PROXY_ENDPOINT": v(f"http://{priv('media-proxy')}:8080", "Internal media proxy URL"),
    "FLUXER_MEDIA_PROXY_UPLOAD_RELAY_ENDPOINT": v(f"{ORIGIN}/media", "Upload relay URL"),
}

# Railway can't generate an EC keypair, so api/worker derive the VAPID pair from a
# random seed at boot (deterministic → both get the same pair). Explicit keys win.
BOOT_JS = ("const c=process.getBuiltinModule('crypto'),u=process.getBuiltinModule('url'),e=process.env;"
           "if(!e.FLUXER_VAPID_PRIVATE_KEY){const k=c.createHash('sha256').update('fluxer-vapid:'+e.FLUXER_VAPID_SEED).digest(),"
           "d=c.createECDH('prime256v1');d.setPrivateKey(k);e.FLUXER_VAPID_PRIVATE_KEY=k.toString('base64url');"
           "e.FLUXER_VAPID_PUBLIC_KEY=d.getPublicKey().toString('base64url')}"
           "import(u.pathToFileURL(process.argv[1]).href)")
def node_start(entry): return f"/bin/sh -c 'exec node -e \"$FLUXER_BOOT_JS\" dist/{entry}'"

ROOT = {
    "FLUXER_BASE_DOMAIN": v("${{RAILWAY_PUBLIC_DOMAIN}}", "Public hostname every service reads. Change this when you add a custom domain"),
    "FLUXER_SUDO_MODE_SECRET": v(secret(64, HEX), "Sudo-mode JWT key"),
    "FLUXER_CONNECTION_INITIATION_SECRET": v(secret(64, HEX), "Connection initiation token key"),
    "FLUXER_GATEWAY_RPC_AUTH_TOKEN": v(secret(64, HEX), "API<->Gateway RPC token"),
    "FLUXER_MEDIA_PROXY_SECRET_KEY": v(secret(64, HEX), "Media proxy URL signing key"),
    "FLUXER_MEDIA_PROXY_UPLOAD_RELAY_SECRET_BASE64": v(secret(44), "Upload relay token key (base64, >=32 bytes)"),
    "FLUXER_ADMIN_SECRET_KEY_BASE": v(secret(64, HEX), "Admin session key"),
    "FLUXER_ADMIN_OAUTH_CLIENT_SECRET": v(secret(48), "Admin OAuth client secret"),
    "FLUXER_VAPID_SEED": v(secret(48), "Seed the web-push VAPID keypair is derived from at boot"),
    "FLUXER_BOOT_JS": v(BOOT_JS, "Boot shim: derives FLUXER_VAPID_* from FLUXER_VAPID_SEED, then starts Fluxer. Don't edit"),
}

# api/worker exit at boot when the internal services don't answer on NATS; referencing a svc
# variable makes Railway hold them until svc is deployed.
SVC_DEP = v("${{svc.PORT}}", "Orders this service after svc on deploy. Don't edit")

def svc(name, icon, source, variables, *, start=None, health=None, domain=False, volume=None):
    s = {"icon": icon, "name": name, "build": {},
         "deploy": {"startCommand": start, "healthcheckPath": health,
                    "restartPolicyType": "ON_FAILURE", "restartPolicyMaxRetries": 10},
         "source": source,
         "networking": {"serviceDomains": {"<hasDomain>": {}} if domain else {}},
         "variables": variables}
    if volume:
        s["volumeMounts"] = {sid(name + "-vol"): {"mountPath": volume}}
    return s

def img(name): return {"image": f"{GH}/fluxer-{name}:{TAG[name]}"}
def repo(d): return {"repo": REPO, "rootDirectory": f"/{d}"}

def common(**extra):
    return {**COMMON, **{k: (x if isinstance(x, dict) else v(x, k)) for k, x in extra.items()}}

services = [
    svc("Fluxer", ICON, repo("edge"), {
        "PORT": v("8080", "Edge listen port"),
        "API_UPSTREAM": v(f"{priv('api')}:8080", "api upstream"),
        "GATEWAY_UPSTREAM": v(f"{priv('gateway')}:8080", "gateway upstream"),
        "MEDIA_UPSTREAM": v(f"{priv('media-proxy')}:8080", "media-proxy upstream"),
        "ADMIN_UPSTREAM": v(f"{priv('admin')}:8080", "admin upstream"),
        "APP_UPSTREAM": v(f"{priv('app-proxy')}:8080", "app-proxy upstream"),
        **ROOT,
    }, health="/_health", domain=True),
    svc("api", ICON, img("api"), {k: {**x, "defaultValue": x["defaultValue"].replace("${{api.", "${{")}
        for k, x in common().items()} | {
        "FLUXER_VAPID_SEED": v("${{Fluxer.FLUXER_VAPID_SEED}}", "Seed for the derived VAPID keypair"),
        "FLUXER_BOOT_JS": v("${{Fluxer.FLUXER_BOOT_JS}}", "Boot shim"),
        "SVC_DEPENDENCY": SVC_DEP,
        "PORT": v("8080", "Listen port"), "FLUXER_API_PORT": v("8080", "Listen port"),
        "FLUXER_POSTGRES_MAX_CONNECTIONS": v("20", "Postgres pool size"),
        "FLUXER_API_PRESIGNED_ATTACHMENT_UPLOADS_ENABLED": v("true", "Presigned attachment uploads")},
        start=node_start("AppEntrypoint.js"), health="/_health"),
    svc("worker", ICON, img("api"), common(
        FLUXER_VAPID_SEED=v("${{Fluxer.FLUXER_VAPID_SEED}}", "Seed for the derived VAPID keypair"),
        FLUXER_BOOT_JS=v("${{Fluxer.FLUXER_BOOT_JS}}", "Boot shim"),
        SVC_DEPENDENCY=SVC_DEP,
        FLUXER_API_WORKER_MODE=v("all_lanes", "Run every job lane"),
        FLUXER_API_WORKER_ENABLE_CRON_SCHEDULER=v("true", "Run cron jobs"),
        FLUXER_POSTGRES_MAX_CONNECTIONS=v("15", "Postgres pool size")),
        start=node_start("WorkerEntrypoint.js")),
    svc("gateway", ICON, img("gateway"), common(
        PORT=v("8080", "Listen port"), FLUXER_GATEWAY_PORT=v("8080", "Listen port"),
        FLUXER_ERLANG_COOKIE=v(secret(48), "BEAM distribution cookie"),
        FLUXER_GATEWAY_MEDIA_PROXY_ENDPOINT=v(f"{ORIGIN}/media", "Public media URL"),
        FLUXER_GATEWAY_STATIC_CDN_ENDPOINT=v(ORIGIN, "Static CDN URL")),
        health="/_health"),
    svc("media-proxy", ICON, img("media-proxy"), common(
        PORT=v("8080", "Listen port"), FLUXER_MEDIA_PROXY_PORT=v("8080", "Listen port"),
        FLUXER_MEDIA_PROXY_MODE=v("upload", "Serve media + upload relay"),
        FLUXER_MEDIA_PROXY_STORAGE_BACKEND=v("s3", "Storage backend"),
        FLUXER_MEDIA_PROXY_CORS_ALLOWED_ORIGINS=v(ORIGIN, "CORS origins"),
        FLUXER_S3_READ_SIGNED=v("true", "Sign S3 reads")),
        health="/_health"),
    svc("app-proxy", ICON, img("app-proxy-self-hosted"), {
        "PORT": v("8080", "Listen port"), "FLUXER_APP_PROXY_PORT": v("8080", "Listen port"),
        "FLUXER_BASE_DOMAIN": v(DOMAIN, "Public hostname"),
        "FLUXER_PUBLIC_SCHEME": v("https", "Public scheme"), "FLUXER_PUBLIC_PORT": v("443", "Public port"),
        "FLUXER_TRUST_CLIENT_IP_HEADER": v("true", "Trust X-Forwarded-For set by the edge"),
        "FLUXER_S3_ENDPOINT": COMMON["FLUXER_S3_ENDPOINT"], "FLUXER_S3_REGION": COMMON["FLUXER_S3_REGION"],
        "FLUXER_S3_ACCESS_KEY_ID": COMMON["FLUXER_S3_ACCESS_KEY_ID"],
        "FLUXER_S3_SECRET_ACCESS_KEY": COMMON["FLUXER_S3_SECRET_ACCESS_KEY"],
        "FLUXER_S3_BUCKET_UPLOADS": COMMON["FLUXER_S3_BUCKET_UPLOADS"],
        "DISCOVERY_UPSTREAM_URL": v(f"http://{priv('Fluxer')}:8088/.well-known/fluxer", "Discovery via the edge's internal listener"),
        "PUBLIC_BOOTSTRAP_API_ENDPOINT": v("/api", "API path in the page bootstrap"),
        "PUBLIC_BOOTSTRAP_API_PUBLIC_ENDPOINT": v(f"{ORIGIN}/api", "Absolute API URL in the page bootstrap"),
    }, health="/_health"),
    svc("svc", ICON, repo("svc"), common(
        PORT=v("8090", "Health port of the first internal service (healthcheck)")), health="/_health"),
    svc("admin", ICON, img("admin"), common(
        PORT=v("8080", "Listen port"), FLUXER_ADMIN_PORT=v("8080", "Listen port"),
        FLUXER_ADMIN_BASE_PATH=v("/admin", "Admin path"),
        FLUXER_API_ENDPOINT=v(f"http://{priv('api')}:8080", "Internal API URL"),
        FLUXER_STATIC_CDN_ENDPOINT=v(ORIGIN, "Static CDN URL")),
        health="/_health"),
    svc("Postgres", "https://devicons.railway.app/i/postgresql.svg",
        {"image": "ghcr.io/railwayapp-templates/postgres-ssl:16"}, {
        "POSTGRES_DB": v("fluxer", "Database name"),
        "POSTGRES_USER": v("fluxer", "Database user"),
        "POSTGRES_PASSWORD": v(secret(32), "Auto-generated database password"),
        "PGDATA": v("/var/lib/postgresql/data/pgdata", "Data subdirectory - keeps Postgres happy on Railway volumes"),
        "RAILWAY_DEPLOYMENT_DRAINING_SECONDS": v("60", "Time for Postgres to shut down cleanly on redeploy"),
    }, volume="/var/lib/postgresql/data"),
    svc("Valkey", "https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/svg/valkey.svg", {"image": "valkey/valkey:9.1-alpine"}, {
        "VALKEY_PASSWORD": v(secret(32), "Auto-generated Valkey password"),
    }, start='/bin/sh -c "chown -R valkey:valkey /data && exec docker-entrypoint.sh valkey-server '
             '--requirepass $VALKEY_PASSWORD --appendonly yes --dir /data --maxmemory 192mb --maxmemory-policy noeviction"',
        volume="/data"),
    svc("NATS", "https://cdn.simpleicons.org/natsdotio", {"image": "nats:2.14-alpine"}, {},
        start="nats-server -js -sd /data -m 8222", volume="/data"),
    svc("Meilisearch", "https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/svg/meilisearch.svg", {"image": "getmeili/meilisearch:v1.53"}, {
        "MEILI_MASTER_KEY": v(secret(48), "Auto-generated Meilisearch master key"),
        "MEILI_ENV": v("production", "Meilisearch mode"),
        "MEILI_NO_ANALYTICS": v("true", "Disable telemetry"),
        "MEILI_HTTP_ADDR": v("[::]:7700", "Listen on IPv6 + IPv4 for private networking"),
        "MEILI_MAX_INDEXING_MEMORY": v("256mb", "Indexing memory cap"),
        "MEILI_MAX_INDEXING_THREADS": v("2", "Indexing threads"),
    }, volume="/meili_data"),
    svc("SeaweedFS", "https://raw.githubusercontent.com/seaweedfs/seaweedfs/master/note/seaweedfs.png", repo("seaweedfs"), {
        "S3_ACCESS_KEY": v("fluxer", "S3 access key"),
        "S3_SECRET_KEY": v(secret(48), "Auto-generated S3 secret key"),
        "GOMEMLIMIT": v("512MiB", "Go heap soft limit"),
        "WEED_MASTER_VOLUME_GROWTH_COPY_1": v("1", "Grow one volume at a time (upstream default)"),
    }, volume="/data"),
]

json.dump({"services": {sid(s["name"]): s for s in services}}, open("template-config.json", "w"), indent=1)
print(len(services), "services")

# All five Fluxer internal services (router + shard each) in one container.
# Upstream runs these as 10 separate containers; on Railway that's 10 services for ~100 MB of Rust.
FROM ghcr.io/fluxerapp/fluxer-snowflakes:2026.1001.150225 AS snowflakes
FROM ghcr.io/fluxerapp/fluxer-users:2026.1002.162104 AS users
FROM ghcr.io/fluxerapp/fluxer-gifs:2026.1002.153934 AS gifs
FROM ghcr.io/fluxerapp/fluxer-unfurl:2026.1003.155631 AS unfurl
FROM ghcr.io/fluxerapp/fluxer-messages:2026.1001.150214
COPY --from=snowflakes /usr/local/bin/fluxer-snowflakes /usr/local/bin/
COPY --from=users /usr/local/bin/fluxer-users /usr/local/bin/
COPY --from=gifs /usr/local/bin/fluxer-gifs /usr/local/bin/
COPY --from=unfurl /usr/local/bin/fluxer-unfurl /usr/local/bin/
COPY run.sh /usr/local/bin/run.sh
CMD ["/bin/bash", "/usr/local/bin/run.sh"]

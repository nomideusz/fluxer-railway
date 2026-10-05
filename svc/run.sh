#!/bin/bash
# Start router + shard for each internal service; if any process dies, exit so Railway restarts the lot.
port=8090
for svc in snowflakes users messages gifs unfurl; do
	for mode in router shard; do
		extra=()
		[[ $mode == shard && ($svc == users || $svc == messages) ]] && extra+=(FLUXER_POSTGRES_MAX_CONNECTIONS=20)
		[[ $mode == shard && $svc == unfurl ]] && extra+=(FLUXER_MEDIA_PROXY_ENDPOINT="$FLUXER_INTERNAL_MEDIA_PROXY_ENDPOINT")
		env FLUXER_SVC_NAME=$svc FLUXER_SVC_MODE=$mode FLUXER_SVC_SHARD_ID=0 FLUXER_SVC_PORT=$port "${extra[@]}" \
			/usr/local/bin/fluxer-$svc &
		port=$((port + 1))
	done
done
wait -n
echo "svc: a process exited, restarting container" >&2
exit 1

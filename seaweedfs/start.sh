#!/bin/sh
# weed server + the upstream seaweedfs-init logic (create the 4 buckets, install the S3 identity) in one service.
buckets="fluxer fluxer-uploads fluxer-reports fluxer-harvests"
(
	while :; do
		sleep 3
		listed=$(echo "s3.bucket.list" | timeout 10 weed shell -master=localhost:9333 2>&1)
		missing=""
		for b in $buckets; do
			echo "$listed" | grep -q "^[[:space:]]*$b[[:space:]]" || missing="$missing $b"
		done
		[ -z "$missing" ] && break
		for b in $missing; do
			echo "s3.bucket.create -name $b" | timeout 10 weed shell -master=localhost:9333 >/dev/null 2>&1
		done
	done
	echo "s3.configure -user=fluxer -access_key=$S3_ACCESS_KEY -secret_key=$S3_SECRET_KEY -actions=Admin,Read,Write,List,Tagging -apply" \
		| timeout 10 weed shell -master=localhost:9333 >/dev/null 2>&1 \
		&& echo "seaweedfs: buckets and S3 identity ready" || echo "seaweedfs: s3.configure FAILED" >&2
) &
exec weed server -s3 -dir=/data -master.telemetry=false

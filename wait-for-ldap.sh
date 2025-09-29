#!/bin/bash
# wait-for-ldap.sh - Script to wait for LDAP service to be ready

set -e

host="$1"
port="$2"
shift 2
cmd="$@"

until nc -z "$host" "$port"; do
  >&2 echo "LDAP is unavailable - sleeping"
  sleep 1
done

>&2 echo "LDAP is up - executing command"
exec $cmd
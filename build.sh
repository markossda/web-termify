#!/bin/sh
# Build script for Cloudflare Workers deployment
# Copies assets to public/ excluding .git and dev files
mkdir -p public
rsync -a --exclude='.git' --exclude='node_modules' --exclude='scripts' --exclude='.wrangler' --exclude='public' --exclude='build.sh' ./ public/

#!/bin/bash
set -e
npm install
npm --workspace lib/db run push

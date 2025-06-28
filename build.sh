#!/usr/bin/env bash

npx repomix -i 'dist,CLAUDE.md,AGENTS.md,issues,.specstory,work' -o ./llms.txt .
uvx hatch clean && uvx hatch build

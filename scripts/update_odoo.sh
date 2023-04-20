#!/bin/bash
docker-compose exec web odoo -u $1 --stop-after-init
docker restart $2_web_1

run:
	docker-compose -f docker_app/docker-compose.prod.yml down -v
	docker-compose -f docker_app/docker-compose.prod.yml up -d --build
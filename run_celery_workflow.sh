docker run -d -p 5672:5672 --name rabbitmq rabbitmq
docker run -d -p 6379:6379 --name redis redis
celery -A Quant.celery_interface worker -l INFO -D
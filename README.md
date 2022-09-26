# rdfind-web
A self-hosted web interface for rdfind for your home server

## Steps to run
- create a `docker-compose.yml`
    ```yml
    version: "3"

    services:
        web:
            image: zkhan93/rdfind-web:master
            ports:
            - 3000:80
            command:
            [
                "gunicorn",
                "wsgi:app",
                "--bind",
                "0.0.0.0:80",
                "--workers",
                "2",
                "--log-level=info",
                "--access-logfile",
                "-"
            ]
            - volumes:
                - /path/to/storage:/storage
                - report:/report
            environment:
            - CELERY_BROKER_URL=redis://redis:6379/0
            - CELERY_RESULT_BACKEND=redis://redis:6379/1
            restart: unless-stopped

        worker:
            image: zkhan93/rdfind-web:master
            command:
            [
                "celery",
                "--app",
                "app.celery",
                "worker",
                "--pool",
                "eventlet",
                "--autoscale",
                "10,2",
                "--loglevel=info",
                "--concurrency=10"
            ]
            environment:
            - CELERY_BROKER_URL=redis://redis:6379/0
            - CELERY_RESULT_BACKEND=redis://redis:6379/1
            - volumes:
                - /path/to/storage:/storage
                - report:/report
            depends_on:
            - redis

        redis:
            image: redis:7-alpine

    volumes:
        data:
  
    ```
- only /storage volume is allowed to be interacted with
- run `docker-compose up --build -d `
- access the web interface at http://\<server ip\>:3000

## TODOs
- optimized delete feature, store only index of rows
- add a hook to celery task to cleanup rdfind report files 
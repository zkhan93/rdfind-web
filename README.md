# rdfind-web
A self-hosted web interface for rdfind for your home server

- copy `docker-compose.yml`
- add a volume
    ```yml
    - volumes:
        /path/to/storage:/storage
    ```
- access the web interface at http://<server ip>:3000

## TODOs
- optimized delete feature, store only index of rows
- add a hook to celery task to cleanup rdfind report files 
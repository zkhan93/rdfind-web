# rdfind-web
A selfhosted web interface for rdfind for your home server

- copy `docker-compose.yml`
- add a volume
    ```yml
    - volumes:
        /path/to/storage:/storage
    ```
- access the web interface at http://<server ip>:3000

## TODOs
- optimized delete feature, store only index of rows
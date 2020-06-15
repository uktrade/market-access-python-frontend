### Quickstart
1. Add `healthcheck` to your `INSTALLED_APPS` settings:
    ```
    INSTALLED_APPS = (
        ...
        "healthcheck",
    ) 
    ```
2. Include the healthcheck URLconf in your project `urls.py`:
    ```
    path("", include("healthcheck.urls", namespace="healthcheck")),
    ```
3. Start the django dev server and visit http://localhost:8880/check/
    - Example response, connection to DB is healthy:
        ```
        OK 0.1822049617767334
        ```
    - Example response, connection to DB has timed out:
        ```
        FAIL 6.0770041942596436
        ```

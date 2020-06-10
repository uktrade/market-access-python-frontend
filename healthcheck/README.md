### Quickstart
1. Add `healtcheck` to your `INSTALLED_APPS` settings:
    ```
    INSTALLED_APPS = (
        ...
        "api.healthcheck",
    ) 
    ```
2. Include the healthcheck URLconf in your project `urls.py`:
    ```
    path("", include("api.healthcheck.urls", namespace="healthcheck")),
    ```
3. Start the dajngo dev server and visit http://localhost:8880/check/
    - Example response, connection to DB is healty:
        ```
        OK 0.1822049617767334
        ```
    - Example response, connection to DB has timed out:
        ```
        FAIL 6.0770041942596436
        ```

# LinkedOut

Start:

```sh
docker compose up --build
```

Entry point: http://localhost:8000

Players should register their own account.

LinkedOut recently launched post templates and Recruiter Labs for local employees. The media pipeline and renderer might reveal more than intended.

## Instancer

The instancer is a separate Flask service. Players only paste their own CTFd token; the service validates it with CTFd and starts one isolated `web + renderer` pair per account.

Build the challenge images and instancer:

```sh
docker compose -f docker-compose.instancer.yml build
```

Start the instancer on port `35000`:

```sh
LINKEDOUT_FLAG_PATH="$(pwd)/flag.txt" \
INSTANCER_SECRET_KEY="$(openssl rand -hex 32)" \
docker compose -f docker-compose.instancer.yml up -d instancer
```

Entry point: http://chals1.ais3.org:35000

Instance ports are allocated from `36000` to `37000`. The admin CTFd token is optional and should be kept out of the repository if used.

The instancer container runs Gunicorn with one worker and multiple threads. This keeps the in-process lifecycle lock and rate limiter consistent while allowing concurrent HTTP requests.

Default request limits are `12` login attempts and `20` instance actions per `60` seconds. Adjust `RATE_LIMIT_WINDOW_SECONDS`, `LOGIN_RATE_LIMIT`, and `INSTANCE_RATE_LIMIT` in the deployment environment if needed.

By default the instancer does not trust `X-Forwarded-*` headers, so direct access to port `35000` cannot spoof client IPs for rate limiting. If it is deployed behind a trusted reverse proxy that strips client-supplied forwarding headers, set `TRUST_PROXY=true`.

Player containers are started with memory, pids, CPU, read-only root filesystem, and bounded tmpfs limits. Their per-instance bridge network disables IP masquerading so the published web port still works while container egress is blocked.

The instancer verifies player tokens with:

```http
GET https://pre-exam.ais3.org/api/v1/users/me
Authorization: Token <player-token>
Accept: application/json
Content-Type: application/json
```

If direct verification fails and `CTFD_ADMIN_TOKEN` is configured, the instancer also tries an admin-token fallback through CTFd's token detail API. If verification redirects to `/login`, CTFd is not accepting API tokens on that route. Check that the token is a CTFd API token and that the CTFd reverse proxy forwards the `Authorization` header to the app.

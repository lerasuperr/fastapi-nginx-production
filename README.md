# FastAPI Nginx Production

## About

This project demonstrates how to build a production-oriented backend infrastructure using FastAPI, Docker and Nginx.

The goal is not only to create a working API, but also to demonstrate production practices such as reverse proxy configuration, request logging, security hardening, compression, rate limiting and deployment preparation.

## Features

- FastAPI application
- Dockerized environment
- Docker Compose orchestration
- Nginx reverse proxy
- Environment-based configuration
- Request logging middleware
- Nginx access and error logging
- Nginx rate limiting
- Custom Nginx log format
- Upstream response time tracking
- Proxy headers
- HTTP security headers
- Gzip response compression

## Technology Stack

- Python 3.13
- FastAPI
- Uvicorn
- Docker
- Docker Compose
- Nginx

## Nginx Configuration

Nginx acts as a reverse proxy in front of the FastAPI application.

The application is not exposed directly to the host. External HTTP traffic enters through Nginx, which forwards requests to the FastAPI service inside the Docker network.

### Request Flow

```text
Client
   |
   | HTTP :80
   v
Nginx
   |
   | proxy_pass
   v
FastAPI :8000
```

Nginx is responsible for infrastructure-level HTTP concerns, while FastAPI handles application logic.

### Reverse Proxy

Requests received by Nginx are forwarded to the FastAPI container:

```nginx
location / {
    proxy_pass http://api:8000;
}
```

Docker service discovery allows Nginx to resolve the `api` service by its Docker network name.

### Proxy Headers

Nginx forwards information about the original client request to FastAPI:

```nginx
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
```

These headers preserve information that would otherwise be lost when the request passes through the reverse proxy.

The forwarded values can be used by the application to determine:

- original host;
- client IP address;
- proxy chain;
- original request protocol.

### Logging

Nginx provides both access and error logging.

The custom access log format includes upstream timing information:

- `$request_time` — total time spent processing the request;
- `$upstream_response_time` — time spent waiting for the upstream FastAPI service;
- `$status` — HTTP response status;
- `$request` — HTTP method and path;
- `$http_user_agent` — client user agent.

This makes it possible to distinguish application latency from proxy-level request processing.

Example:

```text
request_time=0.003
upstream_response_time=0.002
```

This means that Nginx spent approximately 3 ms processing the entire request, while approximately 2 ms were spent waiting for FastAPI.

### HTTP Security Headers

Nginx adds several HTTP security headers independently of the application:

```http
X-Content-Type-Options: nosniff
X-Frame-Options: SAMEORIGIN
Referrer-Policy: strict-origin-when-cross-origin
Content-Security-Policy-Report-Only: default-src 'self';
```

#### X-Content-Type-Options

Prevents browsers from MIME-sniffing responses and interpreting content as a different media type than declared by the server.

The project uses:

```http
X-Content-Type-Options: nosniff
```

#### X-Frame-Options

Controls whether the application can be embedded inside a `<frame>` or `<iframe>`.

The current configuration uses:

```http
X-Frame-Options: SAMEORIGIN
```

This allows framing only by pages from the same origin.

#### Referrer-Policy

Controls how much referrer information is sent when navigating from the application to another origin.

The project uses:

```http
Referrer-Policy: strict-origin-when-cross-origin
```

This provides a balance between preserving useful referrer information and limiting the amount of URL information disclosed to other origins.

#### Content Security Policy

CSP is currently configured in Report-Only mode:

```http
Content-Security-Policy-Report-Only: default-src 'self';
```

Report-Only mode allows CSP violations to be observed without actively blocking resources.

This is useful when introducing CSP into an existing application because the policy can be tested before switching to enforcement mode.

### Gzip Compression

Nginx compresses sufficiently large JSON responses using Gzip:

```nginx
gzip on;
gzip_types application/json;
gzip_min_length 1000;
```

The client advertises compression support using:

```http
Accept-Encoding: gzip
```

If the response meets the configured conditions, Nginx compresses the response and returns:

```http
Content-Encoding: gzip
```

Compression is handled at the reverse proxy layer rather than inside the FastAPI application.

This allows the application to remain responsible only for generating the response, while Nginx handles transport-level optimization.

### Rate Limiting

Nginx limits the request rate before requests reach the FastAPI application.

The rate limiter is configured using `limit_req_zone`:

```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
```

The configuration uses the client's IP address as the rate-limiting key.

`api_limit` is the name of the shared memory zone used by Nginx to store the state required for rate limiting.

The zone has a size of 10 MB.

The configured rate is:

```text
10 requests per second per client IP
```

The limiter is applied to API requests using:

```nginx
limit_req zone=api_limit burst=20 nodelay;
```

`burst` allows a temporary spike of requests above the configured rate.

`nodelay` prevents requests within the allowed burst from being artificially delayed. Requests that exceed the available burst capacity are rejected immediately.

The project explicitly configures the HTTP status returned when the rate limit is exceeded:

```nginx
limit_req_status 429;
```

Therefore, clients exceeding the configured limit receive:

```http
HTTP/1.1 429 Too Many Requests
```

Rate limiting is performed by Nginx before `proxy_pass`, so rejected requests do not reach FastAPI.

This provides an infrastructure-level protection mechanism without requiring the application to process every incoming request.

### Rate Limiting Flow

```text
Client
   |
   | HTTP request
   v
Nginx
   |
   +---- rate limit exceeded ----> 429 Too Many Requests
   |
   | request allowed
   v
proxy_pass
   |
   v
FastAPI
```

### Separation of Responsibilities

The architecture intentionally separates application and infrastructure concerns.

FastAPI is responsible for:

- routing;
- application logic;
- request validation;
- response generation.

Nginx is responsible for:

- reverse proxying;
- proxy headers;
- request logging;
- error logging;
- upstream timing;
- HTTP security headers;
- response compression.

This separation keeps infrastructure-level concerns outside the application business logic and makes the architecture easier to extend and operate.

### Current Architecture

```text
                    ┌──────────────────┐
                    │      Client      │
                    └────────┬─────────┘
                             │
                             │ HTTP :80
                             ▼
                    ┌──────────────────┐
                    │      Nginx       │
                    │                  │
                    │ Reverse Proxy    │
                    │ Logging          │
                    │ Security Headers │
                    │ Gzip             |
                    | Rate Limiting    │
                    └────────┬─────────┘
                             │
                             │ Docker network
                             │ http://api:8000
                             ▼
                    ┌──────────────────┐
                    │     FastAPI      │
                    │                  │
                    │ Routing          │
                    │ Business Logic   │
                    │ Validation       │
                    │ Response         │
                    └──────────────────┘
```

## Project Progress

- [x] FastAPI application
- [x] Docker support
- [x] Docker Compose
- [x] Reverse proxy with Nginx
- [x] Proxy headers
- [x] Nginx access and error logging
- [x] Custom log format
- [x] Upstream response time tracking
- [x] HTTP security headers
- [x] Gzip compression
- [x] Rate limiting
- [ ] Production hardening
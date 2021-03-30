## Problem
### Wprgo: replay
| proportion | Problems                                        |
| ---------- | ----------------------------------------------- |
| 20%        | request could not be found.                     |
| 0.3%       | translating content-encoding error              |
| 1.14%      | no start tags found, skip injecting script      |
| 0.3%       | error re(de)compressing response body: identity |


> Analysis replay.log of 10,000 sites for crawl_date=Mar_1_2020
```
('serving 200 response', 840351)
("couldn't find matching request: not found", 265447)
('serving 206 response', 166872)
('serving 302 response', 46233)
('ScriptInjector(xxxxx): no start tags found, skip injecting script', 20162)
('serving 204 response', 7958)
('serving 301 response', 6655)
('http: TLS handshake error from 127.0.0.1:xxxxx: read tcp 127.0.0.1:xxxxx->127.0.0.1:xxxxx: read: connection reset by peer', 5259)
('translating Content-Encoding [gzip] -> [identity]', 3518)
('error recompressing response body: unknown compression: identity', 3518)
('Error unmarshaling request', 3247)
('serving 404 response', 3059)
('serving 307 response', 1901)
('couldn\'t find matching request: couldn\'t unmarshal response: malformed HTTP status code "-01"', 789)
('serving 403 response', 684)
('serving 101 response', 545)
('serving 400 response', 494)
('serving 303 response', 491)
('error decompressing response body: unknown compression: identity', 478)
('translating Content-Encoding [identity] -> [gzip, deflate, br]', 452)
('http: TLS handshake error from 127.0.0.1:xxxxx: EOF', 429)
('serving 304 response', 307)
('serving 201 response', 300)
('serving 202 response', 225)
('serving 503 response', 128)
('serving 401 response', 122)
('warning: client response truncated: write tcp 127.0.0.1:xxxxx->127.0.0.1:xxxxx: write: broken pipe', 99)
('serving 502 response', 63)
('serving 500 response', 56)
('serving 504 response', 33)
('serving 514 response', 30)
('serving 522 response', 27)
('translating Content-Encoding [identity] -> [gzip, deflate]', 26)
('serving 429 response', 16)
('serving 410 response', 11)
('warning: client response truncated: readfrom tcp 127.0.0.1:xxxxx->127.0.0.1:xxxxx: write tcp 127.0.0.1:xxxxx->127.0.0.1:xxxxx: write: broken pipe', 11)
('serving 405 response', 9)
('serving 412 response', 8)
('serving 422 response', 8)
('serving 521 response', 7)
('warning: client response truncated: write tcp 127.0.0.1:xxxxx->127.0.0.1:xxxxx: write: connection reset by peer', 5)
('http: TLS handshake error from 127.0.0.1:xxxxx: local error: tls: unexpected message', 5)
('serving 308 response', 4)
('serving 416 response', 4)
('serving 577 response', 4)
('serving 523 response', 4)
('serving 456 response', 4)
('serving 530 response', 3)
('serving 203 response', 2)
('serving 402 response', 2)
('serving 421 response', 2)
('serving 439 response', 2)
('serving 451 response', 1)
('serving 419 response', 1)
('serving 418 response', 1)
('serving 408 response', 1)
('serving 524 response', 1)
('translating Content-Encoding [gzip] -> []', 1)
('error recompressing response body: unknown compression:', 1)
('serving 505 response', 1)
('serving 599 response', 1)
('serving 205 response', 1)
('serving 207 response', 1)
('serving 520 response', 1)
('serving 501 response', 1)
```

### OpenWPM: unsuccessful crawl
TODO: read log script

## Analysis
### Canvas FP
### Audio FP
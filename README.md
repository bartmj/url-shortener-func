"# url-shortener-func" 

## Test endpoint

```bash
curl -X POST http://localhost:7071/api/ShortenUrl \
  -H "Content-Type: application/json" \
  -d '{"url": "https://google.com"}'

curl -i "http://localhost:7071/api/Redirect?shortCode=abc123"
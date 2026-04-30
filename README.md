# url-shortener-func

## Uruchomienie aplikacji

### Wymagania

* Azure Functions Core Tools (`func`)
* Node.js **lub** .NET (w zależności od implementacji projektu)
* (opcjonalnie) Azurite lub dostęp do Azure Storage

### Kroki

1. Przejdź do katalogu projektu:

```bash
cd url-shortener-func
```

2. Zainstaluj zależności (jeśli wymagane):

```bash
npm install
```

*(dla .NET: `dotnet restore`)*

3. Uruchom aplikację lokalnie:

```bash
func start
```

Aplikacja będzie dostępna pod adresem:

```
http://localhost:7071
```

---

## Test endpointów

### Skracanie URL

```bash
curl -X POST http://localhost:7071/api/ShortenUrl \
  -H "Content-Type: application/json" \
  -d '{"url": "https://google.com"}'
```

### Przekierowanie

```bash
curl -i "http://localhost:7071/api/Redirect?shortCode=abc123"
```

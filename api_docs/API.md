# Image to WebP Optimizer API

An API that downloads an image (up to 500MB) from a given URL, optimizes it into a lossless WEBP format while maintaining dimensions and quality, and returns the raw Base64 encoded string.

## Base URL

```
https://<your-workspace>--image-to-webp-optimizer-optimize-image.modal.run
```

## Endpoints

### Optimize Image

Optimize an image from a URL and receive it as a Base64 encoded string.

**Endpoint:** `POST /`

**Operation ID:** `optimize_image`

#### Request

**Content-Type:** `application/json`

**Body Parameters:**

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `url` | string (uri) | Yes | The absolute URL of the image to download | `https://example.com/path/to/large-image.jpg` |

**Example Request:**

```json
{
  "url": "https://example.com/path/to/large-image.jpg"
}
```

#### Responses

**200 - Success**

Successfully optimized image. Returns a raw Base64 encoded string.

**Content-Type:** `text/plain`

Returns the Base64 encoded image string.

---

**400 - Bad Request**

The image exceeds 500MB or download failed.

**Content-Type:** `application/json`

```json
{
  "detail": "Human-readable error message."
}
```

---

**422 - Validation Error**

Missing or invalid URL parameter.

**Content-Type:** `application/json`

```json
{
  "detail": [
    {
      "loc": ["body", "url"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

**500 - Internal Server Error**

Failed to process or encode the image.

**Content-Type:** `application/json`

```json
{
  "detail": "Human-readable error message."
}
```

## Schemas

### ImageRequest

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `url` | string | Yes | The absolute URL of the image to download |

### HTTPError

| Field | Type | Description |
|-------|------|-------------|
| `detail` | string | Human-readable error message |

### HTTPValidationError

| Field | Type | Description |
|-------|------|-------------|
| `detail` | array | Array of ValidationError objects |

### ValidationError

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `loc` | array | Yes | Location of the error (e.g., `["body", "url"]`) |
| `msg` | string | Yes | Error message |
| `type` | string | Yes | Error type |

## Example Usage

### cURL

```bash
curl -X POST "https://<your-workspace>--image-to-webp-optimizer-optimize-image.modal.run/" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/path/to/large-image.jpg"}'
```

### Python

```python
import requests
import base64

url = "https://<your-workspace>--image-to-webp-optimizer-optimize-image.modal.run/"
payload = {"url": "https://example.com/path/to/large-image.jpg"}

response = requests.post(url, json=payload)

if response.status_code == 200:
    # The response is a raw Base64 string
    base64_string = response.text
    
    # To decode and save the image
    image_data = base64.b64decode(base64_string)
    with open("optimized_image.webp", "wb") as f:
        f.write(image_data)
else:
    print(f"Error: {response.status_code}")
    print(response.json())
```

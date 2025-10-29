# API Reference

## Base URL

- **Production**: `https://api.dealscout.com`
- **Staging**: `https://staging.dealscout.com`
- **Local Development**: `http://localhost:8000`

## Authentication

All API requests except `/health` and authentication endpoints require a Bearer token.

```http
Authorization: Bearer <your_jwt_token>
```

### Obtaining a Token

```bash
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=yourpassword
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

---

## API Endpoints

### Authentication

#### POST /api/v1/auth/register
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "John Doe"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_verified": false,
  "subscription_tier": "free",
  "created_at": "2024-10-28T10:00:00Z"
}
```

#### POST /api/v1/auth/login
Login and receive JWT token.

**Request Body:**
```http
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=securepassword123
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

#### GET /api/v1/auth/me
Get current user information.

**Headers:**
```http
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_verified": true,
  "subscription_tier": "pro",
  "created_at": "2024-10-28T10:00:00Z"
}
```

---

### Searches

#### GET /api/v1/searches
List all searches for the current user.

**Query Parameters:**
- `skip` (integer, optional): Number of records to skip (default: 0)
- `limit` (integer, optional): Maximum records to return (default: 100, max: 100)

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "name": "iPhone Deals",
    "keywords": "iPhone 13",
    "marketplaces": ["ebay", "gumtree"],
    "location": "London",
    "min_price": 200,
    "max_price": 600,
    "status": "active",
    "check_interval_minutes": 60,
    "last_checked_at": "2024-10-28T09:30:00Z",
    "created_at": "2024-10-28T08:00:00Z"
  }
]
```

#### POST /api/v1/searches
Create a new search.

**Request Body:**
```json
{
  "name": "iPhone Deals",
  "keywords": "iPhone 13 Pro",
  "marketplaces": ["ebay", "facebook"],
  "location": "London",
  "radius_km": 50,
  "min_price": 200,
  "max_price": 600,
  "check_interval_minutes": 60
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "user_id": 1,
  "name": "iPhone Deals",
  "keywords": "iPhone 13 Pro",
  "marketplaces": ["ebay", "facebook"],
  "location": "London",
  "radius_km": 50,
  "min_price": 200,
  "max_price": 600,
  "status": "active",
  "check_interval_minutes": 60,
  "created_at": "2024-10-28T10:00:00Z"
}
```

#### GET /api/v1/searches/{search_id}
Get a specific search.

**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "iPhone Deals",
  "keywords": "iPhone 13",
  "marketplaces": ["ebay"],
  "status": "active",
  "last_checked_at": "2024-10-28T09:30:00Z"
}
```

#### PUT /api/v1/searches/{search_id}
Update a search.

**Request Body:**
```json
{
  "name": "Updated iPhone Search",
  "max_price": 500
}
```

#### DELETE /api/v1/searches/{search_id}
Delete a search.

**Response:** `200 OK`
```json
{
  "message": "Search deleted successfully"
}
```

#### POST /api/v1/searches/{search_id}/trigger
Manually trigger a search to run immediately.

**Response:** `200 OK`
```json
{
  "message": "Search triggered successfully"
}
```

---

### Listings

#### GET /api/v1/listings
Get listings with optional filters.

**Query Parameters:**
- `search_id` (integer, optional): Filter by search ID
- `marketplace` (string, optional): Filter by marketplace (ebay, facebook, gumtree, craigslist)
- `is_saved` (boolean, optional): Filter saved/unsaved listings
- `skip` (integer, optional): Pagination offset
- `limit` (integer, optional): Maximum results

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "search_id": 1,
    "external_id": "123456789",
    "marketplace": "ebay",
    "title": "iPhone 13 Pro 256GB - Like New",
    "description": "Barely used iPhone...",
    "price": 450.00,
    "currency": "USD",
    "location": "London",
    "url": "https://ebay.com/itm/123456789",
    "image_urls": ["https://..."],
    "seller_name": "TechDeals",
    "is_saved": false,
    "posted_at": "2024-10-27T15:30:00Z",
    "scraped_at": "2024-10-28T09:30:00Z"
  }
]
```

#### GET /api/v1/listings/recent
Get recent listings from the last N hours.

**Query Parameters:**
- `hours` (integer, required): Number of hours to look back (1-168)

**Response:** `200 OK` (same format as GET /listings)

#### GET /api/v1/listings/{listing_id}
Get a specific listing.

**Response:** `200 OK`
```json
{
  "id": 1,
  "title": "iPhone 13 Pro 256GB",
  "price": 450.00,
  "url": "https://ebay.com/itm/123456789"
}
```

#### PATCH /api/v1/listings/{listing_id}
Update a listing (e.g., save/unsave).

**Request Body:**
```json
{
  "is_saved": true
}
```

#### GET /api/v1/listings/saved
Get all saved listings for the current user.

**Response:** `200 OK` (same format as GET /listings)

---

### Alerts

#### GET /api/v1/alerts
List all alerts for the current user.

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "user_id": 1,
    "search_id": 1,
    "channel": "email",
    "enabled": true,
    "config": {
      "recipient": "user@example.com"
    },
    "last_triggered_at": "2024-10-28T09:30:00Z",
    "created_at": "2024-10-28T08:00:00Z"
  }
]
```

#### POST /api/v1/alerts
Create a new alert.

**Request Body:**
```json
{
  "search_id": 1,
  "channel": "email",
  "enabled": true,
  "config": {
    "recipient": "user@example.com"
  }
}
```

#### PATCH /api/v1/alerts/{alert_id}
Update an alert.

**Request Body:**
```json
{
  "enabled": false
}
```

#### DELETE /api/v1/alerts/{alert_id}
Delete an alert.

---

### Dashboard

#### GET /api/v1/dashboard/stats
Get dashboard statistics for the current user.

**Response:** `200 OK`
```json
{
  "total_searches": 5,
  "active_searches": 3,
  "total_listings": 1234,
  "new_listings_today": 45,
  "saved_listings": 12
}
```

---

### Monitoring

#### GET /health
Basic health check.

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "production"
}
```

#### GET /api/v1/monitoring/health/detailed
Detailed health check with component status.

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "timestamp": "2024-10-28T10:00:00Z",
  "components": {
    "database": {
      "status": "healthy",
      "connections": 5
    },
    "redis": {
      "status": "healthy",
      "connected_clients": 3
    },
    "celery": {
      "status": "healthy",
      "workers": 4
    }
  }
}
```

#### GET /api/v1/monitoring/metrics
Prometheus metrics endpoint.

**Response:** `200 OK` (Prometheus format)
```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",endpoint="/api/v1/searches",status="200"} 1234
...
```

---

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### HTTP Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required or failed
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

### Example Error Response

```json
{
  "detail": "Search not found"
}
```

---

## Rate Limiting

Rate limits are enforced per user:

- **Per Minute**: 60 requests
- **Per Hour**: 1000 requests

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1635432000
```

When rate limit is exceeded:
```json
HTTP/1.1 429 Too Many Requests
{
  "detail": "Rate limit exceeded. Please try again later."
}
```

---

## Pagination

List endpoints support pagination:

**Query Parameters:**
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum records to return (default: 100, max: 100)

**Example:**
```
GET /api/v1/searches?skip=0&limit=20
```

---

## Webhooks (Coming Soon)

Configure webhooks to receive real-time notifications:

```json
{
  "channel": "webhook",
  "config": {
    "url": "https://your-app.com/webhook",
    "method": "POST",
    "headers": {
      "Authorization": "Bearer your-webhook-secret"
    }
  }
}
```

**Webhook Payload:**
```json
{
  "event": "new_listing",
  "search_id": 1,
  "listing": {
    "id": 123,
    "title": "iPhone 13",
    "price": 450
  },
  "timestamp": "2024-10-28T10:00:00Z"
}
```

---

## SDKs & Libraries

Official SDKs:
- **Python**: `pip install dealscout`
- **JavaScript**: `npm install @dealscout/sdk`
- **Go**: `go get github.com/dealscout/go-sdk`

Community SDKs:
- Ruby, PHP, Java (see GitHub organization)

---

## OpenAPI Specification

Interactive API documentation available at:
- **Swagger UI**: `https://api.dealscout.com/docs`
- **ReDoc**: `https://api.dealscout.com/redoc`
- **OpenAPI JSON**: `https://api.dealscout.com/openapi.json`

---

## Support

- **Documentation**: https://docs.dealscout.com
- **API Status**: https://status.dealscout.com
- **Support Email**: support@dealscout.com
- **Community Forum**: https://community.dealscout.com

---

**Last Updated**: 2024-10-28
**API Version**: 1.0.0

# Uber - API Design

## API Overview

RESTful API with JSON responses. All endpoints require authentication via Bearer token. Real-time tracking uses WebSocket. Rate limited per user tier.

## Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register as rider or driver |
| POST | `/api/v1/auth/login` | Login, returns JWT |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| POST | `/api/v1/auth/logout` | Invalidate session |

## Rider

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/rider/profile` | Get rider profile |
| PUT | `/api/v1/rider/profile` | Update rider profile |
| GET | `/api/v1/rider/trips` | List trip history (paginated) |
| GET | `/api/v1/rider/trips/{trip_id}` | Get trip details |
| GET | `/api/v1/rider/payment-methods` | List payment methods |
| POST | `/api/v1/rider/payment-methods` | Add payment method |
| DELETE | `/api/v1/rider/payment-methods/{id}` | Remove payment method |

## Rides

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/rides/estimate` | Get fare estimate |
| POST | `/api/v1/rides/request` | Request a ride |
| GET | `/api/v1/rides/{ride_id}` | Get ride status |
| POST | `/api/v1/rides/{ride_id}/cancel` | Cancel ride |
| POST | `/api/v1/rides/{ride_id}/start` | Driver starts ride |
| POST | `/api/v1/rides/{ride_id}/complete` | Complete ride |
| POST | `/api/v1/rides/{ride_id}/rate` | Rate driver/rider |

## Driver

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/driver/profile` | Get driver profile |
| PUT | `/api/v1/driver/profile` | Update driver profile |
| POST | `/api/v1/driver/go-online` | Set driver available |
| POST | `/api/v1/driver/go-offline` | Set driver unavailable |
| GET | `/api/v1/driver/earnings` | Get earnings summary |
| GET | `/api/v1/driver/trips` | List driver's trips |
| POST | `/api/v1/driver/rides/{ride_id}/accept` | Accept ride request |
| POST | `/api/v1/driver/rides/{ride_id}/decline` | Decline ride request |

## Pricing

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/pricing/surge` | Get current surge multiplier |
| POST | `/api/v1/pricing/estimate` | Get fare estimate for route |

## Payments

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/payments/charge` | Process payment (idempotent) |
| POST | `/api/v1/payments/refund` | Refund a payment |
| GET | `/api/v1/payments/{payment_id}` | Get payment status |
| GET | `/api/v1/payments/receipts/{trip_id}` | Get trip receipt |

## WebSocket Endpoints

| Endpoint | Direction | Description |
|----------|-----------|-------------|
| `/ws/tracking` | Bidirectional | Real-time location updates |
| `/ws/ride-updates` | Server → Client | Ride status changes |
| `/ws/driver-requests` | Server → Driver | Incoming ride requests |

## Staff-Level API Design Considerations

### Fare Estimate Response
```json
{
  "ride_id": null,
  "estimated_fare": 15.50,
  "currency": "USD",
  "surge_multiplier": 1.5,
  "estimated_time": "5 min",
  "distance": "3.2 km",
  "breakdown": {
    "base_fare": 2.50,
    "per_km": 8.00,
    "per_min": 3.00,
    "surge": 2.00
  }
}
```

### Idempotency
- All payment operations require `Idempotency-Key` header
- Ride request uses `ride_request_id` to prevent duplicate bookings
- Rating uses `trip_id + rater_id` as unique constraint

### Real-time Location Update (WebSocket)
```json
{
  "type": "location_update",
  "driver_id": "d123",
  "latitude": 37.7749,
  "longitude": -122.4194,
  "timestamp": 1609459200,
  "heading": 45,
  "speed": 30
}
```

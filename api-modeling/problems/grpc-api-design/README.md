# gRPC API Design

## Problem Statement

Design a gRPC API using Protocol Buffers for a microservices architecture. Define service contracts, message types, streaming patterns, and error handling for high-performance internal service communication.

**Reference**: Educative.io, ByteByteGo

## Key Concepts

### Protobuf Service Definition

```protobuf
syntax = "proto3";

package ecommerce.v1;

service OrderService {
  rpc CreateOrder(CreateOrderRequest) returns (CreateOrderResponse);
  rpc GetOrder(GetOrderRequest) returns (Order);
  rpc ListOrders(ListOrdersRequest) returns (ListOrdersResponse);
  rpc UpdateOrderStatus(UpdateOrderStatusRequest) returns (Order);
  rpc StreamOrderUpdates(OrderIdRequest) returns (stream OrderUpdate);
}

message Order {
  string id = 1;
  string user_id = 2;
  OrderStatus status = 3;
  repeated OrderItem items = 4;
  Money total = 5;
  string created_at = 6;
}

message OrderItem {
  string product_id = 1;
  string name = 2;
  int32 quantity = 3;
  Money price = 4;
}

message Money {
  int64 amount_cents = 1;
  string currency_code = 2;
}

enum OrderStatus {
  ORDER_STATUS_UNSPECIFIED = 0;
  ORDER_STATUS_PENDING = 1;
  ORDER_STATUS_CONFIRMED = 2;
  ORDER_STATUS_SHIPPED = 3;
  ORDER_STATUS_DELIVERED = 4;
  ORDER_STATUS_CANCELLED = 5;
}
```

### Streaming Patterns
- **Server streaming**: `StreamOrderUpdates` — client subscribes to real-time order changes.
- **Client streaming**: Upload large data in chunks.
- **Bidirectional streaming**: Real-time chat, collaborative editing.

## Staff-Level Design Considerations

- **Use int64 for money**: Store amount in cents, not floating point — avoids precision issues.
- **Enum always has UNSPECIFIED**: First enum value is 0 (default) — never use it for valid data.
- **Staff insight**: Use **gRPC for internal microservices** where performance matters. Protobuf is 3-10x smaller than JSON and faster to serialize. Use **server streaming** for real-time updates (order status, notifications). Use **interceptors** for auth, logging, and tracing — don't repeat code in every RPC.

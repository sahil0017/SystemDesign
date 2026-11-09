# GraphQL API Design

## Problem Statement

Design a GraphQL API schema for an e-commerce platform with queries, mutations, subscriptions, proper type design, DataLoader for N+1 prevention, and pagination.

**Reference**: Educative.io, ByteByteGo

## Schema Design

```graphql
type Query {
  product(id: ID!): Product
  products(
    first: Int = 20
    after: String
    filter: ProductFilter
    sort: ProductSort
  ): ProductConnection!
  order(id: ID!): Order
  orders(status: OrderStatus): [Order!]!
}

type Mutation {
  createOrder(input: CreateOrderInput!): Order!
  updateOrderStatus(id: ID!, status: OrderStatus!): Order!
  cancelOrder(id: ID!): Order!
}

type Subscription {
  orderUpdated(id: ID!): Order!
  orderStatusChanged(status: OrderStatus!): Order!
}

type Product {
  id: ID!
  name: String!
  description: String
  price: Money!
  category: Category
  reviews(first: Int = 5): ReviewConnection
}

type Money {
  amount: Float!
  currency: String!
}

type ProductConnection {
  edges: [ProductEdge!]!
  pageInfo: PageInfo!
}

type ProductEdge {
  node: Product!
  cursor: String!
}

type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}

input ProductFilter {
  category: String
  minPrice: Float
  maxPrice: Float
  inStock: Boolean
}
```

## Staff-Level Design Considerations

- **Use Relay connection spec**: Cursor-based pagination with `PageInfo` — consistent across all collections.
- **DataLoader for N+1**: Batch database queries per request — one query for all products in a request instead of one per product.
- **Staff insight**: Use **query complexity analysis** to prevent abuse. A query like `{ users { orders { items { product { reviews { user { ... } } } } } }` can cause millions of DB queries. Set max depth (e.g., 5) and cost per field. Use **subscriptions** for real-time updates (order status, notifications) — clients subscribe once, server pushes changes.

# Coffee Vending Machine

## Problem Statement

Design a coffee vending machine system that supports multiple coffee types, ingredient management, payment processing, recipe customization, and maintenance alerts.

**Reference**: AlgoMaster, LLD Coding

## Requirements

### Functional Requirements
- **Coffee types**: Espresso, Cappuccino, Latte, Americano, Mocha, etc., each with a recipe.
- **Recipe management**: Define recipes with ingredient quantities and brewing parameters.
- **Ingredient management**: Track stock levels; alert when ingredients are low.
- **Payment**: Accept coins, notes, card, and mobile payment; provide change.
- **Customization**: Adjust strength, temperature, milk type, and sugar level.
- **Dispensing**: Brew coffee according to recipe; dispense into cup.
- **Maintenance**: Clean cycle alerts; error handling for jams and malfunctions.

### Non-Functional Requirements
- **Concurrency**: Handle multiple simultaneous orders (multi-dispenser machine).
- **Reliability**: 99.9% uptime; fail-safe on ingredient shortage.
- **Latency**: Order to dispensing < 30s.

## Key Design Decisions
- **State machine**: Idle → Selected → Payment → Brewing → Dispensing → Idle.
- **Strategy pattern**: Different payment methods as strategies.
- **Builder pattern**: Build coffee orders with customizable parameters.
- **Observer pattern**: Notify on low stock, maintenance alerts, and order completion.

## Class Diagram

```
┌──────────────────┐     ┌──────────────┐     ┌──────────────┐
│ VendingMachine   │────►│    Recipe    │────►│  Ingredient  │
├──────────────────┤     ├──────────────┤     ├──────────────┤
│ - machineId      │     │ - recipeId   │     │ - name       │
│ - state          │     │ - name       │     │ - quantity   │
│ - dispensers     │     │ - ingredients│     │ - threshold  │
│ - paymentSystem  │     │ - parameters │     └──────────────┘
├──────────────────┤     └──────────────┘
│ + selectCoffee() │
│ + pay()          │
│ + dispense()     │
│ + refund()       │
└──────────────────┘
```

## Staff-Level Design Considerations

### State Machine for Brewing
- **State transitions**: Idle → Selected → Payment → Brewing → Dispensing → Idle. Error → Maintenance.
- **Staff insight**: The State pattern is the canonical solution. Each state handles the same events differently (e.g., "pay" in Idle is a no-op; "pay" in Selected starts brewing).

### Ingredient Management
- **Stock check before brewing**: Validate all ingredients are available before accepting payment.
- **Staff insight**: Check stock AFTER payment but BEFORE brewing. If you check before payment and stock runs out, you've overpromed. Use a distributed lock on ingredients during the check-brew window.

### Recipe Extensibility
- **Recipe as data**: Store recipes as JSON/config, not in code. New recipes = new config, not new code.
- **Staff insight**: This is the Open-Closed Principle in action. The machine should be open for new recipes but closed for modification.

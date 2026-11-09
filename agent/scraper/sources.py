"""Source definitions and problem keyword database for detection."""

from agent.core.models import Category

# ------------------------------------------------------------------ #
#  Source definitions
# ------------------------------------------------------------------ #

SOURCES = {
    "algomaster": {
        "urls": [
            "https://algomaster.io/system-design",
            "https://algomaster.io/learn/lld",
        ],
        "type": "html",
    },
    "hellointerview": {
        "urls": [
            "https://www.hellointerview.com/learn/system-design",
        ],
        "type": "html",
    },
    "designgurus": {
        "urls": [
            "https://designgurus.io/course/grokking-the-system-design-interview",
        ],
        "type": "html",
    },
    "educative": {
        "urls": [
            "https://www.educative.io/courses/grokking-the-system-design-interview",
        ],
        "type": "html",
    },
    "github_trending": {
        "urls": [
            "https://github.com/trending?since=monthly",
        ],
        "type": "github",
    },
    "bytebytego": {
        "urls": [
            "https://bytebytego.com/",
        ],
        "type": "html",
    },
    "system-design-primer": {
        "urls": [
            "https://raw.githubusercontent.com/donnemartin/system-design-primer/master/README.md",
        ],
        "type": "markdown",
    },
    "system-design-interview": {
        "urls": [
            "https://raw.githubusercontent.com/checkcheckzz/system-design-interview/master/README.md",
        ],
        "type": "markdown",
    },
    "awesome-system-design": {
        "urls": [
            "https://raw.githubusercontent.com/ashishps1/awesome-system-design-resources/main/README.md",
            "https://raw.githubusercontent.com/ashishps1/awesome-low-level-design/main/README.md",
        ],
        "type": "markdown",
    },
}

# Comprehensive problem keyword database for detection
PROBLEM_KEYWORDS = {
    # HLD - System Design
    "url shortener": (Category.HLD, ["URL Shortener", "TinyURL", "Bitly"]),
    "tiktok": (Category.HLD, ["TikTok", "Short Video", "Video Feed"]),
    "youtube": (Category.HLD, ["YouTube", "Video Streaming", "Video Platform"]),
    "whatsapp": (Category.HLD, ["WhatsApp", "Messaging App", "Chat Application"]),
    "uber": (Category.HLD, ["Uber", "Ride Sharing", "Ride Hailing"]),
    "instagram": (Category.HLD, ["Instagram", "Photo Sharing", "Image Feed"]),
    "linkedin": (Category.HLD, ["LinkedIn", "Professional Network", "Social Graph"]),
    "twitter": (Category.HLD, ["Twitter", "X Platform", "Microblog", "Tweet"]),
    "amazon": (Category.HLD, ["Amazon", "E-commerce", "Online Shopping"]),
    "spotify": (Category.HLD, ["Spotify", "Music Streaming", "Audio Platform"]),
    "netflix": (Category.HLD, ["Netflix", "Video on Demand", "Streaming Service"]),
    "google docs": (Category.HLD, ["Google Docs", "Collaborative Editor", "Real-time Editor"]),
    "rate limiter": (Category.HLD, ["Rate Limiter", "Throttling", "Rate Limiting"]),
    "web crawler": (Category.HLD, ["Web Crawler", "Spider", "Search Crawler"]),
    "chat system": (Category.HLD, ["Chat System", "Chat Application", "Messaging"]),
    "news feed": (Category.HLD, ["News Feed", "Social Feed", "Activity Feed"]),
    "rag system": (Category.HLD, ["RAG", "Retrieval Augmented Generation", "Vector Search"]),
    "llm inference": (Category.HLD, ["LLM Inference", "Model Serving", "AI Inference"]),
    "fraud detection": (Category.HLD, ["Fraud Detection", "Fraud Prevention"]),
    "flash sale": (Category.HLD, ["Flash Sale", "Lightning Deal"]),
    "ad platform": (Category.HLD, ["Ad Platform", "Ad Tech", "Advertising"]),
    "ci/cd pipeline": (Category.HLD, ["CI/CD", "Continuous Integration", "Deployment Pipeline"]),
    "semantic search": (Category.HLD, ["Semantic Search", "Vector Search", "Similarity Search"]),
    "digital wallet": (Category.HLD, ["Digital Wallet", "Payment Wallet", "E-wallet"]),
    "workflow orchestration": (Category.HLD, ["Workflow", "Orchestration", "DAG Execution"]),
    "live streaming": (Category.HLD, ["Live Streaming", "Video Live", "Twitch"]),
    "notification system": (Category.HLD, ["Notification", "Push Notification"]),
    "payment system": (Category.HLD, ["Payment", "Payment Gateway"]),
    "dns system": (Category.HLD, ["DNS", "Domain Name System"]),
    "web server": (Category.HLD, ["Web Server", "HTTP Server"]),
    "load balancer": (Category.HLD, ["Load Balancer", "LB"]),
    "cdn": (Category.HLD, ["CDN", "Content Delivery Network"]),
    "message queue": (Category.HLD, ["Message Queue", "MQ", "Kafka"]),
    "cache system": (Category.HLD, ["Cache", "Caching System"]),
    "search engine": (Category.HLD, ["Search Engine", "Full Text Search"]),
    "recommendation system": (Category.HLD, ["Recommendation", "Rec System"]),
    "analytics pipeline": (Category.HLD, ["Analytics", "Data Pipeline"]),
    "log aggregation": (Category.HLD, ["Log Aggregation", "Logging System"]),
    "file storage": (Category.HLD, ["File Storage", "Dropbox", "Cloud Storage"]),
    "image processing": (Category.HLD, ["Image Processing", "Image Service"]),
    "autocomplete": (Category.HLD, ["Autocomplete", "Typeahead", "Search Suggestions"]),
    "hit counter": (Category.HLD, ["Hit Counter", "Page Counter"]),
    "google maps": (Category.HLD, ["Google Maps", "Map Service"]),
    "stock broker": (Category.HLD, ["Stock Broker", "Trading Platform"]),
    "hotel booking": (Category.HLD, ["Hotel Booking", "Accommodation"]),
    "flight booking": (Category.HLD, ["Flight Booking", "Airline"]),
    "cricinfo": (Category.HLD, ["CricInfo", "Cricket Score", "Live Score"]),
    # LLD - Object Oriented Design
    "parking lot": (Category.LLD, ["Parking Lot", "Parking"]),
    "lru cache": (Category.LLD, ["LRU Cache", "Least Recently Used"]),
    "lfu cache": (Category.LLD, ["LFU Cache", "Least Frequently Used"]),
    "snake and ladder": (Category.LLD, ["Snake and Ladder", "Snakes and Ladders"]),
    "snake game": (Category.LLD, ["Snake Game"]),
    "tic tac toe": (Category.LLD, ["Tic Tac Toe", "Tic-Tac-Toe"]),
    "vending machine": (Category.LLD, ["Vending Machine"]),
    "stack overflow": (Category.LLD, ["Stack Overflow", "Q&A Platform"]),
    "elevator system": (Category.LLD, ["Elevator", "Lift System"]),
    "pub sub system": (Category.LLD, ["Pub Sub", "Publisher Subscriber"]),
    "chess": (Category.LLD, ["Chess Game", "Chess"]),
    "coffee vending": (Category.LLD, ["Coffee Vending", "Coffee Machine"]),
    "restaurant management": (Category.LLD, ["Restaurant", "Restaurant Management"]),
    "movie ticket booking": (Category.LLD, ["Movie Ticket", "Cinema Booking"]),
    "online auction": (Category.LLD, ["Online Auction", "Auction"]),
    "food delivery": (Category.LLD, ["Food Delivery", "Swiggy", "Zomato"]),
    "ride sharing": (Category.LLD, ["Ride Sharing", "Ride Share"]),
    "splitwise": (Category.LLD, ["Splitwise", "Expense Splitting"]),
    "text editor": (Category.LLD, ["Text Editor", "Editor"]),
    "atm": (Category.LLD, ["ATM", "Automated Teller"]),
    "logging framework": (Category.LLD, ["Logging", "Logger"]),
    "car rental": (Category.LLD, ["Car Rental", "Vehicle Rental"]),
    "library management": (Category.LLD, ["Library", "Book Management"]),
    "traffic signal": (Category.LLD, ["Traffic Signal", "Traffic Light"]),
    "concert booking": (Category.LLD, ["Concert Booking", "Event Ticket"]),
    "social network": (Category.LLD, ["Social Network", "Social Media"]),
    "digital wallet": (Category.LLD, ["Digital Wallet", "Wallet"]),
    "airline management": (Category.LLD, ["Airline", "Flight Management"]),
    "stock exchange": (Category.LLD, ["Stock Exchange", "Trading"]),
    "course registration": (Category.LLD, ["Course Registration", "University"]),
    # Distributed Systems
    "vector database": (Category.DISTRIBUTED_SYSTEMS, ["Vector DB", "Vector Database", "ANN"]),
    "feature store": (Category.DISTRIBUTED_SYSTEMS, ["Feature Store", "ML Features"]),
    "secret management": (Category.DISTRIBUTED_SYSTEMS, ["Secret Management", "Vault"]),
    "distributed cache": (Category.DISTRIBUTED_SYSTEMS, ["Distributed Cache", "Cache Cluster"]),
    "distributed lock": (Category.DISTRIBUTED_SYSTEMS, ["Distributed Lock", "Lock Service"]),
    "distributed tracing": (Category.DISTRIBUTED_SYSTEMS, ["Distributed Tracing", "Tracing"]),
    "distributed config": (Category.DISTRIBUTED_SYSTEMS, ["Distributed Config", "Config Service"]),
    "event sourcing": (Category.DISTRIBUTED_SYSTEMS, ["Event Sourcing", "Event Store"]),
    "circuit breaker": (Category.DISTRIBUTED_SYSTEMS, ["Circuit Breaker"]),
    "idempotency": (Category.DISTRIBUTED_SYSTEMS, ["Idempotency", "Idempotent"]),
    "saga pattern": (Category.DISTRIBUTED_SYSTEMS, ["Saga", "Saga Pattern"]),
    "consistent hashing": (Category.DISTRIBUTED_SYSTEMS, ["Consistent Hashing"]),
    "leader election": (Category.DISTRIBUTED_SYSTEMS, ["Leader Election", "Election"]),
    # Trade-offs
    "sql vs nosql": (Category.TRADEOFFS, ["SQL vs NoSQL", "Relational vs Non-relational"]),
    "monolith vs microservices": (Category.TRADEOFFS, ["Monolith vs Microservices"]),
    "rest vs grpc": (Category.TRADEOFFS, ["REST vs gRPC"]),
    "graphql vs rest": (Category.TRADEOFFS, ["GraphQL vs REST"]),
    "vector db vs traditional": (Category.TRADEOFFS, ["Vector DB vs Traditional"]),
    "edge vs centralized": (Category.TRADEOFFS, ["Edge vs Centralized", "Edge Computing"]),
    "build vs buy": (Category.TRADEOFFS, ["Build vs Buy", "Buy vs Build"]),
    # Java
    "virtual threads": (Category.JAVA, ["Virtual Threads", "Project Loom"]),
    "record patterns": (Category.JAVA, ["Record Patterns", "Pattern Switch"]),
    "pattern matching": (Category.JAVA, ["Pattern Matching", "Instanceof"]),
    "structured concurrency": (Category.JAVA, ["Structured Concurrency"]),
    "stamped lock": (Category.JAVA, ["StampedLock", "Stamped Lock"]),
    "lock free": (Category.JAVA, ["Lock Free", "Lock-free"]),
    "disruptor": (Category.JAVA, ["Disruptor", "Disruptor Pattern"]),
    "actor model": (Category.JAVA, ["Actor", "Actor Model"]),
}

# Foundation ER diagram

```mermaid
erDiagram
    CAMPAIGNS ||--o{ CAMPAIGN_SESSIONS : contains
    CAMPAIGNS ||--o{ EVENTS : records
    CAMPAIGN_SESSIONS o|--o{ EVENTS : captures
    EVENTS ||--o{ EVENT_LINKS : links
    CAMPAIGNS ||--o{ DICE_LOGS : records
    CAMPAIGN_SESSIONS o|--o{ DICE_LOGS : includes
    EVENTS o|--o{ DICE_LOGS : contextualizes
    EVENTS o|--o{ EVENTS : supersedes
```


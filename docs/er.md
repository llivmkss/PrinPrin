# ER-диаграмма

```mermaid
erDiagram
    TABLES ||--o{ BOOKINGS : "на столик бронируют"
    TABLES ||--o{ TABLE_FEATURES : "имеет"
    FEATURES ||--o{ TABLE_FEATURES : "есть у"

    TABLES {
        int number PK "номер столика"
        int capacity "вместимость, CHECK > 0"
        string zone "зона ресторана"
        bool is_available "доступен ли столик"
    }

    BOOKINGS {
        int id PK "идентификатор брони"
        int table_number FK "столик"
        int guests "гостей, CHECK > 0"
        datetime start "начало брони"
        string customer_name "имя клиента"
        string customer_phone "телефон клиента"
        string status "active или cancelled"
    }

    FEATURES {
        int id PK
        string name UK "удобство, например у окна"
    }

    TABLE_FEATURES {
        int table_number PK, FK
        int feature_id PK, FK
    }

    ADMINS {
        int id PK
        string login UK "логин"
        string password_hash "хеш пароля"
    }
```

## Ограничения

- `tables.number`, `bookings.id`, `features.id`, `admins.id` — первичные ключи (PK).
- `bookings.table_number` — внешний ключ на `tables.number`, `ON DELETE RESTRICT`: столик с бронями удалить нельзя (п. 4.2.6 ТЗ).
- `table_features` — связующая таблица для связи «многие ко многим»; при удалении столика или удобства её строки удаляются (`ON DELETE CASCADE`).
- `features.name`, `admins.login` — уникальные (UNIQUE).
- `tables.capacity > 0`, `bookings.guests > 0` — проверки (CHECK).
- `bookings.status` принимает только `active` или `cancelled`.

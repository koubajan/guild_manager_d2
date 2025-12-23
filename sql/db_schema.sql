CREATE TABLE classes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    description TEXT
);

CREATE TABLE heroes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    level INT DEFAULT 1,
    gold_balance FLOAT DEFAULT 0.0,
    is_active BOOLEAN DEFAULT TRUE,
    join_date DATETIME DEFAULT NOW(),
    class_id INT,
    FOREIGN KEY (class_id) REFERENCES classes(id)
);

CREATE TABLE items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    rarity ENUM('Common', 'Rare', 'Epic', 'Legendary') NOT NULL,
    value FLOAT DEFAULT 0
);

CREATE TABLE inventory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    hero_id INT,
    item_id INT,
    quantity INT DEFAULT 1,
    FOREIGN KEY (hero_id) REFERENCES heroes(id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES items(id)
);

CREATE TABLE quest_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    hero_id INT,
    quest_name VARCHAR(200),
    status VARCHAR(50),
    FOREIGN KEY (hero_id) REFERENCES heroes(id)
);

CREATE VIEW view_guild_wealth AS
SELECT h.name, h.gold_balance, SUM(i.value * inv.quantity) as inventory_value
FROM heroes h
LEFT JOIN inventory inv ON h.id = inv.hero_id
LEFT JOIN items i ON inv.item_id = i.id
GROUP BY h.id;

CREATE VIEW view_active_heroes AS
SELECT name, level, join_date FROM heroes WHERE is_active = 1;

INSERT INTO classes (name, description) VALUES ('Warrior', 'Melee fighter'), ('Mage', 'Spell caster');
INSERT INTO items (name, rarity, value) VALUES ('Wooden Sword', 'Common', 10.0);
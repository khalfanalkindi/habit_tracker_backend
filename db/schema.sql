-- Habit tracker MySQL schema (utf8mb4).
-- TablePlus: File → Open SQL → run this file (or paste into a query tab).
-- CLI: mysql -u root -p < db/schema.sql
-- If you prefer Python instead of this file for tables: create the empty database
-- (first two statements below), set DATABASE_URL, then run: python -m app.db.init_db

CREATE DATABASE IF NOT EXISTS habit_tracker
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE habit_tracker;

-- ---------------------------------------------------------------------------
-- users
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
  id CHAR(36) NOT NULL,
  email VARCHAR(255) NOT NULL,
  display_name VARCHAR(255) NOT NULL,
  password_hash VARCHAR(255) NULL COMMENT 'Optional until real auth is wired',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_users_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
-- food_options — personal food catalog (per user)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS food_options (
  id CHAR(36) NOT NULL,
  user_id CHAR(36) NOT NULL,
  name VARCHAR(255) NOT NULL,
  calories_per_serving DECIMAL(10, 2) NOT NULL,
  protein_g_per_serving DECIMAL(10, 2) NOT NULL,
  carbs_g_per_serving DECIMAL(10, 2) NOT NULL,
  fat_g_per_serving DECIMAL(10, 2) NOT NULL,
  serving_size DECIMAL(12, 3) NOT NULL,
  serving_unit VARCHAR(32) NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY ix_food_options_user_id (user_id),
  CONSTRAINT fk_food_options_user
    FOREIGN KEY (user_id) REFERENCES users (id)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
-- food_log_entries — what was eaten on a calendar day
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS food_log_entries (
  id CHAR(36) NOT NULL,
  user_id CHAR(36) NOT NULL,
  food_option_id CHAR(36) NOT NULL,
  log_date DATE NOT NULL,
  meal_type VARCHAR(32) NOT NULL COMMENT 'breakfast, lunch, dinner, snacks',
  quantity DECIMAL(12, 3) NOT NULL COMMENT 'Number of servings',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY ix_food_log_user_date (user_id, log_date),
  KEY ix_food_log_food_option (food_option_id),
  CONSTRAINT fk_food_log_user
    FOREIGN KEY (user_id) REFERENCES users (id)
    ON DELETE CASCADE,
  CONSTRAINT fk_food_log_food_option
    FOREIGN KEY (food_option_id) REFERENCES food_options (id)
    ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
-- exercise_entries — weekly plan + completion (matches current frontend model)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS exercise_entries (
  id CHAR(36) NOT NULL,
  user_id CHAR(36) NOT NULL,
  day_of_week TINYINT UNSIGNED NOT NULL COMMENT '0=Sunday .. 6=Saturday (JS getDay)',
  exercise_type VARCHAR(32) NOT NULL COMMENT 'gym, walk, cardio, swim, yoga, cycling',
  duration_minutes INT UNSIGNED NULL,
  completed TINYINT(1) NOT NULL DEFAULT 0,
  completed_on_date DATE NULL COMMENT 'Set when completed is true',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY ix_exercise_user_dow (user_id, day_of_week),
  CONSTRAINT fk_exercise_user
    FOREIGN KEY (user_id) REFERENCES users (id)
    ON DELETE CASCADE,
  CONSTRAINT chk_exercise_day_of_week CHECK (day_of_week BETWEEN 0 AND 6)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

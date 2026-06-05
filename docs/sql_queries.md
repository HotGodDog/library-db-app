# SQL Запросы

## Q1: Книги с авторами и жанрами

```sql
SELECT 
    b.title,
    a.last_name || ' ' || a.first_name AS author,
    c.name AS category,
    b.year,
    b.available || ' / ' || b.total AS availability
FROM books b
JOIN authors a ON b.author_id = a.author_id
JOIN categories c ON b.category_id = c.category_id
WHERE b.is_visible = 1
ORDER BY b.title;
```

**Назначение:** Формирование каталога для читателей.

---

## Q2: Поиск книг по названию или автору

```sql
SELECT 
    b.book_id,
    b.title,
    a.last_name,
    a.first_name,
    b.available
FROM books b
JOIN authors a ON b.author_id = a.author_id
WHERE b.is_visible = 1
  AND (b.title LIKE '%Война%' 
       OR a.last_name LIKE '%Толстой%')
ORDER BY b.title;
```

**Назначение:** Поиск в каталоге (используется на главной странице).

---

## Q3: Просроченные выдачи с деталями

```sql
SELECT 
    r.full_name AS reader,
    r.email,
    b.title AS book,
    l.issue_date,
    l.due_date,
    julianday('now') - julianday(l.due_date) AS days_overdue
FROM loans l
JOIN readers r ON l.reader_id = r.reader_id
JOIN books b ON l.book_id = b.book_id
WHERE l.returned = 0 
  AND l.due_date < DATE('now')
ORDER BY days_overdue DESC;
```

**Назначение:** Контроль просрочек для библиотекаря.

---

## Q4: Читатели в чёрном списке с просрочками

```sql
SELECT 
    r.reader_id,
    r.full_name,
    r.email,
    COUNT(l.loan_id) AS overdue_count,
    MAX(julianday('now') - julianday(l.due_date)) AS max_days_overdue
FROM readers r
JOIN loans l ON r.reader_id = l.reader_id
WHERE r.is_blacklisted = 1
  AND l.returned = 0
  AND l.due_date < DATE('now')
GROUP BY r.reader_id
ORDER BY max_days_overdue DESC;
```

**Назначение:** Анализ причин блокировки читателей.

---

## Q5: Статистика по жанрам

```sql
SELECT 
    c.name AS category,
    COUNT(b.book_id) AS book_count,
    SUM(b.total) AS total_copies,
    SUM(b.available) AS available_copies
FROM categories c
LEFT JOIN books b ON c.category_id = b.category_id
GROUP BY c.category_id
ORDER BY book_count DESC;
```

**Назначение:** Статистика книжного фонда.

---

## Q6: Активные выдачи читателя

```sql
SELECT 
    b.title,
    l.issue_date,
    l.due_date,
    l.extensions,
    CASE 
        WHEN l.due_date < DATE('now') THEN 'Просрочено'
        ELSE 'Активно'
    END AS status
FROM loans l
JOIN books b ON l.book_id = b.book_id
WHERE l.reader_id = ?
  AND l.returned = 0
ORDER BY l.due_date;
```

**Назначение:** Личный кабинет читателя («Мои выдачи»).

---

## Q7: Популярность книг (по количеству выдач)

```sql
SELECT 
    b.title,
    a.last_name AS author,
    COUNT(l.loan_id) AS loan_count
FROM books b
JOIN authors a ON b.author_id = a.author_id
LEFT JOIN loans l ON b.book_id = l.book_id
GROUP BY b.book_id
ORDER BY loan_count DESC
LIMIT 10;
```

**Назначение:** Рейтинг популярных книг для статистики.

---

## Q8: Эффективность работы библиотекарей

```sql
SELECT 
    e.full_name,
    COUNT(DISTINCT l.loan_id) AS total_issues,
    COUNT(DISTINCT CASE WHEN l.returned = 1 THEN l.loan_id END) AS total_returns
FROM employees e
LEFT JOIN loans l ON e.employee_id = l.employee_id
WHERE e.position_id = (SELECT position_id FROM positions WHERE name = 'Библиотекарь')
GROUP BY e.employee_id
ORDER BY total_issues DESC;
```

**Назначение:** Отчёт по активности сотрудников.

---

## Q9: Динамика выдач по месяцам

```sql
SELECT 
    strftime('%Y-%m', l.issue_date) AS month,
    COUNT(*) AS issue_count,
    COUNT(DISTINCT l.reader_id) AS unique_readers
FROM loans l
WHERE l.issue_date >= DATE('now', '-12 months')
GROUP BY month
ORDER BY month;
```

**Назначение:** Анализ сезонности спроса на книги.

---

## Q10: Проверка перед выдачей (валидация)

```sql
SELECT 
    r.is_blacklisted,
    r.is_active,
    b.available,
    CASE 
        WHEN r.is_blacklisted = 1 THEN 'Читатель в чёрном списке'
        WHEN r.is_active = 0 THEN 'Аккаунт неактивен'
        WHEN b.available <= 0 THEN 'Нет доступных экземпляров'
        ELSE 'OK'
    END AS validation_result
FROM readers r, books b
WHERE r.reader_id = ? AND b.book_id = ?;
```

**Назначение:** Проверка возможности выдачи перед созданием записи.

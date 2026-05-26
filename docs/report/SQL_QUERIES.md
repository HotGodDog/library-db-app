# SQL-запросы для АСУБ (Автоматизированная система управления библиотекой)

## 1. ПРОСТОЙ ЗАПРОС: Список всех книг в каталоге
### Описание: Выводит названия и год издания доступных книг
SELECT 
    b.title,
    b.year_published,
    a.last_name || ' ' || a.first_name AS author
FROM books b
JOIN authors a ON b.author_id = a.author_id
WHERE b.available > 0 AND b.is_visible = 1
ORDER BY b.title;


## 2. ЗАПРОС С ПАРАМЕТРОМ: Поиск книг по названию или автору
### Описание: Используется в строке поиска на главной странице
### Параметр: ? — строка поиска
SELECT 
    b.book_id,
    b.title,
    a.last_name || ' ' || a.first_name AS author_name,
    c.name AS category_name,
    b.year_published,
    b.available,
    b.total_copies
FROM books b
LEFT JOIN authors a ON b.author_id = a.author_id
LEFT JOIN categories c ON b.category_id = c.category_id
WHERE b.title LIKE '%' || ? || '%' 
   OR a.last_name LIKE '%' || ? || '%'
   OR a.first_name LIKE '%' || ? || '%'
ORDER BY b.title;


## 3. ВЫЧИСЛЯЕМЫЙ ЗАПРОС: Статистика библиотеки
### Описание: Агрегатные показатели для панели статистики
SELECT 
    (SELECT COUNT(*) FROM books) AS total_books,
    (SELECT SUM(total_copies) FROM books) AS total_copies,
    (SELECT SUM(available) FROM books) AS available_copies,
    (SELECT COUNT(*) FROM readers WHERE is_active = 1) AS total_readers,
    (SELECT COUNT(*) FROM loans WHERE return_date IS NULL) AS active_loans,
    (SELECT COUNT(*) FROM loans) AS total_loans;


## 4. ЗАПРОС С JOIN: Журнал выдач и возвратов
### Описание: Полная информация по всем операциям с книгами
SELECT 
    l.loan_id,
    l.loan_date,
    l.due_date,
    l.return_date,
    l.status,
    b.title AS book_title,
    r.last_name || ' ' || r.first_name AS reader_name,
    e.last_name || ' ' || e.first_name AS employee_name
FROM loans l
JOIN books b ON l.book_id = b.book_id
JOIN readers r ON l.reader_id = r.reader_id
LEFT JOIN employees e ON l.employee_id = e.employee_id
ORDER BY l.loan_date DESC;


## 5. ЗАПРОС С УСЛОВИЕМ: Просроченные выдачи
### Описание: Книги, которые не вернули в срок
SELECT 
    l.loan_id,
    b.title AS book_title,
    r.last_name || ' ' || r.first_name AS reader_name,
    r.phone AS reader_phone,
    l.due_date,
    julianday('now') - julianday(l.due_date) AS days_overdue
FROM loans l
JOIN books b ON l.book_id = b.book_id
JOIN readers r ON l.reader_id = r.reader_id
WHERE l.return_date IS NULL 
  AND l.due_date < DATE('now')
ORDER BY days_overdue DESC;


## 6. ЗАПРОС С ГРУППИРОВКОЙ: Популярность книг
### Описание: Сколько раз каждая книга была выдана
SELECT 
    b.title,
    a.last_name || ' ' || a.first_name AS author,
    COUNT(l.loan_id) AS times_issued
FROM books b
LEFT JOIN loans l ON b.book_id = l.book_id
LEFT JOIN authors a ON b.author_id = a.author_id
GROUP BY b.book_id
ORDER BY times_issued DESC;


## 7. ЗАПРОС С ПОДЗАПРОСОМ: Читатели с книгами на руках
### Описание: Список активных читателей с количеством книг
SELECT 
    r.reader_id,
    r.last_name || ' ' || r.first_name AS full_name,
    r.phone,
    r.email,
    (SELECT COUNT(*) 
     FROM loans l2 
     WHERE l2.reader_id = r.reader_id 
       AND l2.return_date IS NULL) AS active_loans_count
FROM readers r
WHERE r.is_active = 1
  AND EXISTS (
      SELECT 1 FROM loans l 
      WHERE l.reader_id = r.reader_id 
        AND l.return_date IS NULL
  )
ORDER BY active_loans_count DESC;


## 8. ЗАПРОС НА ИЗМЕНЕНИЕ: Выдача книги (триггер/процедура)
### Описание: Уменьшает available при выдаче
UPDATE books 
SET available = available - 1 
WHERE book_id = ? AND available > 0;

### Соответствующая вставка в loans:
INSERT INTO loans (book_id, reader_id, employee_id, loan_date, due_date, status)
VALUES (?, ?, ?, DATE('now'), DATE('now', '+14 days'), 'active');


## 9. ЗАПРОС НА ИЗМЕНЕНИЕ: Возврат книги
### Описание: Обновляет дату возврата и увеличивает available
UPDATE loans 
SET return_date = DATE('now'), status = 'returned'
WHERE loan_id = ? AND return_date IS NULL;

UPDATE books 
SET available = available + 1 
WHERE book_id = (SELECT book_id FROM loans WHERE loan_id = ?);


## 10. ЗАПРОС С ОКОННЫМИ ФУНКЦИЯМИ: Рейтинг читателей по активности
### Описание: Топ читателей с рангом по количеству выдач
SELECT 
    r.last_name || ' ' || r.first_name AS reader_name,
    COUNT(l.loan_id) AS total_loans,
    RANK() OVER (ORDER BY COUNT(l.loan_id) DESC) AS activity_rank
FROM readers r
LEFT JOIN loans l ON r.reader_id = l.reader_id
WHERE r.is_active = 1
GROUP BY r.reader_id
ORDER BY activity_rank;

SELECT name FROM sqlite_master WHERE type='table';

-- structure of a table
PRAGMA table_info(InvoiceLine);
PRAGMA table_info(Track);
PRAGMA table_info(Invoice);
PRAGMA table_info(Customer);


--top-selling products
SELECT 
    Track.Name AS Product,
    SUM(InvoiceLine.Quantity) AS TotalSold
FROM InvoiceLine
JOIN Track ON InvoiceLine.TrackId = Track.TrackId
GROUP BY Track.TrackId
ORDER BY TotalSold DESC
LIMIT 10;


--revenue per region
SELECT 
    Customer.Country,
    SUM(Invoice.Total) AS Revenue
FROM Invoice
JOIN Customer ON Invoice.CustomerId = Customer.CustomerId
GROUP BY Customer.Country
ORDER BY Revenue DESC;


-- monthly performance
SELECT 
    strftime('%Y-%m', InvoiceDate) AS Month,
    SUM(Total) AS MonthlyRevenue
FROM Invoice
GROUP BY Month
ORDER BY Month;


--combining Product + Sales

SELECT 
    Artist.Name AS Artist,
    Track.Name AS Track,
    SUM(InvoiceLine.Quantity) AS UnitsSold,
    SUM(InvoiceLine.UnitPrice * InvoiceLine.Quantity) AS Revenue
FROM InvoiceLine
JOIN Track ON InvoiceLine.TrackId = Track.TrackId
JOIN Album ON Track.AlbumId = Album.AlbumId
JOIN Artist ON Album.ArtistId = Artist.ArtistId
GROUP BY Track.TrackId
ORDER BY Revenue DESC
LIMIT 10;


-- bonus window function 
SELECT *
FROM (
    SELECT 
        Customer.Country,
        Track.Name AS Track,
        SUM(InvoiceLine.UnitPrice * InvoiceLine.Quantity) AS Revenue,
        RANK() OVER (
            PARTITION BY Customer.Country 
            ORDER BY SUM(InvoiceLine.UnitPrice * InvoiceLine.Quantity) DESC
        ) AS Rank
    FROM InvoiceLine
    JOIN Invoice ON InvoiceLine.InvoiceId = Invoice.InvoiceId
    JOIN Customer ON Invoice.CustomerId = Customer.CustomerId
    JOIN Track ON InvoiceLine.TrackId = Track.TrackId
    GROUP BY Customer.Country, Track.TrackId
) AS RankedSales
WHERE Rank = 1;


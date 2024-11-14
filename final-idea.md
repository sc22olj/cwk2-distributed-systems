Spacy pipeline in one function for analysing text

https://williamandrewgriffin.com/best-way-to-deploy-spacy-to-azure-functions/

Sentiment analysis for business reviews
- Use google, tripadvisor and trustpilot review APIs to collate reviews of a business into a central database
- For large businesses, it may be hard to read over all reviews. We need a way of analysing them quickly
- Any time the database is updated, a function performs sentiment analysis on the last 15 (adjustable) reviews, allowing the 
business owner to get insight into problems quickly
- Also classify the problematic reviews into categories

Benefits
- Allows collation of reviews from multiple sources
- Allows quick insight into problems without needing to read every review

CREATE TABLE customer_reviews (
    db_review_id UNIQUEIDENTIFIER PRIMARY KEY,
    api_review_id NVARCHAR,
    rating INT CHECK (rating >= 1 AND rating <= 5),
    review_text NVARCHAR NOT NULL,                                
    date_added DATETIME2(0) DEFAULT CURRENT_TIMESTAMP,
);

Server=tcp:ozzy-server.database.windows.net,1433;Initial Catalog=ozzy-database;Persist Security Info=False;User ID=ozzy;Password={X[lrA:"QZS[]4N8Zzlw)};MultipleActiveResultSets=False;Encrypt=True;TrustServerCertificate=False;Connection Timeout=30;

X[lrA:"QZS[]4N8Zzlw)

ntfy.sh
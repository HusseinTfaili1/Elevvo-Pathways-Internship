import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_excel("Online_Retail.xlsx")
print(df.head())

# Convert InvoiceDate to datetime
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])

# Reference Date to calculate recency
reference_date = df['InvoiceDate'].max() + pd.Timedelta(days=1)

# Recency calculation
recency_df = df.groupby('CustomerID').agg({'InvoiceDate': lambda x: (reference_date - x.max()).days})
recency_df.rename(columns={'InvoiceDate': 'Recency'}, inplace=True)

# Top 10 Recent Customers
last_purchase = df.groupby('CustomerID')['InvoiceDate'].max().reset_index()
last_purchase = last_purchase.set_index('CustomerID')
top_recent = recency_df.sort_values(by='Recency').head(10)
top_recent = top_recent.join(last_purchase)
print("Top 10 Most Recent Customers (with last purchase date):")
print(top_recent[['Recency', 'InvoiceDate']])


# Plotting Recency
plt.figure(figsize=(8,4))
sns.histplot(recency_df['Recency'], bins=30, kde=False, color='teal')
plt.title('Customer Recency Distribution', fontsize=16)
plt.xlabel('Days Since Last Purchase')
plt.ylabel('Number of Customers')
plt.show()

# Customer Recency Boxplot
plt.figure(figsize=(8,4))
sns.boxplot(x=recency_df['Recency'], color='teal')
plt.title('Customer Recency Boxplot', fontsize=16)
plt.xlabel('Days Since Last Purchase')
plt.show()

# Customer Recency Density Plot
plt.figure(figsize=(8,4))
sns.kdeplot(recency_df['Recency'], fill=True, color='teal')
plt.title('Customer Recency Density Plot', fontsize=16)
plt.xlabel('Days Since Last Purchase')
plt.ylabel('Density')
plt.show()



#Calculating Frequency and Monetary values
frequency_df = df.groupby('CustomerID').agg({'InvoiceNo': 'nunique'}) #For each customer, it counts the number of unique invoices they have 
frequency_df.rename(columns={'InvoiceNo': 'Frequency'}, inplace=True)

df['SalesAmount'] = df['UnitPrice'] * df['Quantity']
monetary_df = df.groupby('CustomerID').agg({'SalesAmount': 'sum'}) #total money spent by each customer
monetary_df.rename(columns={'SalesAmount': 'Monetary'}, inplace=True)

#merging RFM DataFrames
rfm = recency_df.merge(frequency_df, on='CustomerID')
rfm = rfm.merge(monetary_df, on='CustomerID')


#Customer Frequency Distribution
plt.figure(figsize=(8,4))
sns.histplot(rfm['Frequency'], bins=30, kde=False, color='orange')
plt.title('Customer Frequency Distribution', fontsize=16)
plt.xlabel('Number of Purchases')
plt.ylabel('Number of Customers')
plt.tight_layout()
plt.show()

# Top 10 Most Frequent Buyers
top_freq = rfm.sort_values(by='Frequency', ascending=False).head(10)
plt.figure(figsize=(10,6))
sns.barplot(y=top_freq.index.astype(str), x=top_freq['Frequency'], color='blue')
plt.title('Top 10 Most Frequent Buyers', fontsize=16)
plt.ylabel('CustomerID')
plt.xlabel('Number of Purchases')
plt.tight_layout()
plt.show()


# Monetary Distribution
plt.figure(figsize=(8,4))
sns.histplot(rfm['Monetary'], bins=30, kde=False, color='green')
plt.title('Customer Monetary Distribution', fontsize=16)
plt.xlabel('Total Spend (£)')
plt.ylabel('Number of Customers')
plt.tight_layout()
plt.show()

#Top 10 Customers by Total Spend
top_monetary = rfm.sort_values(by='Monetary', ascending=False).head(10)
plt.figure(figsize=(10,6))
sns.barplot(y=top_monetary.index.astype(str), x=top_monetary['Monetary'], color='green')
plt.title('Top 10 Customers by Total Spend', fontsize=16)
plt.ylabel('CustomerID')
plt.xlabel('Total Spend (£)')
plt.tight_layout()
plt.show()

#Correlation between RFM Metrics
plt.figure(figsize=(6,4))
sns.heatmap(rfm.corr(), annot=True, cmap="coolwarm")
plt.title('Correlation between RFM Metrics', fontsize=16)
plt.show()



# ADD RFM SCORING & CUSTOMER SEGMENTATION

# Step 1: Assign R, F, M scores (1–5) with robust binning
def assign_scores(series, n=5, reverse=False):
    try:
        labels = list(range(1, n+1))
        if reverse:
            labels = labels[::-1]
        return pd.qcut(series, q=n, labels=labels, duplicates='drop')
    except Exception:
        labels = list(range(1, n+1))
        if reverse:
            labels = labels[::-1]
        return pd.cut(series.rank(method='first'), bins=n, labels=labels)

rfm['R_Score'] = assign_scores(rfm['Recency'], n=5, reverse=True)
rfm['F_Score'] = assign_scores(rfm['Frequency'], n=5, reverse=False)
rfm['M_Score'] = assign_scores(rfm['Monetary'], n=5, reverse=False)

# Step 2: Create RFM Score
rfm['RFM_Score'] = rfm['R_Score'].astype(int) + rfm['F_Score'].astype(int) + rfm['M_Score'].astype(int)


# Step 3: Segment Customers (Simple)
# Customers are segmented based on their total RFM score:
# - VIP: RFM_Score >= 12 (top scores in all metrics)
# - Loyal: RFM_Score >= 9
# - Regular: RFM_Score >= 6
# - At Risk: RFM_Score < 6 (lowest scores)
def rfm_segment(score):
    if score >= 12:
        return 'VIP'
    elif score >= 8:
        return 'Loyal'
    elif score >= 5:
        return 'Regular'
    else:
        return 'At Risk'

rfm['Segment'] = rfm['RFM_Score'].apply(rfm_segment)


print(rfm.head(10))


# Step 4: Segment Distribution
plt.figure(figsize=(7,4))
sns.countplot(data=rfm, x='Segment', palette='Set2', order=['VIP','Loyal','Regular','At Risk'])
plt.title('Customer Segments by RFM Score', fontsize=16)
plt.xlabel('Segment')
plt.ylabel('Number of Customers')


#RFM Visualizations

# 1. RFM Heatmap (Recency vs Frequency)
rfm = rfm.reset_index()  # Ensure CustomerID is a column
plt.figure(figsize=(8,6))
rfm_pivot = rfm.pivot_table(index='R_Score', columns='F_Score', values='CustomerID', aggfunc='count')
sns.heatmap(rfm_pivot, annot=True, fmt='.0f', cmap='YlGnBu')
plt.title('Heatmap of Recency vs Frequency Scores')
plt.xlabel('Frequency Score')
plt.ylabel('Recency Score')

# 2. Boxplot by Segment (Monetary)
plt.figure(figsize=(8,4))
sns.boxplot(x='Segment', y='Monetary', data=rfm, order=['VIP','Loyal','Regular','At Risk'])
plt.yscale('log')
plt.title('Monetary Value by Segment (Log Scale)')

# 3. Pie Chart of Segment Proportions
plt.figure(figsize=(6,6))
rfm['Segment'].value_counts().plot.pie(autopct='%1.1f%%', startangle=90, colors=sns.color_palette('Set2'))
plt.title('Customer Segment Proportions')
plt.ylabel('')

plt.show()

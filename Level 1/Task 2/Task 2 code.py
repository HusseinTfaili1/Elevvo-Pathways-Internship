import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


train_df = pd.read_excel("train.xlsx")

# Fill missing age values with median and embarked with mode
train_df['Age'].fillna(train_df['Age'].median(), inplace=True)
train_df['Embarked'].fillna(train_df['Embarked'].mode()[0], inplace=True)

# Convert 3 values to categorical
for col in ['Sex', 'Embarked', 'Pclass']:
    train_df[col] = train_df[col].astype('category')

# Extracting titles from the passengers
train_df['Title'] = train_df['Name'].str.extract(' ([A-Za-z]+)\.', expand=False)
train_df['Title'] = train_df['Title'].replace(['Lady', 'Countess', 'Capt', 'Col', 'Don', 'Dr',
                                               'Major', 'Rev', 'Sir', 'Jonkheer', 'Dona'], 'Rare')
train_df['Title'] = train_df['Title'].replace({'Mlle': 'Miss', 'Ms': 'Miss', 'Mme': 'Mrs'})
train_df['Title'] = train_df['Title'].astype('category')

# Family size
train_df['FamilySize'] = train_df['SibSp'] + train_df['Parch'] + 1

# Create FamilyGroup column by binning FamilySize
def family_group(size):
    if size == 1:
        return 'Single'
    elif size <= 4:
        return 'Small'
    else:
        return 'Large'
train_df['FamilyGroup'] = train_df['FamilySize'].apply(family_group)

# HasCabin feature: 1 if there is a cabin, 0 if null
train_df['HasCabin'] = train_df['Cabin'].notnull().astype(int)
cols = list(train_df.columns)
if 'HasCabin' in cols and 'Cabin' in cols:
    cols.remove('Cabin')
    hascabin_idx = cols.index('HasCabin')
    cols.insert(hascabin_idx + 1, 'Cabin')
    train_df = train_df[cols]

# Add great british pound to Fare
train_df['Fare_display'] = train_df['Fare'].apply(lambda x: f"GBP {x:.2f}")

sns.set_style("whitegrid")
sns.set_context("talk")
palette = "viridis"

# Preview
print(train_df.head())
print(train_df.isnull().sum())

print("\n*** Summary Statistics (Numeric Columns) ***")
print(train_df.describe())

print("\n*** Summary Statistics (All Columns) ***")
print(train_df.describe(include='all'))


# Grouped Survival Rate Calculations

# Survival rate by Sex
surv_by_sex = train_df.groupby('Sex', observed=False)['Survived'].mean()
print("\nSurvival Rate by Sex:\n", surv_by_sex)

# Survival rate by Pclass
surv_by_class = train_df.groupby('Pclass', observed=False)['Survived'].mean()
print("\nSurvival Rate by Pclass:\n", surv_by_class)

# Survival rate by Sex & Pclass
surv_by_sex_class = train_df.groupby(['Sex', 'Pclass'], observed=False)['Survived'].mean()
print("\nSurvival Rate by Sex & Pclass:\n", surv_by_sex_class)

# Survival rate by Embarked
surv_by_port = train_df.groupby('Embarked', observed=False)['Survived'].mean()
print("\nSurvival Rate by Embarked Port:\n", surv_by_port)

# Survival rate by Title
surv_by_title = train_df.groupby('Title', observed=False)['Survived'].mean()
print("\nSurvival Rate by Title:\n", surv_by_title)

# Survival rate by FamilyGroup
surv_by_family = train_df.groupby('FamilyGroup', observed=False)['Survived'].mean()
print("\nSurvival Rate by Family Size Group:\n", surv_by_family)


# Visualizations: Bar Plots of Survival Rates and more

# Survival Rate by Gender
plt.figure(figsize=(8,4))
ax = sns.barplot(x='Sex', y='Survived', data=train_df, palette=palette, ci=None)
plt.title('Survival Rate by Gender', fontsize=16)
plt.xlabel('Sex', fontsize=12)
plt.ylabel('Survival Rate', fontsize=12)
for p in ax.patches:
    height = p.get_height()
    ax.annotate(f"{height:.2f}",
                xy=(p.get_x() + p.get_width() / 2., height),
                xytext=(0, height * 0.01),
                textcoords="offset points",
                ha='center', va='bottom', fontsize=10, color='black')
plt.xticks(fontsize=11)
plt.yticks(fontsize=11)
plt.tight_layout()


# Survival Rate by Class
plt.figure(figsize=(8,4))
ax = sns.barplot(x='Pclass', y='Survived', data=train_df, palette=palette, ci=None)
plt.title('Survival Rate by Class', fontsize=16)
plt.xlabel('Passenger Class', fontsize=12)
plt.ylabel('Survival Rate', fontsize=12)
for p in ax.patches:
    height = p.get_height()
    ax.annotate(f"{height:.2f}",
                xy=(p.get_x() + p.get_width() / 2., height),
                xytext=(0, height * 0.01),
                textcoords="offset points",
                ha='center', va='bottom', fontsize=10, color='black')
plt.xticks(fontsize=11)
plt.yticks(fontsize=11)
plt.tight_layout()


# Survival Rate by Port
plt.figure(figsize=(8,4))
ax = sns.barplot(x='Embarked', y='Survived', data=train_df, palette=palette, ci=None)
plt.title('Survival Rate by Port', fontsize=16)
plt.xlabel('Port of Embarkation', fontsize=12)
plt.ylabel('Survival Rate', fontsize=12)
for p in ax.patches:
    height = p.get_height()
    ax.annotate(f"{height:.2f}",
                xy=(p.get_x() + p.get_width() / 2., height),
                xytext=(0, height * 0.01),
                textcoords="offset points",
                ha='center', va='bottom', fontsize=10, color='black')
plt.xticks(fontsize=11)
plt.yticks(fontsize=11)
plt.tight_layout()



# Survival Rate by Family Size Group
plt.figure(figsize=(8,4))
ax = sns.barplot(x='FamilyGroup', y='Survived', data=train_df, order=['Single', 'Small', 'Large'], palette=palette, ci=None)
plt.title('Survival Rate by Family Size Group', fontsize=16)
plt.xlabel('Family Group', fontsize=12)
plt.ylabel('Survival Rate', fontsize=12)
for p in ax.patches:
    height = p.get_height()
    ax.annotate(f"{height:.2f}",
                xy=(p.get_x() + p.get_width() / 2., height),
                xytext=(0, height * 0.01),
                textcoords="offset points",
                ha='center', va='bottom', fontsize=10, color='black')
plt.xticks(fontsize=11)
plt.yticks(fontsize=11)
plt.tight_layout()



# Survival Rate by Title
plt.figure(figsize=(10,4))
ax = sns.barplot(x='Title', y='Survived', data=train_df, palette=palette, ci=None)
plt.title('Survival Rate by Title', fontsize=16)
plt.xlabel('Title', fontsize=12)
plt.ylabel('Survival Rate', fontsize=12)
plt.xticks(rotation=45, fontsize=11)
plt.yticks(fontsize=11)
for p in ax.patches:
    height = p.get_height()
    ax.annotate(f"{height:.2f}",
                xy=(p.get_x() + p.get_width() / 2., height),
                xytext=(0, height * 0.01),
                textcoords="offset points",
                ha='center', va='bottom', fontsize=10, color='black')
plt.tight_layout()


# Survival Rate by Gender and Class
plt.figure(figsize=(10,5))
ax = sns.barplot(x='Sex', y='Survived', hue='Pclass', data=train_df, palette=palette, ci=None)
plt.title('Survival Rate by Gender and Class', fontsize=16)
plt.xlabel('Sex', fontsize=12)
plt.ylabel('Survival Rate', fontsize=12)
plt.xticks(fontsize=11)
plt.yticks(fontsize=11)
for p in ax.patches:
    height = p.get_height()
    ax.annotate(f"{height:.2f}",
                xy=(p.get_x() + p.get_width() / 2., height),
                xytext=(0, height * 0.01),
                textcoords="offset points",
                ha='center', va='bottom', fontsize=10, color='black')
plt.legend(title='Pclass')
plt.tight_layout()


# Correlation heatmap for numeric features
plt.figure(figsize=(10,6))
numeric_cols = train_df.select_dtypes(include=[np.number])
sns.heatmap(numeric_cols.corr(), annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5, linecolor='white', cbar_kws={"shrink": .8})
plt.title('Correlation Heatmap (Numeric Features)')
plt.tight_layout()

plt.show() # calls the graphs at once rather than one by one. 
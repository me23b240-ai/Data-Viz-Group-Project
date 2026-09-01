# A Visual Study of E-Commerce Orders, Delivery and Customer Satisfaction

Data Visualization Design Project, Group 16

## Team

- Poras Vilas Wadhai (ME23B240)
- Vinayak Kumar (21F1006600)
- A Ayyakutti (21F2000827)
- Naman Shyamsukha (22F2000108)

## Live Deliverables

- **Interactive Dashboard:** https://data-viz-group-project-group16.streamlit.app/
- **Technical Report:** see `report/` folder in this repository

## Project Objective

Online marketplaces face a structural tension between growth and customer experience. Aggressively onboarding sellers and increasing order volume raises gross sales, but late deliveries, inconsistent seller quality, and poor reviews can drive customers away. Strict quality enforcement protects satisfaction but shrinks seller diversity and slows growth.

This project analyzes the complete order journey of a Brazilian e-commerce marketplace, from order placement and payment, through seller handling and freight, to final delivery and customer review, to answer:

- Which product categories, seller behaviours, regions, and delivery patterns predict a satisfied customer versus a dissatisfied one
- Where the marketplace should invest to sustain growth, and where it should intervene to protect the customer experience
- Whether high risk segments share a common root cause, or require different interventions depending on the entity

## Central Finding

Customer satisfaction is governed by a delivery promise threshold, not by delivery speed. Average review score stays largely stable while an order is early or only slightly late, then drops sharply once the order crosses its promised delivery date. This threshold effect held consistently across categories, sellers, and geography.

The deeper structural insight: root cause heterogeneity increases the further down the hierarchy you go. Category and geographic risk are almost entirely delivery driven, meaning a single logistics fix resolves most of it. Seller level risk is meaningfully more heterogeneous, a genuine three way split between delivery driven, intrinsic, and mixed risk sellers, and requires differentiated intervention rather than one blanket policy.

## Dataset

Olist style relational Brazilian e-commerce dataset, nine linked tables (orders, order items, customers, sellers, products, category translations, payments, reviews, geolocation), covering 99,441 orders from September 2016 to October 2018. A supplementary Marketing Funnel dataset was evaluated and deliberately excluded from the core analysis due to limited overlap with active sellers (see technical report, Section 2).

## Project Structure
Data-Viz-Group-Project/
├── data/
│   ├── raw/                  # Original Olist and Marketing Funnel CSVs
│   └── processed/            # Analytical tables produced by the notebooks
├── notebooks/                # Week 1 and Week 2 analysis notebooks
├── dashboard/
│   ├── app.py                # Streamlit dashboard source
│   └── style.py               # Dashboard design system (colors, fonts, components)
├── report/                   # Technical report (LaTeX source and compiled PDF)
├── .streamlit/
│   └── config.toml            # Dashboard theme configuration
├── requirements.txt
└── README.md

## Methodology Summary

**Week 1: Data Understanding, Cleaning, and Initial Insights**
Audited every table for grain, keys, missing values, duplicates, and timestamp validity. Built derived variables (delivery delay, low rating rate, late delivery flags, same state versus cross state) with documented formulas and limitations. Surfaced the delivery threshold effect as an early hypothesis.

**Week 2: Deep Comparative Analysis**
Tested whether the threshold effect and other early patterns were robust across categories, sellers, and geography. Introduced a root cause framework at every level: does a segment's poor rating persist even when delivery is on time, or is it explained mainly by lateness. Built the Marketplace Experience Risk Matrix, classifying every segment by business importance versus customer experience risk.

**Week 3: Dashboard, Reporting, and Presentation**
Converted validated findings into an interactive Streamlit dashboard, a technical report, and a presentation built around a decision oriented narrative.

## Running the Dashboard Locally

```bash
git clone https://github.com/me23b240-ai/Data-Viz-Group-Project.git
cd Data-Viz-Group-Project
pip install -r requirements.txt
streamlit run dashboard/app.py
```

## Reproducing the Analysis

All notebooks in `notebooks/` are designed to run top to bottom in Google Colab. Upload the raw CSVs from `data/raw/` (or the original Kaggle dataset) and run the notebooks in order:

1. Week 1 data foundation and exploratory analysis
2. Week 2 deep dive: delivery, category, seller, and geographic root cause analysis

Each notebook exports its analytical tables to `data/processed/`, which the dashboard reads directly.

## Key Deliverables Checklist

- [x] Interactive dashboard (Streamlit, deployed)
- [x] Technical report (LaTeX/PDF)
- [x] Reproducible notebooks and processed data tables
- [x] Final presentation

## Data Source

Olist and Andre Sionek, "Brazilian E-Commerce Public Dataset by Olist," Kaggle.
Available: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

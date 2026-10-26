---
title: "Automated Weekly Business Intelligence Report"
excerpt: "Built a Monday morning report automation that pulls KPIs from Stripe, Google Analytics, and HubSpot — then uses AI to write an executive summary. Zero human effort required."
date: "2026-02-28"
category: "reporting"
tools: ["n8n", "Stripe API", "Google Analytics", "HubSpot", "GPT-4o", "Gmail", "Google Slides"]
results: "Saves 4 hrs every Monday | Executive team gets reports automatically at 8AM"
featured: false
published: true
---

## The Problem

A SaaS startup's leadership team spent **4 hours every Monday morning** manually pulling numbers from Stripe, Google Analytics, and HubSpot — copying them into a Google Slides deck and writing a summary. It was the same repetitive work, every single week.

## The Automation

I built an **n8n workflow** that runs automatically every Monday at 8:00 AM and delivers a complete business intelligence report to the entire leadership team.

### What Gets Pulled Automatically

- **Stripe** — Weekly revenue, new subscriptions, churn, MRR
- **Google Analytics** — Sessions, new users, top pages, conversion rate
- **HubSpot** — New leads, deals closed, pipeline value, sales activity

### What AI Does With the Data

All data is sent to **GPT-4o** with a structured prompt that:
1. Identifies the biggest wins and concerns of the week
2. Compares current week vs previous week (% change)
3. Writes an executive-level summary in plain English — no jargon

### How It's Delivered

The final report is:
- Formatted into a **Google Slides template** automatically
- Emailed to the leadership team via **Gmail** with a direct link
- Also posted in a **Slack channel** with the AI summary

## Results

> ⏱️ **Time saved:** **4 hours every Monday** — that's 16+ hours/month  
> 📊 **Consistency:** Reports are always ready by 8AM, without fail  
> 🤖 **AI summaries:** Leadership team rated the AI summaries as "better than what we wrote manually"  
> 📉 **Human error:** Eliminated — no more copy-paste mistakes in KPI slides

## Tools Used

- **n8n** — Workflow automation and scheduling
- **Stripe API** — Revenue and subscription data
- **Google Analytics API** — Traffic and conversion data
- **HubSpot API** — Sales pipeline data
- **GPT-4o** — Executive summary generation
- **Google Slides API** — Report generation
- **Gmail** — Report delivery
- **Slack** — Team notification

---
title: "Automated Review Collection & AI-Powered Testimonial Social Posting System"
excerpt: "Built a fully automated workflow that collects product reviews from RSS feeds, filters positive high-rating reviews using AI, generates branded testimonial creatives, and publishes them to social media automatically."
date: "2026-04-01"
category: "automation"
tools: ["n8n", "Gemini", "RSS Feed", "Apify API", "HTML", "CSS", "Facebook API"]
results: "Automated review monitoring | AI-based sentiment filtering | Dynamic testimonial generation | Social media posting with proof links"
screenshots:
   workflow:
   - 1-part.png
   - 2-part.png
   - 3-part.png
   - 4-part.png
   output:
   - 1-output.png
   - 2-output.png
   - 3-output.png
featured: true
published: true
---

## What Was the Problem?

Manually collecting product reviews and turning them into social media testimonials is time-consuming and inconsistent.

For businesses managing multiple products or plugins, this becomes even harder when:
- Reviews need to be monitored continuously
- Positive and negative reviews need different handling
- Low-rated reviews should be escalated to the team immediately
- Social proof content needs to be created fast
- Testimonial images need to be branded and visually consistent
- Product links should be shared carefully to avoid reducing post reach

They needed a system that could:
- Automatically monitor incoming product reviews
- Detect whether a review is positive or negative using AI
- Filter only high-quality reviews for social posting
- Route reviews by product automatically
- Generate post copy and branded testimonial creatives
- Publish the content to social media with proof links in comments
- Alert the internal team when bad or low-rated reviews appear

---

## What I Built

Using **n8n**, I built a fully automated review collection and testimonial posting system that tracks new reviews, filters them with AI, generates branded testimonial assets, and publishes them to social media automatically.

### Workflow Overview

1. **Scheduled Review Monitoring**
   - The workflow runs automatically every hour
   - It checks product **RSS review feeds** to detect whether any new review has been posted within the last hour
   - If no new review is found, the workflow stops
   - If a new review is found, it moves to the next step

2. **AI Sentiment Check**
   - An **AI agent** analyzes the incoming review
   - It determines whether the review is **positive** or **negative**
   - If the review is negative, the system immediately sends an alert email to the internal team
   - If the review is positive, the workflow continues

3. **Star Rating Validation**
   - A second AI/logic step checks the review rating
   - If the review is **greater than 4 stars**, it qualifies for testimonial creation
   - If the review is **4 stars or below**, the system sends an email alert to the team instead of posting it publicly

4. **Product-Based Routing**
   - Since the workflow handles multiple products/plugins, a **switch router** detects which product the review belongs to
   - The review is then sent to the correct product-specific branch

5. **AI Social Post Writing**
   - Inside the selected product branch, an AI agent writes a social media caption
   - The post is based on:
     - What the customer said in the review
     - Product value/highlights
     - A natural promotional tone suitable for testimonial content

6. **Reviewer Profile Scraping**
   - The workflow scrapes the reviewer profile to collect profile data
   - This includes checking whether a usable profile image is available
   - The goal is to make the testimonial more authentic by using the reviewer’s image when possible

7. **Human Image Detection**
   - Another AI/image analysis step checks whether the profile image contains a real human face
   - If the image is a valid human profile image, it is approved for the testimonial design
   - If not, the workflow skips using the profile image in the creative

8. **Dynamic Testimonial Template Generation**
   - A testimonial template built with **HTML + CSS** is used
   - The template dynamically inserts:
     - Reviewer name
     - Reviewer profile image (if valid)
     - Review text
     - Star rating
     - Product logo
     - Product branding elements
   - This ensures visually consistent testimonial posts across all products

9. **HTML to Image Conversion**
   - The generated testimonial template is converted into a **JPG image**
   - This final image is prepared for use as the social media post creative

10. **Automated Social Media Publishing**
   - The final testimonial image and AI-generated caption are published automatically to **Facebook**
   - The post also includes product value messaging and relevant hashtags for better engagement

11. **Comment-Based Proof & Product Links**
   - After publishing the post, the workflow automatically adds a comment containing:
     - The original review link
     - The product link
   - This is done intentionally because direct links inside the post can reduce reach
   - Keeping links in the comment helps preserve engagement while still providing proof and conversion paths

---

## Key Technical Details

- Built using **n8n modular workflow architecture**
- Used **RSS feed monitoring** to detect new reviews automatically
- Implemented **AI-based sentiment analysis** for review qualification
- Added **rating-based filtering logic** to separate top reviews from low-rated ones
- Used **switch routing** for handling multiple products in a single workflow
- Automated **AI caption generation** for social media posting
- Integrated **profile scraping and human image detection** to improve testimonial authenticity
- Built reusable **HTML/CSS testimonial templates** with dynamic content injection
- Converted testimonial layouts into **JPG creatives** for platform-friendly publishing
- Added **Facebook posting + automated comment publishing** as the final delivery step
- Designed alert logic to notify the internal team instantly about negative or lower-rated reviews

---

## Results

> 🚀 **100% automated review-to-social workflow** — no manual testimonial creation needed  
> 🧠 **AI-powered review filtering** — only positive, high-quality reviews get published  
> 🎨 **Dynamic testimonial generation** — branded creatives created automatically  
> ⏱️ **Hourly review monitoring** — new feedback is processed in near real time  
> 📣 **Automated Facebook posting** — caption, creative, and follow-up comments handled end-to-end  
> 🔔 **Instant team alerts** — bad or low-rated reviews are escalated immediately  

---

## Tools Used

- **n8n** — Workflow automation & orchestration  
- **Gemini API** — Sentiment analysis, content generation, decision logic  
- **RSS Feed** — Product review monitoring  
- **Apify API** — Reviewer profile scraping / data collection  
- **HTML & CSS** — Testimonial template design  
- **Image Processing / HTML-to-Image** — JPG testimonial generation  
- **Facebook API** — Social media publishing and comment posting  
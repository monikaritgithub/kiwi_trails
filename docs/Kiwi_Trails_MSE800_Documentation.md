# Kiwi Trails (Ara Aotearoa)
## Eco Tourism Reservation and Cultural Guided Tour Platform
### MSE800 Software Engineering Project Report

| Field | Details |
| --- | --- |
| Course Code | MSE800 Software Engineering Practice |
| Course Title | Master of Software Engineering / Postgraduate Project |
| Assessment | Assessment 2 Project Design and System Implementation |
| Educational Institution | Yoobee Colleges of Creative Innovation, School of Technology |
| Campus Location | Auckland, New Zealand |
| Submission Date | 26 October 2026 |
| Technology Stack | Django 6, Django REST Framework 3, SQLite, HTML5, CSS3, ES6 JavaScript |
| Testing Framework | Django Test Suite, 342 Passing Tests, Ruff Linter |
| Cultural Framework | Te Tiriti o Waitangi Integration (Partnership, Participation, Protection) |


# Abstract

This project documentation records the architectural specification, design engineering, and technical delivery of the Kiwi Trails (Ara Aotearoa) platform. Kiwi Trails is a culturally responsive eco tourism web platform engineered to connect international and domestic travelers with authentic, guided New Zealand tour experiences. Guided by the core tenets of Te Tiriti o Waitangi, the platform embeds Kaitiakitanga (environmental guardianship), Manaakitanga (hospitality and cultural care), and Whanaungatanga (relationship building) directly into software design.

Constructed using Python Django and Django REST Framework for the application server, a robust SQLite relational database, and a responsive frontend interface leveraging vanilla HTML5, modern CSS custom properties, and ES6 modules, the platform enables authenticated customer reservations, atomic seat capacity management, promotional coupon redemptions, automated PDF invoice generation, calendar synchronization, and verified post tour traveler reviews. Operations management is facilitated through an administrator portal providing real time departure attendance rosters, customer status transitions, and analytical dashboard metrics. The project was executed through an Agile Scrum methodology over four sequential sprints, achieving comprehensive test coverage verified by 342 automated unit and integration tests and complete code quality compliance with Ruff.


# 1. Executive Summary

The Kiwi Trails (Ara Aotearoa) platform emerged from a simulated software engineering initiative designed to satisfy the growing demand for authentic, sustainable, and culturally respectful tourism in New Zealand. Conventional commercial travel portals often disconnect travelers from genuine cultural narratives, commodify indigenous knowledge without tribal collaboration, and lack automated mechanisms to manage fragile site visitor capacities. Kiwi Trails addresses these deficiencies through a specialized, full stack web platform that unites travelers, Kaitiaki guides, and operations administrators.

The application provides distinct user experiences tailored by role. Guests and authenticated customers can discover curated tours across five distinct outdoor categories, view real time scheduled departures, request pricing quotes with promotional discounts, lock departure seats atomically to prevent overbooking, receive instant digital invoices, download calendar files, and submit verified reviews following tour completion. Platform administrators maintain catalog governance, schedule seasonal departures, oversee attendance tracking on the day of departure, and monitor operational performance through visual metrics.

A central pillar of the Kiwi Trails engineering philosophy is the structural alignment with the principles of Te Tiriti o Waitangi. Partnership (Patuitanga) is established through authentic guide representation and tribal narrative recognition. Participation (Whai Wahitanga) is fostered via transparent pricing quotes, verified reviews, and interactive booking management. Protection (Tiakitanga) is enforced through ethical data handling adhering to Maori data sovereignty concepts (Mana Raraunga) and atomic capacity locking that prevents over tourism on delicate natural ecosystems. This documentation outlines the entire software engineering lifecycle from kickoff to deployment.


# 2. Team Formation and Roles

The development of Kiwi Trails was accomplished by a collaborative agile engineering team composed of three primary technical roles, ensuring clear specialization, ownership, and balanced workload distribution across the full software delivery lifecycle.


| Member Role | Primary Focus | Key Responsibilities |
| --- | --- | --- |
| Member 1 Frontend Developer | Client Presentation & UX Architecture | Engineered responsive UI using HTML5, modern CSS custom properties, and ES6 JavaScript. Developed customer tour catalog, discovery filters, interactive calendar views, booking quote modal, authentication screens, and administrator operations dashboards. |
| Member 2 Backend Developer | Tour Catalog, Departures & Reviews | Constructed Django domain models for Categories, Guides, Tours, Tour Images, Tour FAQs, Departures, Coupons, and Verified Customer Reviews. Implemented public discovery APIs, administrative tour management, rating recalculation, and seed commands. |
| Member 3 Backend Developer | Bookings Engine, Operations & Admin API | Built atomic booking reservation workflows, departure capacity locking, quote calculations, customer cancellation rules, ReportLab PDF confirmation invoice generation, ICS calendar exports, attendance roster management, and administrative dashboard metrics. |


## 3.1 Project Kickoff Overview

The project kickoff established a unified vision for Kiwi Trails, framing the platform not merely as a commercial transaction engine, but as an educational, culturally supportive bridge for exploring Aotearoa. Key goals included:


* Engineering an accessible, responsive web application connecting travelers with certified Kaitiaki guides.
* Providing robust RESTful API endpoints following standard HTTP methods, clean resource naming, and status codes.
* Guaranteeing atomic transactional integrity during booking reservation and capacity decrement to avoid double booking.
* Embedding cultural respect, ecological responsibility, and educational depth across all tour details and interactions.

## 3.2 Project Planning and Team Alignment

Development practices were standardized at kickoff to ensure rapid, high quality delivery:
1. Agile Methodology: Sprints were structured with explicit user stories, task estimations, and backlog prioritization.
2. Version Control Strategy: GitHub served as the centralized code repository, utilizing feature branch workflows, pull request code reviews, and squash merges into main.
3. Automated Quality Verification: Continuous local testing via Django test suite ensuring zero regressions across all 342 test cases.
4. Linting and Clean Code: Ruff was enforced across all Python files to maintain strict PEP8 adherence and zero unused imports.


## 3.3 Te Tiriti o Waitangi Integration

The three foundational principles of Te Tiriti o Waitangi guided every tier of system architecture:
1. Partnership (Patuitanga): Kiwi Trails partners with certified local Kaitiaki guides who directly own and represent the narratives of their ancestral lands. Platform policies mandate that indigenous knowledge and tour descriptions remain authentic and respectful.
2. Participation (Whai Wahitanga): Travelers of all backgrounds are encouraged to participate in culturally grounded eco tourism. The user interface provides clear educational FAQs regarding cultural tikanga (customs), while post tour review mechanisms empower transparent, respectful traveler participation.
3. Protection (Tiakitanga): The system actively safeguards wahi tapu (sacred cultural sites) and fragile wilderness areas by implementing strict capacity enforcement on scheduled departures. Furthermore, traveler personal details and booking records are protected through encrypted storage and strict access controls, respecting Maori data sovereignty principles (Mana Raraunga).


## 3.4 Guidance and Quality Assurance

The project benefited from structured academic review and simulated cultural advisory sessions. Iterative feedback provided during sprint reviews assisted in refining functional priorities, perfecting database relationships, reinforcing API security boundaries, and confirming the ethical alignment of cultural content.


## 4.1 Background Review and Literature Review

Aotearoa New Zealand possesses world renowned natural landscapes, spanning glacial mountains, geothermal valleys, ancient native forests, and coastal habitats. Alongside this ecological wealth is the vibrant living culture of the Maori people. In traditional society, tribal collectives were organized around iwi (nations or large tribes), hapu (sub tribes or clans), and whanau (extended families), with ancestral connections deeply bound to the land (whenua).

Academic literature highlights that modern tourism often risks commercializing indigenous culture without equitable tribal participation (Keegan and Wotherspoon, 2019). Furthermore, contemporary digital initiatives must recognize Maori data sovereignty (Mana Raraunga, 2023), asserting that indigenous communities retain authority over the representation of their stories, images, and cultural heritage (Brown et al., 2024; Ruckstuhl, 2023). Kiwi Trails integrates these scholarly insights by providing direct guide profiles, authentic local photography, transparent pricing structures, and strict environmental capacity thresholds that prevent over tourism.


## 4.2 Simulated Stakeholder Interview Questions and Findings

To gather realistic system requirements, 28 simulated stakeholder interviews were conducted spanning domestic travelers, international eco tourists, certified Kaitiaki guides, and platform operations administrators. Below are the key findings:


| No. | Question | Stakeholder Insight & Platform Decision |
| --- | --- | --- |
| 1 | What makes an eco tour authentic in New Zealand? | Authenticity requires local Kaitiaki guides who share real oral histories and environmental context, not scripted corporate spiels. Decision: Created dedicated Guide model with certifications. |
| 2 | How should cultural heritage sites be protected from overcrowding? | Tours must enforce strict participant limits to protect fragile trails and sacred wahi tapu. Decision: Enforced atomic database capacity limits on departures. |
| 3 | What information do travelers require before booking? | Clear itinerary details, physical difficulty ratings, duration, pricing in NZD, dietary accommodations, and packing advice. Decision: Implemented Tour FAQs and structured tour specifications. |
| 4 | How should pricing quotes handle group discounts or coupons? | Travelers want transparent quotes showing base price, traveler multipliers, and validated promotional discounts before confirming. Decision: Created GET /api/v1/bookings/quote/ endpoint. |
| 5 | What happens if a customer needs to cancel a reservation? | Customers require flexible self service cancellation up to 48 hours prior to departure, returning capacity to the schedule. Decision: Built PATCH /api/v1/bookings/{id}/cancel/ endpoint. |
| 6 | How do guides verify customer arrival on the day of departure? | Guides need a simple digital manifest to view traveler counts, special requirements, and mark attendance as present or absent. Decision: Built GET and PUT attendance endpoints. |
| 7 | How can travelers trust post tour reviews? | Reviews must only be allowed from verified customers who actually completed the tour. Decision: Review creation restricted to users with completed bookings. |
| 8 | What format should booking confirmations take? | Travelers expect immediate downloadable PDF invoices and calendar invite files for mobile trip planning. Decision: Automated ReportLab PDF and .ics calendar generation. |
| 9 | What role based controls are required for administrators? | Admins must manage tours, schedule departures, review pending reservations, mark attendance, and inspect revenue statistics. Decision: Role based access control with is_staff permissions. |
| 10 | How should the platform handle offline or mobile network conditions? | Frontend must be lightweight, fast loading, and responsive without heavy external frameworks. Decision: Built responsive vanilla HTML5, CSS3, and ES6 client architecture. |


## 4.4 Functional Requirements by Domain Module

The platform is structured into five core modules:

* Accounts Module: Registration, authentication, customer and admin roles.
* Catalog Module: Tours, categories, guide profiles, images, and FAQs.
* Departures Module: Scheduled tour dates, capacities, and calendar availability.
* Coupons Module: Promotional discount codes and validation rules.
* Bookings Module: Quotes, atomic reservations, invoices, calendar exports, attendance, and reviews.

## 4.11 Access Control Matrix


| Platform Feature / Action | Guest (Public) | Customer | Administrator |
| --- | --- | --- | --- |
| Browse Tour Catalog & Itineraries | Yes | Yes | Yes |
| View Tour FAQs & Guide Profiles | Yes | Yes | Yes |
| Browse Scheduled Departures & Open Seats | Yes | Yes | Yes |
| Calculate Booking Price Quotes | Yes | Yes | Yes |
| Customer Account Registration & Login | Yes | Yes | Yes |
| Create New Tour Booking Reservation | No | Yes | Yes |
| View Personal Booking History & Status | No | Yes | Yes |
| Cancel Personal Pending/Approved Booking | No | Yes | Yes |
| Download PDF Confirmation Invoice | No | Yes | Yes |
| Download iCalendar (.ics) Event File | No | Yes | Yes |
| Submit Verified Tour Review & Rating | No | Yes (Completed only) | Yes |
| Create & Edit Tours, Categories, Guides | No | No | Yes |
| Schedule Departures & Set Capacity | No | No | Yes |
| Approve or Reject Pending Bookings | No | No | Yes |
| View Departure Attendance Roster | No | No | Yes |
| Mark Customer Attendance (Present/Absent) | No | No | Yes |
| Manage Promotional Coupons | No | No | Yes |
| View Operations Dashboard Metrics | No | No | Yes |

* Performance: API responses complete in under 200 milliseconds under standard load. Frontend assets load in under 1 second.
* Security: Passwords hashed using PBKDF2 SHA256. CSRF tokens enforced on forms. Cross Origin Resource Sharing (CORS) configured.
* Reliability and Availability: Target availability of 99.9% uptime. Database transactions isolated using atomic blocks.
* Usability and Accessibility: Mobile first, fully responsive layout adhering to WCAG 2.1 AA contrast standards.
* Maintainability: Decoupled service layer architecture separating business logic from HTTP controller views.
* Portability: Runs uniformly on Windows, macOS, and Linux operating systems with SQLite relational storage.
* Compatibility: Cross browser support verified across Chrome, Firefox, Safari, and Edge.
* Monitoring and Audit Logging: Structured application logs recording booking creations, status updates, and attendance marks.

## 4.24 User Stories


| ID | As a... | I want to... | So that... |
| --- | --- | --- | --- |
| US01 | Guest | Browse available eco tours by category and region | I can discover New Zealand experiences aligned with my interests. |
| US02 | Guest | Read detailed tour itineraries, cultural FAQs, and guide profiles | I understand what to expect and respect cultural guidelines. |
| US03 | Guest | View upcoming departure dates and real time seat availability | I can plan my travel itinerary accurately. |
| US04 | Guest | Calculate an instant booking quote with coupon discount | I can review pricing before committing to registration. |
| US05 | User | Register for an account and log in securely | I can save my bookings and manage personal travel details. |
| US06 | Customer | Book a departure for multiple travelers with special requirements | My seats are secured and dietary or pickup needs are recorded. |
| US07 | Customer | Receive immediate booking confirmation and view reservation status | I have peace of mind regarding my travel arrangements. |
| US08 | Customer | Download an official PDF invoice for my approved reservation | I possess documentation for personal accounting and travel receipts. |
| US09 | Customer | Download an iCalendar (.ics) file for my confirmed tour | The tour details and schedule integrate directly into my digital calendar. |
| US10 | Customer | Cancel my booking if my travel plans change unexpectedly | I can release seats back to the community and update my schedule. |
| US11 | Customer | Submit a 1 to 5 star review and feedback after completing a tour | I can share my experience and assist future travelers. |
| US12 | Admin | Create, edit, and archive tour packages and upload gallery media | The catalog remains fresh, accurate, and appealing. |
| US13 | Admin | Schedule new tour departures with assigned Kaitiaki guides | Capacity is established for upcoming seasonal periods. |
| US14 | Admin | Review pending customer bookings and approve or reject them | Reservations are formally confirmed according to operational capacity. |
| US15 | Admin | Inspect departure manifests and passenger lists | Guides know exactly who will be attending each departure. |
| US16 | Admin | Mark passenger attendance as present or absent on the day of departure | Operational records reflect actual traveler participation. |
| US17 | Admin | Create and manage promotional discount coupons with date boundaries | Marketing campaigns can stimulate bookings during off peak seasons. |
| US18 | Admin | View an analytical operations dashboard with summary statistics | I can monitor revenue, capacity utilization, and booking trends. |


## 5.3 Cultural and Ethical Mapping to Te Tiriti o Waitangi


| Te Tiriti Principle | Kiwi Trails Software Implementation |
| --- | --- |
| Partnership (Patuitanga) | Certified Kaitiaki guides are recognized as core entities with profiles and dedicated assignments. Local Iwi consultation informs authentic descriptions and environmental guidelines. |
| Participation (Whai Wahitanga) | Open access to educational FAQs, transparent price quoting, inclusive customer booking options, and verified traveler review systems giving every participant a voice. |
| Protection (Tiakitanga) | Strict atomic capacity locking prevents ecological strain on sacred sites. Customer identity and payment records are safeguarded adhering to Maori data sovereignty (Mana Raraunga). |


## 5.4 MoSCoW Prioritisation Matrix


| Priority Category | Feature Description |
| --- | --- |
| Must Have | 1. User registration, authentication, and role authorization. 2. Curated tour catalog with category taxonomy and guide profiles. 3. Scheduled departures with real time capacity tracking. 4. Price quote calculator with coupon validation. 5. Atomic booking creation and capacity locking. 6. Administrative booking approval and rejection. 7. PDF invoice generation and ICS calendar export. 8. Departure attendance manifest and attendance marking. |
| Should Have | 1. Verified customer review submission and rating recalculation. 2. Administrative operations dashboard with revenue metrics. 3. Responsive mobile first design system using CSS custom properties. 4. Customer self service booking cancellation with seat release. |
| Could Have | 1. Advanced search filtering by physical difficulty and duration. 2. Email dispatch integration for automated booking notices. 3. One click desktop launchers for frontend and backend servers. |
| Won't Have (Future) | 1. Native iOS and Android mobile app variants. 2. Direct real time credit card payment gateway integration. 3. Real time chat between guides and travelers. |


## 6.1 Database Schema Overview (11 Relational Entities)

The Kiwi Trails relational schema is composed of 11 distinct database models designed to ensure high normalization, referential integrity, and efficient querying across tour discovery, scheduling, and reservation lifecycles:


| Entity Model | Database Table | Key Attributes | Relational Associations |
| --- | --- | --- | --- |
| User | accounts_user | id, email, password, full_name, is_staff, is_active, created_at | Parent of Bookings, Attendance marks, and Reviews. |
| Category | catalog_category | id, name, slug, description, icon | Parent of Tours (One to Many). |
| Guide | catalog_guide | id, name, bio, photo, certification, is_active | Parent of Tours and Departures (One to Many). |
| Tour | catalog_tour | id, title, slug, summary, price, duration_days, difficulty, status | Belongs to Category and Guide; Parent of Images, FAQs, Departures, Reviews. |
| TourImage | catalog_tourimage | id, tour_id, image, caption, is_cover, display_order | Belongs to Tour (Many to One). |
| TourFaq | catalog_tourfaq | id, tour_id, question, answer, display_order | Belongs to Tour (Many to One). |
| Departure | departures_departure | id, tour_id, guide_id, departure_date, capacity, available_seats, status | Belongs to Tour and Guide; Parent of Bookings (One to Many). |
| Coupon | coupons_coupon | id, code, discount_type, discount_value, min_spend, valid_until, is_active | Associated with Bookings during quote and reservation. |
| Booking | bookings_booking | id, booking_reference, user_id, departure_id, num_travelers, total_price, status | Belongs to User and Departure; Parent of Attendance. |
| Attendance | bookings_attendance | id, booking_id, status (present/absent), marked_by_id, marked_at | One to One with Booking; references User (guide/admin). |
| Review | catalog_review | id, tour_id, user_id, booking_id, rating (1-5), comment, is_verified | Belongs to Tour, User, and Booking (One to One per booking). |


## 6.5 Project Directory Structure

```
kiwi_trails/
├── apps/
│   ├── accounts/     # User authentication, profiles, role permissions
│   ├── catalog/      # Tours, Categories, Guides, Images, FAQs, Reviews
│   ├── departures/   # Scheduled departures, capacity limits, calendar
│   ├── coupons/      # Promotional discount codes and validation rules
│   └── bookings/     # Quotes, reservations, invoices, calendar, attendance, dashboard
├── config/           # Django settings, root URLs, WSGI/ASGI handlers
├── diagrams/         # DrawIO system architecture and UML diagrams
├── docs/             # Project documentation and build scripts
├── frontend/         # Static HTML5 templates, CSS design system, ES6 JavaScript
├── media/            # Seed photography and uploaded tour assets
├── run.bat           # Master Windows batch development launcher
├── run.ps1           # Master PowerShell development launcher
├── serve_frontend.py # Dedicated static frontend development server
├── start_backend.bat # Dedicated Django API launcher (Port 8000)
├── start_frontend.bat# Dedicated frontend server launcher (Port 5500)
└── manage.py         # Django project management CLI
```


# 7. User Flow Mapping Overview


| User Flow Stage | Operational Lifecycle Description |
| --- | --- |
| 7.1 Visit Website & Cultural Onboarding | Traveler arrives at the landing page, reads Kaitiakitanga principles, and explores featured New Zealand eco tours. |
| 7.2 Account Registration & Authentication | Customer signs up with email and password, receiving immediate token session authentication. |
| 7.3 Exploring Tour Catalog & Itineraries | Customer filters tours by category (Hiking, Water, Culture), inspecting itineraries, FAQs, and guide backgrounds. |
| 7.4 Selecting Departure & Calculating Quotes | Customer chooses a scheduled departure date, inputs traveler counts, enters an optional coupon, and receives an instant price quote. |
| 7.5 Submitting Booking Reservation | Customer confirms special pickup details and submits booking. The backend executes an atomic transaction, reserving seats and issuing a unique booking reference. |
| 7.6 Admin Review & Approval | Operations administrator reviews the pending reservation and approves it, confirming official departure inclusion. |
| 7.7 Confirmation Invoice & Calendar Download | Customer downloads an official branded PDF invoice and adds the .ics calendar file to their digital schedule. |
| 7.8 Departure Day Attendance Marking | On tour day, the Kaitiaki guide opens the departure manifest and marks traveler attendance as present or absent. |
| 7.9 Verified Review Submission | Following tour completion, the customer submits a verified rating and written review, updating the tour average score. |


# 8. Project Timeline and Planning


| Milestone | Target Deliverable | Prerequisite Dependency |
| --- | --- | --- |
| M1: Inception & Architecture | Database ER model, project repository, and base setup | Project Kickoff |
| M2: Catalog & Departures | Public tour discovery API, guide profiles, and departure scheduling | M1 Inception |
| M3: Booking Engine & Operations | Atomic reservation API, PDF invoice generation, and calendar export | M2 Catalog |
| M4: Operations & Attendance | Departure attendance rosters, admin dashboard metrics, verified reviews | M3 Booking Engine |
| M5: Frontend Integration & QA | Complete UI screens, end to end testing, documentation, and launchers | M4 Operations |


# 9. Agile Development Sprints

Agile Scrum practices governed team collaboration throughout the project lifecycle.


# 10. Cost Estimation


| Engineering Activity | Estimated Hours | Hourly Rate (NZD) | Total Cost (NZD) |
| --- | --- | --- | --- |
| Project Inception, Requirements & Treaty Planning | 16 hrs | $30.00 | $480.00 |
| Backend Architecture, Database & Catalog API (Member 2) | 36 hrs | $30.00 | $1,080.00 |
| Backend Booking Engine, Invoices & Attendance (Member 3) | 38 hrs | $30.00 | $1,140.00 |
| Frontend UI, Design System & Client Integration (Member 1) | 32 hrs | $30.00 | $960.00 |
| Automated Testing, Quality Assurance & Linting | 12 hrs | $30.00 | $360.00 |
| System Documentation, Diagrams & Launchers | 14 hrs | $30.00 | $420.00 |
| Total Project Investment | 148 hrs | - | $4,440.00 |


# 11. Testing and Quality Assurance

Quality assurance was embedded into every phase of development, achieving 342 passing tests and zero linting errors.


# 12. Deployment Strategy

The deployment strategy supports local development launchers and cloud production hosting.


# 13. Challenges and Risk Mitigation


| Identified Challenge | Risk Impact | Mitigation Strategy Implemented |
| --- | --- | --- |
| Atomic Seat Concurrency | High (Double Booking) | Implemented database level transaction.atomic() blocks ensuring seats are locked and verified before booking confirmation. |
| Cultural Authenticity & Sensitivity | High (Misrepresentation) | Embedded Kaitiakitanga principles and partnered with authentic Kaitiaki guide profiles and validated cultural FAQs. |
| Frontend Static Path Resolution | Medium (Asset 404s) | Authored dedicated serve_frontend.py server resolving both root and /frontend/ asset paths seamlessly. |
| Tight 3-Member Agile Delivery | Medium (Scope Creep) | Applied strict MoSCoW prioritization, limiting non core features and completing 100% of Must Have requirements. |


# 14. Cultural Integration Considerations

Kiwi Trails honors indigenous values and ecological responsibility across all software tiers.


# 15. Reflection and Lessons Learned

The project provided valuable technical, architectural, and ethical lessons.


# 16. Conclusion

Kiwi Trails successfully fulfills all requirements of MSE800 Assessment 2.

* 17.1 Whenua Environmental Impact Tracking: Real time carbon footprint calculation and trail restoration donation options.
* 17.2 Commercial Payment Gateway Integration: Stripe and Windcave credit card processing with automated refund handling.
* 17.3 Full Te Reo Maori Bilingual Interface: Complete language toggle with audio pronunciation for indigenous terms.
* 17.4 Offline Progressive Web App (PWA): Downloadable trail maps and emergency GPS coordinates for remote wilderness areas.
* 17.5 Iwi Trust Board Partnership Portal: Direct revenue sharing dashboards and cultural event sponsorship management.
* [1] Brown, P. T., et al. (2024). Maori algorithmic sovereignty: Idea, principles, and use. Data Science Journal, 23, Article 15.
* [2] Keegan, T. T., & Wotherspoon, T. (2019). Indigenous tourism and cultural integrity in Aotearoa New Zealand. Journal of Sustainable Tourism, 27(4), 512-528.
* [3] Kukutai, T., et al. (2020). Maori data sovereignty: Principles and practices. ANU Press, Canberra.
* [4] Lilley, S., et al. (2024). Maori data sovereignty: Contributions to data cultures in the government sector in New Zealand. Information, Communication & Society.
* [5] Mana Raraunga Maori Data Sovereignty Network. (2023). Principles of Maori Data Sovereignty. Te Mana Raraunga.
* [6] Ruckstuhl, K. (2023). Data as taonga: Aotearoa New Zealand, Maori data sovereignty and implications for protection of treasures. NYU Journal of Intellectual Property & Entertainment Law.
* [7] Te Ara - The Encyclopedia of New Zealand. (n.d.). Eco-tourism and outdoor recreation in New Zealand. https://teara.govt.nz
* [8] Tourism New Zealand. (2024). Tiaki Promise: Caring for New Zealand. https://www.tiakinewzealand.com
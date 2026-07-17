# School Management Software — ERPNext v15 Gap Analysis & Implementation Roadmap

> **App:** `school_management_software`  
> **Target Platform:** ERPNext v15 ↔ Frappe Framework v15  
> **Customization Approach:** 100% custom app — no core ERPNext/Frappe files modified  
> **Version:** 1.0.0  
> **Date:** July 17, 2026

---

## 1. Executive Summary

The **School Management Software** (`school_management_software`) is a Frappe/ERPNext-based custom app that extends the ERPNext **Education** module with 100+ custom DocTypes, 33 Server Scripts, 48 Client Scripts, and 12 custom Workspaces. It covers Admissions, Attendance, Assessments, Fees, Events, Hostel, Transport, Library, Exam, Certificates, ID Cards, Student/Parent portals, and more.

This document provides a **detailed gap analysis** comparing the current implementation against:

1. **ERPNext v15 Education module** built-in capabilities — identifying what is already integrated vs. what still needs custom DocTypes vs. what could leverage native features.
2. **Nine market competitors** (Bloombyte, MasterSoft, SUMS, LoiLoNote, Access Education, OneAdvanced, PowerSchool SIS, Teachmint, EZAE) — identifying feature gaps and differentiation opportunities.
3. **A prioritized implementation roadmap** — P0–P3 items with detailed Frappe/ERPNext implementation strategies.

### Current App Statistics

| Metric | Count |
|---|---|
| Custom DocTypes | ~97 fixtures (including child tables; ~70 standalone DocTypes) |
| Custom Server Scripts | 33 |
| Custom Client Scripts | 48 |
| Custom Workspaces | 12 |
| Modules Used | `Education`, `Custom` |
| Portal / Web Views | None (0 DocTypes with `has_web_view: 1`) |
| Print Format fixtures | None |
| Report fixtures | None |

**Important Discrepancy Note:** The comprehensive analysis source material describes Bizaxl as *already having* richly featured Student and Parent portals with online fee payment, hall-ticket downloads, PTM booking, homework/assignments, and live classes. However, **none of these portal features currently exist in this codebase**. The source material describes an aspirational product specification, not the current implementation. Portal features are correctly listed as gaps below.

#### Portal Prerequisites:
Before portal pages can be built, the following must be enabled on existing DocTypes:
- `has_web_view: 1` on DocTypes that need web-facing pages (Student Certificate, Hall Ticket, etc.)
- `allow_guest_to_view: 1` on DocTypes needing public access (Certificate verification)
- `is_published_field` and `route` fields for web routing
- Portal templates in `school_management_software/templates/`
- The currently empty `public/css/` and `public/js/` directories must be populated with portal styles and scripts

---

## 2. Existing Feature Inventory — ERPNext v15 Mapping

This section maps every existing feature in the app to its implementation approach — whether it extends an ERPNext Education built-in DocType, uses a custom DocType, or leverages a Frappe framework feature.

### 2.1 Front Office & Admissions

| Feature | Implementation | ERPNext Integration | Notes |
|---|---|---|---|
| **Student Admission** | Custom DocType: `Create Admission` (Submittable) | Extends ERPNext `Student Admission` workflow | Links to `Student Admission`, `Student Applicant`, `Program` |
| **Student Applicant** | ERPNext native | Built-in `Student Applicant` | Used via workspace links |
| **Program Enrollment** | Custom DocType: `Custom Program Enrollment` (Submittable) | Extends ERPNext `Program Enrollment` | Auto-creates `Custom Student` on submit |
| **Student Enrollment** | Custom DocType: `Program Student Entry` | Integration helper | Links Program → Students |
| **Application Workflow** | Server Script: `approved` | Validates `Custom Program Enrollment` against `Create Admission` status | Prevents enrollment unless admission is "Approved" |
| **Auto-sync on enrollment** | Server Script: `sync data when enrollment is submitted` | Before Submit on `Custom Program Enrollment` | Auto-creates/link `Custom Student` records |

#### Integration Points with ERPNext Native:
- `Student Admission` (ERPNext Education) → `Create Admission` (Custom) → `Custom Program Enrollment` (Custom) → `Custom Student` (Custom)
- `Student Applicant` (ERPNext Education) — linked in workspaces
- `Program` (ERPNext Education) — referenced across admission workflow

#### Gap:
- The admission workflow has **two parallel paths**: `Student Admission` (ERPNext) → `Student Applicant` (ERPNext) → `Program Enrollment` (ERPNext), and also `Create Admission` (Custom) → `Custom Program Enrollment` (Custom). These should be consolidated or clearly separated.
- No **Lead/Enquiry CRM** tracking (enquiry source, follow-up status, conversion tracking) — covered by the Reception module gap below.

### 2.2 Reception / Front Office

| Feature | Implementation | ERPNext Integration | Notes |
|---|---|---|---|
| **Complaint Management** | Custom DocType: `Grievance Box` | Standalone custom DocType | Server Script notifies maintenance on assignment |
| **Response Templates** | — | Not yet implemented | Configurable templates for complaint responses |

#### Gaps (Reception Module):
The comprehensive analysis identifies the following **Reception features as missing** from the current fixture set:

| Missing Feature | Priority | Recommended Approach |
|---|---|---|
| **Admission Enquiry Tracking** | P1 | Custom DocType `Admission Enquiry` with fields for: source (walk-in, phone, web, referral), status (new, contacted, follow-up, converted, lost), assigned to, follow-up date, remarks |
| **Postal Record (Incoming/Outgoing)** | P2 | Custom DocType `Postal Record` with type (Incoming/Outgoing), date, sender/recipient, description, reference number, confidential flag, attachment |
| **Call Log** | P2 | Custom DocType `Call Log` with caller name, phone, direction (Incoming/Outgoing), duration, purpose, staff member, follow-up required |
| **Visitor Log** | P2 | Custom DocType `Visitor Log` with visitor name, contact, purpose, whom to meet, entry time, exit time, id proof, vehicle number |
| **Configurable Response Templates** | P2 | Custom DocType `Response Template` with title, category, content (Text Editor), applicable to (Complaint, Enquiry, etc.) |

### 2.3 Student & Parent Lifecycle

| Feature | Implementation | ERPNext Integration | Notes |
|---|---|---|---|
| **Custom Student** | Custom DocType: `Custom Student` | Extends but replaces ERPNext `Student` with richer fields | Includes: naming series, personal details, address, relations (guardians, siblings), exit info, fee status |
| **Student Guardian** | Custom Child Table: `Custom Student Guardian` | Linked to `Custom Student` | Name, relation, contact, email, occupation |
| **Student Sibling** | Custom Child Table: `Custom Student Sibling` | Linked to `Custom Student` | Name, class, school |
| **Guardian Profile** | Custom DocType: `Guardian Profile` | Standalone with links to students | Interests, education, occupation, multiple students per guardian |
| **Guardian Profile Interest** | Custom Child Table: `Guardian Profile Interest` | Linked to `Guardian Profile` | Interest type and description |
| **Guardian Profile Student** | Custom Child Table: `Guardian Profile Student` | Links guardian to student records | Student link, relationship |
| **Student Event** | Custom DocType: `Student Event` | Standalone | Server Script sends email notifications to guardians on submit |
| **Student Kit Issue** | Custom DocType: `Student Kit Issue` | Standalone | Tracks kit items issued to students |
| **Kit Item Detail** | Custom Child Table: `Kit Item Detail` | Linked to `Student Kit Issue` | Item, quantity, status, color coding |

#### Integration Points with ERPNext Native:
- `Student` (ERPNext Education) — core student record used alongside custom
- `Guardian` (ERPNext Education) — used in `Create Admission` and workspace links
- `Student Log` (ERPNext) — referenced in Masters workspace
- `Education Settings` (ERPNext) — referenced in Masters workspace

#### Gap: Student Portal & Parent Portal
The comprehensive analysis source material describes richly featured Student and Parent portals as existing features of "Bizaxl" — however, **they are not implemented in this codebase**. Currently:
- The app has **no dedicated web view DocTypes** for portals
- No `has_web_view` or `allow_guest_to_view` enabled on any existing DocType
- No custom web templates or portal routes exist in the `public/` directory

| Portal Feature | Status | Recommended Approach |
|---|---|---|
| **Student Profile View** | ❌ Missing | Create web templates or portal pages using Frappe Portal |
| **Online Fee Payment** | ❌ Missing | Integrate with ERPNext Payment Entry + Razorpay/PayPal via custom web form |
| **Hall Ticket Download** | ⚠️ Partial | `Hall Ticket` DocType exists but no portal view |
| **Homework/Assignments** | ❌ Missing | Extend with custom DocType + portal integration |
| **Leave Application** | ❌ Missing | Create Student-facing web form linked to leave workflow |
| **Live Classes** | ❌ Missing | Integrate with Frappe Meeting/Video conferencing or Jitsi API |
| **Parent Dashboard** | ❌ Missing | Build Frappe Portal pages with student summary |
| **PTM Booking** | ❌ Missing | Custom DocType `Parent Teacher Meeting` with web form |
| **Notifications Center** | ❌ Missing | Use Frappe `Notification` + custom portal view |

### 2.4 Academics

> **Note:** The source material lists "Content Master — Article, Video, Quiz" and "Online Exam — question bank, online tests, auto evaluation, result publishing" and "Live Class Rooms — online classes, meeting scheduling, attendance tracking" as existing features. However:
> - `Article`, `Video`, `Quiz` are **ERPNext Education native DocTypes**, not custom — the custom app simply links to them via the Masters workspace.
> - **Online Exam** and **Live Class Rooms** have **no custom DocType fixtures** in this app. These are aspirational features not yet implemented.

| Feature | Implementation | ERPNext Integration | Notes |
|---|---|---|---|
| **Course Schedule** | Custom DocType: `Custom Course Schedule` | Extends ERPNext `Course Schedule` | Adds timetable preview, weekly slots, branch, program, student group |
| **Course Schedule Slot** | Custom Child Table: `Course Schedule Slot` | Linked to `Custom Course Schedule` | Day, time, course, instructor, room |
| **Timetable Detail** | Custom DocType: `Custom Timetable Detail` (Child Table) | Generic timetable row | Period, subject, from/to time, instructor, room, color |
| **Teacher Weekly Schedule** | Custom DocType: `Teacher Weekly Schedule` | Links Instructor to weekly schedule | Standalone timetable management |
| **Custom Timetable Detail** | Custom Child Table | Generic period entry | Used across timetable implementations |
| **Assessment Group** | Custom DocType: `Assessment Group` | Hierarchical grouping | Parent-child assessment group tree |
| **Report Card** | Custom DocType: `Report Card` | Standalone | Student-wise report card |
| **Report Card Subject** | Custom Child Table: `Report Card Subject` | Subject-level marks | Subject, score, grade, remarks |
| **Report Card Trait** | Custom Child Table: `Report Card Trait` | Behavioral traits | Trait, rating, remarks |
| **Trait Master** | Custom DocType: `Trait Master` | Behavioral trait definition | Name, description, category |
| **Trait Entry** | Custom DocType: `Trait Entry` | Trait evaluation | Linked to student, multiple traits |
| **Trait Entry Detail** | Custom Child Table | Individual trait ratings | Trait, score, comments |
| **Student Rank** | Custom DocType: `Student Rank` | Student ranking | Rank, academic year, term, based on assessment |
| **Student Progress Card** | Custom DocType: `Student Progress Card` | Combined progress card | Links subjects, traits, ranks |
| **Student Progress Card Detail** | Custom Child Table | Subject entries for progress card | Subject, marks, grade, teacher remarks |

#### Integration Points with ERPNext Native:
- `Course Schedule` (ERPNext Education) — base DocType
- `Course` (ERPNext) — referenced across academic DocTypes
- `Program` (ERPNext) — grade/program reference
- `Instructor` (ERPNext) — teacher reference
- `Student Group` (ERPNext) — class/section reference
- `Assessment Plan` (ERPNext) — assessment management
- `Assessment Criteria` (ERPNext) — criteria definition
- `Assessment Result` (ERPNext) — result records
- `Grading Scale` (ERPNext) — grading configuration
- `Topic` (ERPNext) — course topics
- `Room` (ERPNext) — classroom reference

### 2.5 Attendance

| Feature | Implementation | ERPNext Integration | Notes |
|---|---|---|---|
| **Student Attendance** | Links to ERPNext `Student Attendance` | Native ERPNext | Via workspace links |
| **Leave Application** | Custom DocType: `Hostel leaves` | Extends student leave for hostel context | Auto-fetches student hostel details |
| **Bulk Attendance** | Links to ERPNext `Student Attendance Tool` | Native ERPNext | Via workspace links |
| **Attendance Reports** | Links to ERPNext reports | Native ERPNext reports | Monthly, batch-wise, absent reports |
| **Mess Attendance** | Custom DocType: `Mess Attendance` | Standalone | Separate meal attendance tracking |
| **Hostel Attendance** | Custom DocType: `Hostel Attendance` | Standalone | Hostel-specific attendance |
| **Exam Attendance** | Custom DocType: `Exam Attendance` | Standalone | Per-exam attendance tracking |

#### Gaps:
| Missing Feature | Priority | Recommended Approach |
|---|---|---|
| **Biometric/RFID integration** | P0 | Create a `Biometric Device` DocType + API integration hook. Use Frappe Scheduler to pull attendance data. Store in `Student Attendance` / custom attendance table |
| **Staff Attendance** | P1 | Already partially covered by ERPNext HR, but needs custom portal view for staff |
| **Geo-fenced mobile attendance** | P2 | Create custom API endpoint + mobile-friendly web form with GPS coordinates |

### 2.6 Examination

| Feature | Implementation | ERPNext Integration | Notes |
|---|---|---|---|
| **Exam Term** | Custom DocType: `Exam Term` | Standalone | Term name, assessment group link, academic year, dates |
| **Exam Schedule** | Custom DocType: `Exam Schedule` | Standalone | Subject, date, time, room, invigilator |
| **Exam Hall** | Custom DocType: `Exam Hall` | Venue management | Hall name, capacity, location, amenities |
| **Hall Allocation** | Custom DocType: `Hall Allocation` | Student → Hall mapping | Links student group to hall, auto-fetches students |
| **Hall Allocation Student** | Custom Child Table | Allocated students | Student, seat number, roll number |
| **Hall Ticket** | Custom DocType: `Hall Ticket` | Student hall ticket generation | Links to exam schedule, student details |
| **Hall Ticket Subject** | Custom Child Table | Subjects in hall ticket | Subject, date, time, room |
| **Student Admit Card** | Custom DocType: `Student Admit Card` | Admit card record | Links to student and exam |
| **Admit Card Template** | Custom DocType: `Admit Card Template` | Configurable template | Print format, layout, fields |
| **Exam Attendance** | Custom DocType: `Exam Attendance` | Tracks exam-day attendance | Per subject, student attendance |

#### Integration Points:
- ERPNext `Assessment Plan` — linked for result integration
- ERPNext `Assessment Result` — result recording
- ERPNext `Assessment Result Tool` — result entry tool

### 2.7 Fees & Finance

| Feature | Implementation | ERPNext Integration | Notes |
|---|---|---|---|
| **Applicant Fee** | Custom Child Table: `Applicant Fee` | Linked to `Create Admission` | Fee structure, amount, components |
| **Custom Student Fee Installment** | Custom DocType: `Custom Student Fee Installment` | Linked to `Custom Student` | Invoice tracking, due date, paid/outstanding |
| **Transport Fee** | Custom DocType: `Transport Fee` | Standalone | Route-based fee |
| **Hostel Fee** | Custom DocType: `Hostel Fee` | Standalone | Room-type based fee |
| **Fee Auto-calculation** | Server Script: `fee auto calculation` | On `Custom Student` submit | Calculates totals from Sales Invoices |
| **Auto-create Sales Invoice** | Server Script: `auto create Sales Invoice on submit` | On `Custom Program Enrollment` submit | Creates invoice from fee structure |
| **Fee Collection Report** | Links to ERPNext reports | Native ERPNext | Student Fee Collection, Program wise Fee Collection |
| **Library Fine** | Custom DocType: `Library fine` | Standalone | Fine calculation and payment |
| **Fine Payment** | Server Script: `Library Fine - Process Payment` | Process fine payments | Updates fine status |
| **Fine Doctypes** | Custom DocType: `Fine Doctypes` | Standalone | Fine type definitions |

#### Integration Points:
- `Sales Invoice` (ERPNext Accounts) — core fee collection DocType
- `Payment Entry` (ERPNext Accounts) — payment recording
- `Fee Category` (ERPNext Education) — fee categorization
- `Fee Structure` (ERPNext Education) — fee structure with components
- `Fee Schedule` (ERPNext Education) — fee due schedule
- `Customer` (ERPNext Accounts) — student as customer

### 2.8 Hostel Management

| Feature | Implementation | ERPNext Integration | Notes |
|---|---|---|---|
| **Hostel** | Custom DocType: `Hostel` | Standalone | Hostel name, type (Boys/Girls/Co-ed), floors, capacity, warden |
| **Hostel Block** | Custom DocType: `Hostel Block` | Standalone | Block within hostel |
| **Hostel Room** | Custom DocType: `Hostel Room` | Standalone | Room number, floor, type, beds, status, fee |
| **Hostel Bed** | Custom DocType: `Hostel Bed` | Standalone | Individual bed tracking |
| **Hostel Room Types** | Custom DocType: `Hostel Room Types` | Room type configuration | Sharing type, amenities, base fee |
| **Hostel Application** | Custom DocType: `Hostel Application` | Application workflow | With approve/reject buttons |
| **Hostel Admission** | Custom DocType: `Hostel Admission` | Check-in/out workflow | Admission status (Checked In, Checked Out) |
| **Hostel Card** | Custom DocType: `Hostel Card` | Identity card for hostel | Card creation and printing |
| **Hostel Check-Out** | Custom DocType: `Hostel Check-Out` | Check-out process | Clears room occupancy |
| **Hostel Fee** | Custom DocType: `Hostel Fee` | Fee configuration | Room-based fee structure |
| **Hostel leaves** | Custom DocType: `Hostel leaves` | Leave management | Approval workflow, gate pass, return tracking |
| **Hostel Medical Incident** | Custom DocType: `Hostel Medical Incident` | Health incident tracking | Incident type, treatment, follow-up |
| **Hostel Visitor Log** | Custom DocType: `Hostel Visitor Log` | Visitor tracking | Entry/exit, purpose, student relationship |
| **Hostel Asset Issue** | Custom DocType: `Hostel Asset Issue` | Asset tracking | Issue and return of hostel assets |
| **Hostel Asset Issue Item** | Custom Child Table | Individual asset items | Item, quantity, condition |
| **Warden** | Custom DocType: `Warden` | Staff management | Warden profile, assignment, contact |
| **Grievance Box** | Custom DocType: `Grievance Box` | Complaint management | Complaint type, status, assignment, resolution |
| **Room Inspection** | Custom DocType: `Room Inspection` | Inspection records | Inspection date, cleanliness, repairs needed |
| **Room Transfer** | Custom DocType: `Room Transfer` | Room change workflow | From room, to room, reason, approval |
| **Mess Menu** | Custom DocType: `Mess Menu` | Weekly/daily menu | Day, meal type, items |
| **Mess Attendance** | Custom DocType: `Mess Attendance` | Meal attendance | Per meal, per student |
| **Hostel Attendance** | Custom DocType: `Hostel Attendance` | Daily hostel attendance | Present/absent tracking |

#### Integration with ERPNext:
- `Employee` (ERPNext HR) — linked as Warden
- `Student` (ERPNext Education) — hostel student reference

#### Occupancy Automation:
- Server Script: `to update room occupancy` — auto-updates bed counts
- Server Script: `frees the room if the student check-out` — release on checkout
- Server Script: `to keep room_display updated automatically` — computed display field
- Client Script: `filter dropdown to only show allocatable rooms + render the live card` — room availability
- Client Script: `auto-fetch Room/Block/Warden on student select + live duration` — auto-populate from admission

### 2.9 Transport Management

| Feature | Implementation | ERPNext Integration | Notes |
|---|---|---|---|
| **Transport Route** | Custom DocType: `Transport Route` | Standalone | Route name, stops, distance, fee |
| **Transport Stop** | Custom DocType: `Transport Stop` | Stop management | Stop name, location, order in route |
| **Transport Vehicle** | Custom DocType: `Transport Vehicle` | Vehicle master | Registration, capacity, driver, insurance |
| **Transport Fee** | Custom DocType: `Transport Fee` | Fee configuration | Route-based fee |
| **Student Transport Assignment** | Custom DocType: `Student Transport Assignment` (Submittable) | Student → route mapping | Boarding stop, drop point, fee status, active flag |

#### Integration with ERPNext:
- `Driver` (ERPNext HR) — referenced in workspace workflow
- `Vehicle Log` (ERPNext HR/Fleet) — vehicle usage tracking
- `Route History` (ERPNext) — route tracking

#### Gaps:
| Missing Feature | Priority | Recommended Approach |
|---|---|---|
| **GPS Bus Tracking** | P3 | Integrate with GPS device API; create `BusTracking` DocType for real-time location data |
| **Parent-facing live tracking** | P3 | Portal view consuming tracking data |
| **Route optimization** | P3 | Custom Server Script using geolocation APIs |

### 2.10 Library Management

| Feature | Implementation | ERPNext Integration | Notes |
|---|---|---|---|
| **Library Book** | Custom DocType: `Library Book` | Standalone | ISBN, author, category, publisher, copies, rack, cover image |
| **Book Author** | Custom DocType: `Book Author` | Author master | Author name, bio |
| **Book Category** | Custom DocType: `Book Category` | Category master | Category hierarchy |
| **Book Copy** | Custom DocType: `Book Copy` | Individual copy tracking | Copy number, status (Available/Issued/Damaged/Lost) |
| **Library Rack** | Custom DocType: `Library Rack` | Rack/location master | Rack name, section, floor |
| **Library Member** | Custom DocType: `Library Member` | Member registration | Links to Student/Employee, membership dates, max books |
| **Book Issue** | Custom DocType: `Book Issue` | Issue transaction | Student/employee, book copy, issue date, due date |
| **Book Return** | Custom DocType: `Book return` | Return transaction | Return date, condition, fine if applicable |
| **Library Fine** | Custom DocType: `Library fine` | Fine calculation and payment | Overdue days, fine amount, paid status |
| **Library Settings** | Custom DocType: `Library Settings` (Single) | System-wide config | Max books per member, fine per day, lending period |
| **Kit Item Detail** | Custom DocType: `Kit Item Detail` | Item details | Used for kit issue tracking |

#### Automation:
- Server Script: `Book Issue - Mark Copy as Issued` — updates copy status
- Server Script: `Book Issue - Validate & Set Due Date` — auto-calculates due date
- Server Script: `Book Return - Release Book Copy` — releases copy on return
- Server Script: `create_fine_on_book_return` — auto-creates fine for overdue
- Server Script: `Library Fine - Process Payment` — fine payment processing
- Client Script: `Validate Max Book Issue Limit` — validates against Library Settings
- Client Script: `Book Issue` — UI enhancements
- Client Script: `book return` — UI enhancements

### 2.11 Events & Communication

| Feature | Implementation | ERPNext Integration | Notes |
|---|---|---|---|
| **School Event** | Custom DocType: `School Event` | Standalone | Title, type, dates, venue, audience, description, publish status |
| **Event Type** | Custom DocType: `Event Type` | Event categorization | Type name, color, icon |
| **Event Attachment** | Custom DocType: `Event Attachment` | File attachments | Linked to events |
| **Event Gallery** | Custom DocType: `Event Gallery` | Photo gallery | Event photos with captions |
| **Event Participant** | Custom DocType: `Event Participant` | Participant tracking | Student/employee participation |
| **Student Event** | Custom DocType: `Student Event` | Student-facing events | Auto-emails guardians on submit |
| **Meeting Schedule** | Custom DocType: `Meeting Schedule` | Meeting management | Agenda, attendees, minutes |
| **Meeting Child Table** | Custom Child Table | Meeting agenda items | Topic, presenter, duration |
| **Gate Pass** | Custom DocType: `Gate Pass` | Entry/exit authorization | Auto-generates pass number on approval |
| **Notice / Communication** | Via Server Scripts | Email notifications | Event notifications, complaint assignments |

#### Automation:
- Server Script: `Notification Script` — publish confirmation on School Event
- Server Script: `Student event Celebration` — sends guardian emails with event details
- Server Script: `auto-generate Gate Pass Number on approval` — workflow automation
- Server Script: `Scheduler Event Frequency Daily` — daily scheduled tasks
- Client Script: `date validation for school events` — date range validation

### 2.12 Certificates & ID Cards

| Feature | Implementation | ERPNext Integration | Notes |
|---|---|---|---|
| **Certificate Template** | Custom DocType: `Certificate Template` | Configurable template | HTML template, dimensions, orientation |
| **Student Certificate** | Custom DocType: `Student Certificate` | Generated certificate | Links to student, template, PDF attachment |
| **Employee Certificate** | Custom DocType: `Employee Certificate` | Staff certificates | Links to employee, template |
| **ID Card Template** | Custom DocType: `ID Card Template` | Card layout | Dimensions, fields, orientation |
| **Student ID Card** | Custom DocType: `Student ID Card` | Student identity card | Photo, name, class, roll, blood group |
| **Employee ID Card** | Custom DocType: `Employee ID Card` | Employee identity card | Photo, name, designation, department |
| **Student ID Card Batch** | Custom DocType: `Student ID Card Batch` | Bulk generation | Generate cards for entire class/group |
| **Student ID Card Batch Item** | Custom Child Table | Individual batch items | Student, status, card reference |
| **Admit Card Template** | Custom DocType: `Admit Card Template` | Exam admit card layout | Configurable template for admit cards |
| **Student Admit Card** | Custom DocType: `Student Admit Card` | Generated admit card | Links to student, exam schedule |

##### Existing Print Format Candidates:
The following DocTypes are natural candidates for custom Print Formats (none currently have Print Format fixtures):
- `Student Certificate` — Certificate print layout
- `Employee Certificate` — Staff certificate layout
- `Student ID Card` — ID card layout (portrait/landscape)
- `Employee ID Card` — Staff ID card layout
- `Hall Ticket` — Exam hall ticket layout
- `Student Admit Card` — Admit card layout
- `Report Card` — Student report card / marksheet layout
- `Hostel Card` — Hostel identity card

**Recommendation:** Create Print Format fixtures for each. Use the existing DocType template fields (e.g., `Certificate Template`, `ID Card Template`, `Admit Card Template`) to give schools configurability. This is a higher-value effort than hardcoding Print Formats.

#### Existing Report Candidates:
The workspaces already link to ERPNext native query reports. The following custom reports should be built:
- **Hostel Occupancy Report** — rooms, beds, occupancy %, by hostel/block
- **Transport Fee Dues Report** — students with pending transport fees
- **Library Circulation Report** — books issued/returned, overdue items, fines collected
- **Exam Result Analysis** — pass %, subject-wise performance, rank list
- **Certificate Issuance Report** — certificates generated by type, date range, student
- **Hostel Attendance Summary** — daily/weekly/monthly attendance by hostel
- **Mess Attendance & Meal Count** — meals served, attendance by date/mess
- **Fee Outstanding Report** — students with outstanding fee balances across categories

**Report Type Recommendation:** Use **Script Report** (Python-based) for complex analytics like Hostel Occupancy, Exam Result Analysis. Use **Query Report** (SQL-based) for straightforward list reports like Fee Dues, Library Circulation.

### Automation:
- Server Script: `generate_student_certificate` — API endpoint for PDF generation

**Important:** The existing Server Script in `generate_student_certificate` uses `frappe.utils.pdf.get_pdf(html)`. The local variable in that script is `cert` (the template DocType), so the correct field access is `cert.html_template` not `template.html_template`. The `get_pdf()` function is still available in v15 via `from frappe.utils import get_pdf` or `frappe.utils.pdf.get_pdf()` — verify the correct import for your specific Frappe v15 build.
- Server Script: `generate_employee_certificate` — employee certificate generation
- Server Script: `generate_student_id_cards` — batch ID card generation
- Server Script: `the actual generation logic` — PDF rendering engine
- Server Script: `Prevent Duplicate Certificates` — validation to avoid duplicates

### 2.13 HR & Employee Management

| Feature | Implementation | ERPNext Integration | Notes |
|---|---|---|---|
| **Employee Certificate** | Custom DocType: `Employee Certificate` | Extends ERPNExT Employee | Certificate issuance for staff |
| **Employee ID Card** | Custom DocType: `Employee ID Card` | Staff identity cards | Photo, department, designation |

#### ERPNext Native HR Features Used (via workspace links):
- `Employee` (ERPNext HR) — employee master
- `Department` (ERPNext) — department structure
- `Designation` (ERPNext) — job titles
- `Job Applicant` (ERPNext HR) — recruitment
- `Job Opening` (ERPNext HR) — job postings
- `Appraisal` (ERPNext HR) — performance reviews
- `Training Event` (ERPNext HR) — training management
- `Leave Application` (ERPNext HR) — staff leave
- `Salary Slip` (ERPNext Payroll) — payroll
- `Salary Structure` (ERPNext Payroll) — compensation

### 2.14 Procurement & Inventory

| Feature | Implementation | ERPNext Integration | Notes |
|---|---|---|---|
| **Kit Item Detail** | Custom DocType: `Kit Item Detail` | Item tracking | Student kit items |

#### ERPNext Native Features Used:
- `Item` (ERPNext Stock) — inventory items
- `Material Request` (ERPNext Buying) — procurement request
- `Purchase Order` (ERPNext Buying) — ordering
- `Purchase Receipt` (ERPNext Stock) — goods receipt
- `Supplier` (ERPNext Buying) — vendor management

---

## 3. Gap Analysis — Detailed Findings

### 3.1 Coverage Summary by Module

| Module | Bizaxl Status | Competitive Benchmark | Gap Level |
|---|---|---|---|
| Admissions | ⚠️ Partial | ✅ Bloombyte, MasterSoft, PowerSchool | **Medium** — duplicate workflows, no enquiry CRM |
| Reception/Front Office | ❌ Missing | ❌ None of 9 competitors have it | **Opportunity** — first-mover advantage |
| Student Management | ✅ Strong | ✅ All competitors | Low — minor refinements |
| Parent Portal | ❌ Missing | ✅ Most competitors | **High** |
| Student Portal | ❌ Missing | ✅ Most competitors | **High** |
| Academics/Timetable | ✅ Strong | ✅ All competitors | Low |
| Attendance | ✅ Good | ✅ All competitors | **Medium** — no biometric/RFID |
| Assessment/Exams | ✅ Strong | ✅ All competitors | Low |
| Fees/Finance | ✅ Strong | ⚠️ Partial in most | Low |
| Hostel | ✅ Strong | ✅ Bloombyte, MasterSoft | Low |
| Transport | ✅ Good | ⚠️ Partial | **Medium** — no GPS tracking |
| Library | ✅ Strong | ⚠️ Partial | Low |
| Events | ✅ Good | ❌ Most missing | Low |
| Certificates/ID Cards | ✅ Strong | ⚠️ Partial | Low — no QR verification |
| HR/Payroll | ✅ Via ERPNext | ✅ Bloombyte, Access | Low |
| Accounting | ✅ Via ERPNext | ⚠️ Partial in most | Low |
| Procurement | ✅ Via ERPNext | ❌ Most missing | Low |
| Website/CMS | ✅ Via ERPNext Website (not custom) | ❌ None have it | ERPNext built-in Website module covers this |
| Mobile Apps | ❌ Missing | ✅ Most competitors | **High** |
| AI Capabilities | ❌ Missing | ⚠️ Partial (LoiLoNote, Access, Teachmint) | **High** |
| Content Library | ❌ Missing | ✅ LoiLoNote, Teachmint | **Medium** |
| Alumni | ❌ Missing | ✅ MasterSoft | **Medium** |
| Gamification | ❌ Missing | ❌ None | **Opportunity** |
| Compliance Certifications | ❌ Missing | ✅ LoiLoNote, PowerSchool | **Medium** |

### 3.2 Critical Gaps (P0)

#### P0.1 — Native Mobile Apps (Parent, Student, Staff)

**Why:** Every serious competitor ships at least one mobile app. This is the single most visible gap.

**Implementation Strategy (Frappe/ERPNext):**
```python
# Approach: Frappe mobile app framework + custom API endpoints
# No iOS/Android native code needed to start

# 1. Create REST API endpoints in custom app
# File: school_management_software/api/mobile.py

import frappe
from frappe import _

@frappe.whitelist(allow_guest=False)
def get_student_dashboard(student_id):
    """Mobile dashboard for students"""
    # Attendance summary, fee status, timetable, upcoming exams
    pass

@frappe.whitelist(allow_guest=False)
def get_parent_dashboard(parent_email):
    """Parent portal mobile data"""
    pass

# 2. Create mobile-optimized web templates
# Create portal pages in Frappe with responsive design
# Use Frappe's built-in mobile framework or PWA approach
```

**Implementation Checklist:**
- [ ] Create Frappe API endpoints for mobile data
- [ ] Build PWA-compatible web portal
- [ ] Create role-based mobile dashboards (Student, Parent, Staff)
- [ ] Push notification integration via Frappe Push Notification
- [ ] Offline-capable data sync for attendance

**ERPNext Integration:**
- Use `Student` (ERPNext) for student data
- Use `Guardian` (ERPNext) for parent mapping
- Use `Program Enrollment` (ERPNext) for academic status
- Use `Fees`, `Sales Invoice`, `Payment Entry` for financial data

---

#### P0.2 — Biometric/RFID Attendance Integration

**Why:** Removes manual marking friction; explicitly demanded by larger schools.

**Implementation Strategy:**
```python
# 1. Create Biometric Device DocType
# File: school_management_software/doctype/biometric_device/biometric_device.json

{
    "doctype": "DocType",
    "name": "Biometric Device",
    "module": "Education",
    "custom": 1,
    "fields": [
        {"fieldname": "device_name", "fieldtype": "Data", "label": "Device Name", "reqd": 1},
        {"fieldname": "device_type", "fieldtype": "Select", "label": "Device Type",
         "options": "Fingerprint\nRFID\nFace Recognition\nIris"},
        {"fieldname": "ip_address", "fieldtype": "Data", "label": "IP Address"},
        {"fieldname": "port", "fieldtype": "Int", "label": "Port"},
        {"fieldname": "api_endpoint", "fieldtype": "Data", "label": "API Endpoint"},
        {"fieldname": "api_key", "fieldtype": "Password", "label": "API Key"},
        {"fieldname": "location", "fieldtype": "Data", "label": "Location (Gate/Classroom)"},
        {"fieldname": "is_active", "fieldtype": "Check", "label": "Is Active"}
    ]
}

# 2. Scheduler to pull attendance data
# File: school_management_software/attendance_sync.py

def sync_biometric_attendance():
    """Called by Frappe Scheduler - pulls data from all active devices"""
    devices = frappe.get_all("Biometric Device", filters={"is_active": 1})
    for device in devices:
        # Call device API, get punch data
        # Map to Student/Faculty records
        # Create Student Attendance records
        pass

# 3. Map biometric ID to Student/Employee
# Add field to Custom Student: biometric_id, rfid_card_number
# Add field to Employee (via Custom Field): biometric_id, rfid_card_number
```

**Implementation Checklist:**
- [ ] Create `Biometric Device` DocType
- [ ] Create `Biometric Attendance Log` DocType (raw punch data)
- [ ] Custom fields: `biometric_id` on Student and Employee
- [ ] Scheduler script for periodic sync
- [ ] Manual attendance reconciliation tool
- [ ] Support for ZKTeco, Mantra, and BioMatric standard APIs

**ERPNext Integration:**
- Maps directly to `Student Attendance` (ERPNext Education)
- Maps to `Employee Attendance` via (ERPNext HR)
- Reuses existing attendance reports

---

#### P0.3 — AI-Assisted Grading & Admin Assistant

**Why:** Fastest-moving differentiator; currently a total blank.

**Implementation Strategy:**
```python
# 1. AI Configuration DocType
# File: school_management_software/doctype/ai_settings/ai_settings.json

{
    "doctype": "DocType",
    "name": "AI Settings",
    "module": "Education",
    "custom": 1,
    "is_single": 1,
    "fields": [
        {"fieldname": "provider", "fieldtype": "Select", "label": "AI Provider",
         "options": "OpenAI\nAzure OpenAI\nAnthropic\nLocal LLM"},
        {"fieldname": "api_key", "fieldtype": "Password", "label": "API Key"},
        {"fieldname": "model", "fieldtype": "Data", "label": "Model Name"},
        {"fieldname": "max_tokens", "fieldtype": "Int", "label": "Max Tokens", "default": 2000}
    ]
}

# 2. AI Grading Assistant
# File: school_management_software/api/ai_grader.py

@frappe.whitelist()
def grade_subjective_answer(question, student_answer, rubric=None):
    """AI-powered grading for subjective answers"""
    # Call AI API with prompt engineering
    # Return score, feedback, and suggestions
    pass

# 3. AI Admin Assistant
# File: school_management_software/api/ai_assistant.py

@frappe.whitelist()
def ask_assistant(question, context_doctype=None, context_docname=None):
    """Natural language Q&A about school data"""
    # Retrieve context from Frappe documents
    # Generate response using AI
    pass

# 4. AI Content Generator
@frappe.whitelist()
def generate_quiz(topic, difficulty, num_questions):
    """Auto-generate quiz questions"""
    pass
```

**Implementation Checklist:**
- [ ] AI Settings DocType (Single)
- [ ] AI grading API endpoint for subjective answers
- [ ] AI assistant chatbot for admin queries
- [ ] AI-generated quiz questions
- [ ] AI-generated report card remarks
- [ ] AI-powered student performance insights

---

### 3.3 High-Priority Gaps (P1)

#### P1.1 — Curriculum Content Library

**Why:** Turns Content Master (Article, Video, Quiz) from an empty container into a real product.

**Implementation Strategy:**
```python
# Extend existing Content Master DocTypes
# Add Custom Fields to Quiz, Article, Video:
# - board (CBSE, ICSE, State, etc.)
# - grade (class-level)
# - subject (Course link)
# - chapter
# - difficulty_level
# - tags (multi-select)

# Create Question Bank DocType
# File: school_management_software/doctype/question_bank/question_bank.json

{
    "doctype": "DocType",
    "name": "Question Bank",
    "module": "Education",
    "fields": [
        {"fieldname": "question", "fieldtype": "Text Editor", "label": "Question"},
        {"fieldname": "question_type", "fieldtype": "Select",
         "options": "Multiple Choice\nTrue/False\nShort Answer\nLong Answer\nFill in the Blank\nMatch the Following"},
        {"fieldname": "subject", "fieldtype": "Link", "options": "Course"},
        {"fieldname": "chapter", "fieldtype": "Data"},
        {"fieldname": "difficulty", "fieldtype": "Select", "options": "Easy\nMedium\nHard"},
        {"fieldname": "marks", "fieldtype": "Int"},
        {"fieldname": "board", "fieldtype": "Select", "options": "CBSE\nICSE\nState Board\nInternational"},
        {"fieldname": "grade", "fieldtype": "Link", "options": "Program"}
    ]
}
```

**Implementation Checklist:**
- [ ] Board-aligned tagging on existing content DocTypes
- [ ] `Question Bank` DocType with rich question types
- [ ] Worksheet creation tool (auto-generate from question bank)
- [ ] Bulk import from CSV/Excel for existing question banks
- [ ] Search and filter by subject, grade, difficulty, board

---

#### P1.2 — Structured LMS / Course Authoring Layer

**Why:** Converts live-class delivery into a full teaching platform.

**Implementation Strategy:**
```python
# Course Authoring DocType
{
    "doctype": "DocType",
    "name": "Course Module",
    "module": "Education",
    "fields": [
        {"fieldname": "course", "fieldtype": "Link", "options": "Course"},
        {"fieldname": "module_title", "fieldtype": "Data"},
        {"fieldname": "module_number", "fieldtype": "Int"},
        {"fieldname": "learning_objectives", "fieldtype": "Text Editor"},
        {"fieldname": "contents", "fieldtype": "Table", "options": "Course Module Content"}
    ]
}

# Course Module Content (Child Table)
{
    "doctype": "DocType",
    "name": "Course Module Content",
    "module": "Education",
    "is_child_table": 1,
    "fields": [
        {"fieldname": "content_type", "fieldtype": "Select",
         "options": "Article\nVideo\nQuiz\nAssignment\nLive Class\nDocument\nEmbed"},
        {"fieldname": "content", "fieldtype": "Dynamic Link", "options": "content_type"},
        {"fieldname": "duration_minutes", "fieldtype": "Int"},
        {"fieldname": "is_mandatory", "fieldtype": "Check"},
        {"fieldname": "order", "fieldtype": "Int"}
    ]
}

# Assignment DocType (enhance existing Homework)
{
    "doctype": "DocType",
    "name": "Assignment",
    "module": "Education",
    "fields": [
        {"fieldname": "title", "fieldtype": "Data"},
        {"fieldname": "course", "fieldtype": "Link", "options": "Course"},
        {"fieldname": "student_group", "fieldtype": "Link", "options": "Student Group"},
        {"fieldname": "due_date", "fieldtype": "Datetime"},
        {"fieldname": "max_score", "fieldtype": "Float"},
        {"fieldname": "submission_type", "fieldtype": "Select",
         "options": "File Upload\nText Entry\nOnline Quiz\nBoth"},
        {"fieldname": "rubric", "fieldtype": "Table", "options": "Assignment Rubric"},
        {"fieldname": "submissions", "fieldtype": "Table", "options": "Assignment Submission"}
    ]
}
```

**Implementation Checklist:**
- [ ] `Course Module` DocType with structured content
- [ ] `Assignment` DocType with submission tracking
- [ ] Student progress tracking per module
- [ ] Integration with Live Class Rooms (Jitsi/Zoom)
- [ ] Student-facing course dashboard
- [ ] Gradebook integration with Assessment Result

---

#### P1.3 — Alumni Management

**Why:** Small build, extends existing Certificate/Student data.

**Implementation Strategy:**
```python
# Alumni DocType
{
    "doctype": "DocType",
    "name": "Alumni Record",
    "module": "Education",
    "fields": [
        {"fieldname": "student", "fieldtype": "Link", "options": "Student"},
        {"fieldname": "batch", "fieldtype": "Link", "options": "Student Batch Name"},
        {"fieldname": "program", "fieldtype": "Link", "options": "Program"},
        {"fieldname": "graduation_year", "fieldtype": "Int"},
        {"fieldname": "current_occupation", "fieldtype": "Data"},
        {"fieldname": "current_organization", "fieldtype": "Data"},
        {"fieldname": "email", "fieldtype": "Data", "options": "Email"},
        {"fieldname": "phone", "fieldtype": "Data", "options": "Phone"},
        {"fieldname": "address", "fieldtype": "Text"},
        {"fieldname": "linkedin_url", "fieldtype": "Data"},
        {"fieldname": "is_active", "fieldtype": "Check", "default": 1},
        {"fieldname": "newsletter_opt_in", "fieldtype": "Check", "default": 1}
    ]
}
```

**Implementation Checklist:**
- [ ] `Alumni Record` DocType
- [ ] Auto-create on student graduation/transfer-out
- [ ] Alumni directory (portal page)
- [ ] Alumni newsletter/communication tool
- [ ] Event management for alumni meets
- [ ] Donation tracking (linked to ERPNext donation tools)

---

### 3.4 Medium-Priority Gaps (P2)

#### P2.1 — QR-Verified Certificates

**Why:** First-mover feature — no K-12 competitor has it.

**Implementation Strategy:**
```python
# Add QR code generation to Certificate DocType
# File: school_management_software/api/certificate_verification.py

@frappe.whitelist(allow_guest=True)
def verify_certificate(certificate_id):
    """Public API for certificate verification"""
    cert = frappe.get_doc("Student Certificate", certificate_id)
    if not cert:
        return {"valid": False, "message": "Certificate not found"}
    
    return {
        "valid": True,
        "student_name": cert.student_name,
        "certificate_type": cert.template,
        "issued_on": cert.generated_on,
        "issued_by": frappe.db.get_value("User", cert.generated_by, "full_name"),
        "certificate_url": cert.certificate_pdf
    }

@frappe.whitelist()
def generate_qr_for_certificate(certificate_id):
    """Generate QR code for certificate"""
    import qrcode
    from io import BytesIO
    import base64
    
    verification_url = f"{frappe.utils.get_url()}/api/method/school_management_software.api.certificate_verification.verify_certificate?certificate_id={certificate_id}"
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(verification_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return qr_base64
```

**ERPNext Libraries:** `qrcode` (PyPI) — add to `requirements.txt` or `pyproject.toml`

**Implementation Checklist:**
- [ ] QR code generation on certificate creation
- [ ] Public verification endpoint (allow_guest=True)
- [ ] Verification portal page
- [ ] Print format with embedded QR code
- [ ] Public URL for each certificate

---

#### P2.2 — Gamification Layer

**Why:** Engagement differentiator — unclaimed by K-12 competitors.

**Implementation Strategy:**
```python
{
    "doctype": "DocType",
    "name": "Gamification Settings",
    "module": "Education",
    "is_single": 1,
    "fields": [
        {"fieldname": "enable_gamification", "fieldtype": "Check", "default": 0},
        {"fieldname": "points_for_attendance", "fieldtype": "Int", "default": 10},
        {"fieldname": "points_for_assignment_submission", "fieldtype": "Int", "default": 20},
        {"fieldname": "points_for_quiz_completion", "fieldtype": "Int", "default": 15},
        {"fieldname": "points_for_high_score", "fieldtype": "Int", "default": 50},
        {"fieldname": "streak_bonus_days", "fieldtype": "Int", "default": 5},
        {"fieldname": "streak_bonus_points", "fieldtype": "Int", "default": 100}
    ]
}

# Student Points & Badges
{
    "doctype": "DocType",
    "name": "Student Points Ledger",
    "module": "Education",
    "fields": [
        {"fieldname": "student", "fieldtype": "Link", "options": "Student"},
        {"fieldname": "date", "fieldtype": "Date"},
        {"fieldname": "activity_type", "fieldtype": "Select",
         "options": "Attendance\nAssignment\nQuiz\nExam\nBehavior\nParticipation\nAchievement"},
        {"fieldname": "reference_doctype", "fieldtype": "Link", "options": "DocType"},
        {"fieldname": "reference_name", "fieldtype": "Dynamic Link", "options": "reference_doctype"},
        {"fieldname": "points", "fieldtype": "Int"},
        {"fieldname": "badge_earned", "fieldtype": "Link", "options": "Badge Definition"}
    ]
}

# Badge Definition
{
    "doctype": "DocType",
    "name": "Badge Definition",
    "module": "Education",
    "fields": [
        {"fieldname": "badge_name", "fieldtype": "Data"},
        {"fieldname": "badge_icon", "fieldtype": "Attach Image"},
        {"fieldname": "description", "fieldtype": "Text"},
        {"fieldname": "criteria_type", "fieldtype": "Select",
         "options": "Points Threshold\nStreak\nAchievement\nEvent"},
        {"fieldname": "criteria_value", "fieldtype": "Int"},
        {"fieldname": "tier", "fieldtype": "Select", "options": "Bronze\nSilver\nGold\nPlatinum"}
    ]
}
```

**Implementation Checklist:**
- [ ] Gamification Settings DocType (Single)
- [ ] Student Points Ledger DocType
- [ ] Badge Definition DocType
- [ ] Server Scripts for automatic point awarding
- [ ] Leaderboard portal page
- [ ] Student dashboard with points, badges, streaks
- [ ] Parent dashboard with gamification summary

---

#### P2.3 — Reception / Front Office Suite

**Why:** First-mover advantage — no competitor offers this.

**Required DocTypes:**
- `Admission Enquiry` — enquiry tracking with source, status, follow-up
- `Postal Record` — incoming/outgoing mail tracking
- `Call Log` — phone call recording
- `Visitor Log` — visitor entry/exit tracking
- `Response Template` — configurable templates for enquiries/complaints

**Implementation Checklist:**
- [ ] Create 5 new DocTypes listed above
- [ ] Workspace: "Front Office" with dashboard
- [ ] Number cards for enquiries, visitors, calls today
- [ ] Client Scripts for auto-numbering and status updates
- [ ] Role-based access (Receptionist role)

#### P2.4 — Compliance Certifications

**Why:** Increasingly important for institutional procurement.

**Implementation Strategy:**
- Implement ISO 27001-ready data handling:
  - Document all data flows
  - Add audit trail fields (`track_changes`, `track_seen`, `track_views`) across sensitive DocTypes
  - Implement role-based access controls
  - Add consent management for student/parent data
- GDPR/FERPA readiness:
  - Data export endpoint for student records
  - Right-to-erasure workflow
  - Data retention policies
- Create compliance documentation module

---

### 3.5 Lower-Priority Gaps (P3)

#### P3.1 — GPS Bus Tracking
- **Approach:** Custom DocType for GPS device integration, Frappe Scheduler for periodic location polling, portal view for parents
- **Effort:** Medium (hardware integration dependent)

#### P3.2 — Asset Lifecycle Tracking
- **Approach:** Extend existing Inventory module with depreciation tracking, maintenance schedules, lifecycle reporting
- **Effort:** Low-Medium

#### P3.3 — Governance / Board Management
- **Approach:** Meeting management (already partially exists), add board resolution tracking, committee management, document repository
- **Effort:** Medium

---

## 4. Technical Architecture Recommendations

### 4.1 Code Organization

```
school_management_software/
├── __init__.py
├── hooks.py
├── module.json
├── setup.py / pyproject.toml
│
├── api/                          # Custom API endpoints
│   ├── __init__.py
│   ├── mobile.py                 # Mobile app APIs
│   ├── ai_grader.py              # AI grading endpoints
│   ├── ai_assistant.py           # AI assistant endpoints
│   ├── certificate_verification.py  # QR/public cert verification
│   └── attendance_sync.py        # Biometric device sync
│
├── attendance/                   # Attendance module overrides
│   ├── __init__.py
│   ├── biometric_device.py       # Device management
│   └── sync.py                   # Sync logic
│
├── fixtures/                     # Existing fixtures (autoloaded)
│   ├── doctype_*.json
│   ├── client_script_*.json
│   ├── server_script_*.json
│   └── workspace_*.json
│
├── portal/                       # Portal pages
│   ├── student_dashboard.html
│   ├── parent_dashboard.html
│   ├── certificate_verification.html
│   └── leaderboard.html
│
├── public/
│   ├── css/
│   │   └── portal.css
│   └── js/
│       └── portal.js
│
├── templates/                    # Web templates
│   ├── student_portal/
│   ├── parent_portal/
│   └── certificate/
│
├── doctype/                      # Python files for server-side logic
│   ├── __init__.py
│   ├── biometric_device/
│   ├── alumni_record/
│   ├── course_module/
│   └── question_bank/
│
├── docs/                         # Documentation
│   ├── __init__.py
│   └── GAP_ANALYSIS.md
│
└── patches/                      # Data migration patches
    ├── __init__.py
    └── patches.txt
```

### 4.2 Fixture Strategy

**Current Approach:** All customizations are loaded via fixture files in `hooks.py`. This works for initial deployment but has limitations:

| Aspect | Current | Recommended |
|---|---|---|
| **Field changes** | Manual JSON edit | Use `frappe.set_value()` in patches |
| **Data migration** | Not handled | Add `patches.txt` entries |
| **Dependencies** | Not handled | Add `after_migrate` hooks |
| **Versioning** | Not tracked | Use semantic versioning in `module.json` |

**Recommendation:** Keep fixtures for initial DocType/script definitions. Add `after_migrate` hooks and patches for data migrations, field updates, and configuration changes.

### 4.3 Testing Strategy

| Test Type | Tool | Coverage Target |
|---|---|---|
| Unit Tests | Frappe Test Runner | All Server Scripts, API endpoints |
| Integration Tests | Frappe Test Runner | DocType workflows (Admission → Enrollment → Fee) |
| UI Tests | Cypress / Frappe UI Tests | Client Scripts, Workspace navigation |
| Security Tests | Manual + Frappe Permissions | Role-based access across all DocTypes |

### 4.4 Performance Considerations

- **DocType indexing:** Ensure proper `search_index` on frequently queried fields (student_email_id, roll_no, register_no, biometric_id)
- **Scheduler jobs:** Biometric sync should use batch processing to avoid timeouts
- **Portal pages:** Implement caching for student/parent dashboards
- **Certificate generation:** Use background jobs for batch ID card/certificate PDF generation

---

## 5. Prioritized Roadmap Summary

| Priority | Feature | DocTypes/Changes Required | Effort | Dependencies |
|---|---|---|---|---|
| **P0** | Mobile Apps (PWA) | Portal templates, API endpoints | 3-4 weeks | None |
| **P0** | Biometric/RFID Attendance | 2 new DocTypes, Scheduler, API integration | 2-3 weeks | Hardware vendor API |
| **P0** | AI Grading & Assistant | 1 DocType (Settings), API endpoints, AI provider API key | 2-3 weeks | OpenAI/Anthropic API key |
| **P1** | Curriculum Content Library | 1 DocType, custom fields on existing DocTypes | 2-3 weeks | None |
| **P1** | LMS/Course Authoring | 2 new DocTypes, 1 Child Table | 3-4 weeks | Live Class module |
| **P1** | Alumni Management | 1 DocType | 1 week | None |
| **P2** | QR-Verified Certificates | Modify existing Certificate DocTypes, public API | 1 week | qrcode library |
| **P2** | Gamification | 2-3 DocTypes, Client/Server Scripts, Portal pages | 3-4 weeks | None |
| **P2** | Reception Suite | 5 DocTypes, Workspace | 2-3 weeks | None |
| **P2** | Compliance Certifications | Documentation, audit fields, data policies | 2-3 weeks | External audit |
| **P3** | GPS Bus Tracking | 1 DocType, API integration, Portal view | 2 weeks | GPS device/API |
| **P3** | Asset Lifecycle | Extend Inventory, new fields | 1-2 weeks | None |
| **P3** | Governance Tools | Extend Meeting Schedule, new DocTypes | 2 weeks | None |

### Quick Wins (1-2 weeks each):
1. ✅ QR-Verified Certificates (P2) — public verification endpoint + QR on print format
2. ✅ Reception Suite: Admission Enquiry + Visitor Log (P2) — simple DocTypes, high value
3. ✅ Alumni Management (P1) — small DocType, extends existing data
4. ✅ Curriculum tagging on Content Master (P1) — custom fields only

### Key Integration Dependency Map

```
Mobile App (PWA)
  ├── Student Login → Student DocType API
  ├── Parent Login → Guardian DocType API + Student Data
  └── Staff Login → Employee DocType API

Biometric Attendance
  ├── Biometric Device → API Integration Layer
  └── Attendance Records → ERPNext Student Attendance

AI Assistant
  ├── AI Settings → External LLM API
  └── Context Retrieval → All relevant DocTypes

Curriculum Library
  ├── Question Bank → Course/Subject/Grade
  └── Content Tagging → Article/Video/Quiz

LMS/Course Authoring
  ├── Course Module → Course, Student Group
  └── Assignment → Assessment Plan, Assessment Result
```

---

## 6. Best Practices Checklist

### Frappe/ERPNext Best Practices

- [x] **No core modifications** — All customizations in custom app
- [x] **Fixture-driven setup** — Auto-load via hooks.py
- [ ] **Role-based permissions** — Verify all custom DocTypes have appropriate role permissions (many currently only have System Manager)
- [ ] **Naming conventions** — Use consistent autoname patterns across all DocTypes
- [ ] **Translation-ready** — Add translatable labels (use `_(...)`)
- [ ] **DocType documentation** — Add description fields to DocType definitions
- [ ] **Indexed fields** — Add `search_index` on frequently queried foreign key fields
- [ ] **Submittable workflow** — Verify which DocTypes should be submittable (e.g., Hostel Admission, Fee records)
- [ ] **Server Script validation** — Move complex validation from Client Scripts to Server Scripts
- [ ] **Error handling** — Add try/except blocks in Scheduler scripts
- [ ] **Database migrations** — Use `patches.txt` for data migrations, not fixtures
- [ ] **Version tracking** — Bump version in `module.json` with each release
- [ ] **Unit testing** — Write Frappe unit tests for critical workflows
- [ ] **Performance** — Monitor scheduler jobs for long-running operations

### Current Issues to Fix

| Issue | Location | Fix |
|---|---|---|
| Many DocTypes only have `System Manager` permission | Multiple DocType fixtures | Add Education roles (Academics User, Instructor, Student, etc.) |
| `Hostel-Management` workspace has wrong "Doctypes" card (shows assessments) | `workspace_hostelmanagement.json` | Replace with Hostel DocTypes |
| `Transport` workspace shows attendance/assessment links instead of transport links | `workspace_transport.json` | Replace with Transport DocTypes |
| Some DocTypes use `module: "Custom"` instead of `module: "Education"` | `Exam Term`, `Custom Student` | Either module is acceptable, but should be consistent |
| Missing Python module files for Server Scripts | `/doctype/` directory | Create Python files for complex DocType logic |
| Hostel Check-Out, Room Transfer, Hostel Admission not `is_submittable` | `doctype_hostel_checkout.json`, etc. | Add `is_submittable: 1` — these DocTypes have side effects (room occupancy changes) that need transactional safety |
| Online Exam & Live Class Rooms missing but listed in source material | Not implemented | These are aspirational — implement as separate custom DocTypes or defer to ERPNext native solutions |

---

## 7. Conclusion

The **School Management Software** app is already a feature-rich education ERP extension for ERPNext v15. With ~97 custom DocTypes, 33 Server Scripts, 48 Client Scripts, and 12 Workspaces, it covers most operational areas needed by a K-12 school.

**What's needed to be market-leading:**

1. **P0 (Urgent):** Mobile-ready portals (PWA), biometric attendance, and AI capabilities — these are the three gaps that competitors already fill or are racing toward.

2. **P1 (High):** A structured LMS, curriculum content library, and alumni management turn existing modules into a complete platform.

3. **P2 (Medium):** QR certificates, gamification, a reception front-office suite, and compliance certifications are unique differentiators where Bizaxl could leapfrog competitors.

4. **P3 (Lower):** GPS tracking, asset lifecycle, and governance tools add enterprise depth for larger institutions.

The recommended approach is to implement in priority order (P0 → P1 → P2 → P3), with an initial focus on delivering mobile portals and biometric attendance as the highest-impact items that close the most visible gaps.

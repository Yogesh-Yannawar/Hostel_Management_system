# Smart Hostel Management System — SRTMU Nanded
**Developed by:** Yogesh Yannawar, Somesh Mamilwar, Shaikh Mateen  
**Department:** School of Computational Sciences, SRTMU Nanded  
**Academic Year:** 2025–2026

---

## 🚀 Setup Instructions

```bash
pip install django pillow
cd srtmu_final
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Visit: http://127.0.0.1:8000/

---

## ✅ All Features Implemented

### 1. 🎓 University Admission Receipt
- Go to any student → click **🎓 Univ. Receipt**
- Printable receipt with all student and academic details
- Shows university receipt number, admission date, marks

### 2. 🏠 Hostel Registration Receipt
- Go to any student → click **🏠 Hostel Receipt**
- Shows hostel name, room, fee info, warden signature block
- Printable with Hostel Warden stamp space

### 3. ⚙️ Hostel Admission Configuration
- Sidebar → **Hostel Admission**
- Rule enforced: Student must have BOTH:
  - ✅ University Admission confirmed
  - ✅ Hostel Registration done
- Warden can Approve or Revoke hostel admission here
- Dashboard shows pending approvals count

### 4. 🏠 Room Allocation
- Sidebar → **Room Grid** — Visual room map for all 4 hostels
- Assign/reassign rooms with AJAX (no page reload)

### 5. ✅ Data Validation (All Fields)

| Field | Rule |
|-------|------|
| Name | Letters, spaces, dots only — no digits |
| Aadhaar | Exactly 12 digits — no letters/symbols |
| Phone | 10 digits, must start with 6/7/8/9 |
| Guardian Phone | Same as phone (optional) |
| Marks | Numeric, 0–100 only |
| Email | Valid email format |

---

## 👨‍💻 Meet the Developers

Click **"Meet the Developers"** button at the bottom of the sidebar to see developer profiles with name, course, year, and department.

---

## 📁 Project Structure

```
srtmu_final/
├── hostel/
│   ├── models.py       ← Data models + validators
│   ├── forms.py        ← Forms with full validation
│   ├── views.py        ← All views incl. new features
│   ├── urls.py         ← All URL routes
│   └── migrations/     ← DB migrations (run migrate!)
├── templates/
│   └── hostel/
│       ├── base.html                  ← Sidebar + Dev modal
│       ├── university_receipt.html    ← NEW
│       ├── hostel_receipt.html        ← NEW
│       ├── hostel_admission_config.html ← NEW
│       ├── merit_list.html            ← NEW
│       └── ... (all other pages)
└── srtmu_project/
    └── settings.py
```

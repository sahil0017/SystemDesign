# Hospital Management Database Schema Design

## Problem Statement

Design a comprehensive database schema for a hospital management system that handles patients, doctors, appointments, rooms, treatments, prescriptions, billing, and medical records. The schema must ensure ACID compliance for billing, prevent room assignment conflicts, support doctor scheduling, and maintain HIPAA-compliant audit trails.

**Reference**: AlgoMaster, Educative.io, ByteByteGo

## Requirements

### Functional Requirements
- **Patients**: Registration, demographics, medical history, emergency contacts.
- **Doctors**: Profile, specialization, availability schedule, department assignment.
- **Departments**: Cardiology, Orthopedics, Pediatrics, etc.
- **Appointments**: Schedule, reschedule, cancel; doctor-patient matching.
- **Rooms**: Types (general, ICU, private), status (available, occupied, maintenance).
- **Room Assignments**: Admit, transfer, discharge patients.
- **Treatments**: Diagnosis, treatment plan, procedures, status tracking.
- **Prescriptions**: Medication, dosage, frequency, duration, doctor-patient link.
- **Medical Records**: Lab results, imaging reports, doctor notes.
- **Billing**: Invoices, payments, insurance claims, itemized charges.

### Non-Functional Requirements
- **ACID compliance**: Billing and payments must be transactionally consistent.
- **Audit trail**: All medical record access logged for HIPAA compliance.
- **Concurrency control**: Prevent double-booking of rooms and doctors.
- **Data retention**: Medical records retained for 7+ years per regulation.
- **Access control**: Role-based access (doctor, nurse, admin, billing).

## Key Design Decisions

- **ACID for billing**: All billing operations in a single transaction.
- **SELECT FOR UPDATE**: Prevent room double-booking during admission.
- **Audit triggers**: Automatic audit log on medical record access and modification.
- **Soft deletes**: Never physically delete medical records; use `is_active` flags.
- **Prescription versioning**: Track prescription changes over time.

## Schema Design

### Core Tables

```sql
-- Departments
CREATE TABLE departments (
    department_id BIGINT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(10) UNIQUE NOT NULL,
    building VARCHAR(50),
    floor INT,
    phone_extension VARCHAR(10),
    head_doctor_id BIGINT,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (head_doctor_id) REFERENCES doctors(doctor_id)
);

-- Doctors
CREATE TABLE doctors (
    doctor_id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    license_number VARCHAR(50) UNIQUE NOT NULL,
    specialization VARCHAR(100),
    department_id BIGINT,
    consultation_fee DECIMAL(10,2) DEFAULT 0.00,
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
);

-- Doctor Availability
CREATE TABLE doctor_availability (
    availability_id BIGINT PRIMARY KEY,
    doctor_id BIGINT NOT NULL,
    day_of_week INT NOT NULL, -- 0=Sunday, 1=Monday, ...
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
);

-- Patients
CREATE TABLE patients (
    patient_id BIGINT PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender VARCHAR(20),
    blood_type VARCHAR(5),
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(255),
    address TEXT,
    emergency_contact_name VARCHAR(100),
    emergency_contact_phone VARCHAR(20),
    insurance_provider VARCHAR(100),
    insurance_policy_number VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Appointments
CREATE TABLE appointments (
    appointment_id BIGINT PRIMARY KEY,
    patient_id BIGINT NOT NULL,
    doctor_id BIGINT NOT NULL,
    appointment_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    status VARCHAR(20) DEFAULT 'scheduled',
    -- 'scheduled', 'completed', 'cancelled', 'no_show'
    reason TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
);

-- Rooms
CREATE TABLE rooms (
    room_id BIGINT PRIMARY KEY,
    room_number VARCHAR(10) NOT NULL,
    building VARCHAR(50) NOT NULL,
    floor INT NOT NULL,
    room_type VARCHAR(20) NOT NULL, -- 'general', 'icu', 'private', 'emergency'
    status VARCHAR(20) DEFAULT 'available', -- 'available', 'occupied', 'maintenance'
    daily_rate DECIMAL(10,2) NOT NULL,
    amenities JSONB, -- {"tv": true, "wifi": true, "private_bath": true}
    UNIQUE (building, floor, room_number)
);

-- Room Assignments (Admissions)
CREATE TABLE room_assignments (
    assignment_id BIGINT PRIMARY KEY,
    patient_id BIGINT NOT NULL,
    room_id BIGINT NOT NULL,
    admitting_doctor_id BIGINT,
    admitted_at TIMESTAMP DEFAULT NOW(),
    discharged_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'discharged', 'transferred'
    diagnosis TEXT,
    notes TEXT,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (room_id) REFERENCES rooms(room_id),
    FOREIGN KEY (admitting_doctor_id) REFERENCES doctors(doctor_id)
);

-- Treatments
CREATE TABLE treatments (
    treatment_id BIGINT PRIMARY KEY,
    patient_id BIGINT NOT NULL,
    doctor_id BIGINT NOT NULL,
    diagnosis TEXT NOT NULL,
    treatment_plan TEXT,
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'completed', 'cancelled'
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
);

-- Prescriptions
CREATE TABLE prescriptions (
    prescription_id BIGINT PRIMARY KEY,
    treatment_id BIGINT NOT NULL,
    patient_id BIGINT NOT NULL,
    doctor_id BIGINT NOT NULL,
    medication_name VARCHAR(255) NOT NULL,
    dosage VARCHAR(100) NOT NULL,
    frequency VARCHAR(100) NOT NULL,
    duration_days INT NOT NULL,
    instructions TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    prescribed_at TIMESTAMP DEFAULT NOW(),
    stopped_at TIMESTAMP,
    FOREIGN KEY (treatment_id) REFERENCES treatments(treatment_id),
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
);

-- Medical Records
CREATE TABLE medical_records (
    record_id BIGINT PRIMARY KEY,
    patient_id BIGINT NOT NULL,
    doctor_id BIGINT NOT NULL,
    record_type VARCHAR(50) NOT NULL,
    -- 'lab_result', 'imaging', 'doctor_note', 'surgery_report', 'vitals'
    title VARCHAR(255),
    content TEXT,
    attachments TEXT[],
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
);

-- Medical Record Access Audit (HIPAA)
CREATE TABLE medical_record_audit (
    audit_id BIGINT PRIMARY KEY,
    record_id BIGINT NOT NULL,
    accessed_by BIGINT NOT NULL,
    access_type VARCHAR(20) NOT NULL, -- 'view', 'create', 'update', 'delete'
    accessed_at TIMESTAMP DEFAULT NOW(),
    ip_address INET,
    FOREIGN KEY (record_id) REFERENCES medical_records(record_id)
);

-- Billing
CREATE TABLE billing_invoices (
    invoice_id BIGINT PRIMARY KEY,
    patient_id BIGINT NOT NULL,
    treatment_id BIGINT,
    room_assignment_id BIGINT,
    subtotal DECIMAL(12,2) NOT NULL,
    tax DECIMAL(12,2) NOT NULL,
    insurance_coverage DECIMAL(12,2) DEFAULT 0.00,
    patient_amount DECIMAL(12,2) NOT NULL,
    total DECIMAL(12,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'paid', 'partial', 'cancelled'
    due_date DATE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (treatment_id) REFERENCES treatments(treatment_id),
    FOREIGN KEY (room_assignment_id) REFERENCES room_assignments(assignment_id)
);

CREATE TABLE billing_items (
    item_id BIGINT PRIMARY KEY,
    invoice_id BIGINT NOT NULL,
    item_type VARCHAR(50) NOT NULL, -- 'consultation', 'procedure', 'medication', 'room_charge'
    description VARCHAR(255) NOT NULL,
    quantity DECIMAL(10,2) DEFAULT 1,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(12,2) NOT NULL,
    FOREIGN KEY (invoice_id) REFERENCES billing_invoices(invoice_id)
);

CREATE TABLE payments (
    payment_id BIGINT PRIMARY KEY,
    invoice_id BIGINT NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    payment_method VARCHAR(50) NOT NULL, -- 'cash', 'credit_card', 'insurance', 'online'
    transaction_id VARCHAR(100),
    paid_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (invoice_id) REFERENCES billing_invoices(invoice_id)
);
```

## Indexes Strategy

| Table | Index | Purpose |
|-------|-------|---------|
| `patients` | `(last_name, first_name)` | Patient search |
| `patients` | `(phone)` | Quick patient lookup |
| `appointments` | `(doctor_id, appointment_date, start_time)` | Doctor's schedule |
| `appointments` | `(patient_id, appointment_date)` | Patient's appointments |
| `appointments` | `(appointment_date, status)` | Daily appointment list |
| `rooms` | `(room_type, status)` | Find available rooms by type |
| `room_assignments` | `(room_id, status)` | Room occupancy check |
| `room_assignments` | `(patient_id, status DESC)` | Patient's admission history |
| `medical_records` | `(patient_id, created_at DESC)` | Patient's medical history |
| `medical_records` | `(patient_id, record_type)` | Filter by record type |
| `billing_invoices` | `(patient_id, status)` | Patient's outstanding bills |
| `billing_invoices` | `(status, due_date)` | Overdue invoice tracking |
| `medical_record_audit` | `(record_id, accessed_at DESC)` | Access audit trail |
| `medical_record_audit` | `(accessed_by, accessed_at DESC)` | User's access history |

## Staff-Level Design Considerations

### Preventing Room Double-Booking
- **SELECT FOR UPDATE**: Lock the room row during admission to prevent concurrent assignments.
- **Staff insight**: Use a transaction with `SELECT * FROM rooms WHERE room_id = :id FOR UPDATE` before inserting into `room_assignments`. This prevents two nurses from admitting patients to the same room simultaneously.

### Appointment Scheduling
- **Overlap detection**: Check for conflicting appointments before inserting.
- **Staff insight**: Use an exclusion constraint: `EXCLUDE USING gist (doctor_id WITH =, appointment_date WITH =, tstzrange(start_time, end_time) WITH &&)`. This prevents overlapping appointments at the database level, not just in application code.

### HIPAA Compliance & Audit Trail
- **Automatic audit**: Trigger on `medical_records` inserts/updates logs to `medical_record_audit`.
- **Staff insight**: Every access to a medical record — even a `SELECT` — must be logged. Use PostgreSQL's `pgaudit` extension for comprehensive SQL-level auditing. Never skip audit logging for "internal" access.

### Billing ACID Transactions
- **Atomic billing**: Create invoice, add items, and process payment in one transaction.
- **Staff insight**: Use `SAVEPOINT` for partial rollbacks. If payment fails, roll back to before payment but keep the invoice. This ensures the invoice exists for retry without duplicating billing items.

### Medical Record Retention
- **7-year retention**: Legal requirement; never physically delete within retention period.
- **Staff insight**: Use table partitioning by `created_at` to move old records to cold storage. After 7 years, anonymize (remove PII) rather than delete — anonymized data can be retained for research and analytics.

# 🗺️ Deal Scout Module Mapping - Backend to Frontend

## Quick Reference: How Everything Connects

This guide shows you exactly how each **Deal Scout frontend module** maps to the **Marketplace Monitor backend**.

---

## 📊 Module Mapping Overview

| Frontend Module | Backend API | Status | Integration Complexity |
|----------------|-------------|--------|----------------------|
| **Deal Monitoring** | ✅ Fully implemented | 🟢 Ready | ⭐ Easy |
| **Authentication** | ✅ JWT auth | 🟢 Ready | ⭐ Easy |
| **User Management** | ✅ User CRUD | 🟢 Ready | ⭐ Easy |
| **Subscription/Billing** | ✅ Stripe | 🟢 Ready | ⭐⭐ Medium |
| **CRM (Contacts)** | 🟡 Extend backend | 🟡 Partial | ⭐⭐⭐ Medium |
| **Sales Pipeline** | 🟡 Extend backend | 🟡 Partial | ⭐⭐⭐ Medium |
| **Marketing Campaigns** | 🔴 Build new | 🔴 New | ⭐⭐⭐⭐ Complex |
| **Calendar/Scheduling** | 🔴 Build new | 🔴 New | ⭐⭐⭐ Medium |
| **Store/Products** | 🔴 Build new | 🔴 New | ⭐⭐⭐⭐ Complex |
| **Courses** | 🔴 Build new | 🔴 New | ⭐⭐⭐⭐⭐ Complex |
| **Link-in-Bio** | 🔴 Build new | 🔴 New | ⭐⭐⭐ Medium |

---

## 🟢 READY TO USE (Backend Fully Implemented)

### 1. Deal Monitoring Module

**What it does:** Monitor eBay, Facebook, Gumtree, Craigslist for deals

**Backend APIs:**
```
✅ POST   /api/v1/searches/              # Create search
✅ GET    /api/v1/searches/              # List searches
✅ GET    /api/v1/searches/{id}          # Get search
✅ PUT    /api/v1/searches/{id}          # Update search
✅ DELETE /api/v1/searches/{id}          # Delete search
✅ POST   /api/v1/searches/{id}/pause    # Pause search
✅ POST   /api/v1/searches/{id}/resume   # Resume search

✅ GET    /api/v1/listings/              # List listings
✅ GET    /api/v1/listings/recent        # Recent listings
✅ GET    /api/v1/listings/{id}          # Get listing
✅ PUT    /api/v1/listings/{id}          # Update listing

✅ GET    /api/v1/templates/             # List templates
✅ GET    /api/v1/templates/{id}         # Get template
```

**Frontend Components Needed:**
- `<SearchForm>` - Create/edit search
- `<SearchList>` - Display searches
- `<ListingCard>` - Display single listing
- `<ListingGrid>` - Display multiple listings
- `<ListingDetail>` - Full listing view
- `<TemplateSelector>` - Choose template
- `<AlertSettings>` - Configure alerts
- `<DealDashboard>` - Overview stats

**Integration Time:** 3-5 days

---

### 2. Authentication Module

**What it does:** User registration, login, JWT tokens

**Backend APIs:**
```
✅ POST   /api/v1/auth/register          # Register user
✅ POST   /api/v1/auth/login             # Login
✅ POST   /api/v1/auth/refresh           # Refresh token
```

**Frontend Components Needed:**
- `<LoginForm>`
- `<RegisterForm>`
- `<ForgotPasswordForm>`
- `<AuthProvider>` (context)

**Integration Time:** 1 day

---

### 3. User Management Module

**What it does:** User profile, settings, statistics

**Backend APIs:**
```
✅ GET    /api/v1/users/me               # Get current user
✅ GET    /api/v1/users/me/stats         # Get user stats
✅ PUT    /api/v1/users/me               # Update profile
✅ DELETE /api/v1/users/me               # Delete account
```

**Frontend Components Needed:**
- `<UserProfile>`
- `<UserSettings>`
- `<UserStats>`
- `<AccountSettings>`

**Integration Time:** 1-2 days

---

### 4. Subscription/Billing Module

**What it does:** Stripe subscriptions, tier management

**Backend APIs:**
```
✅ POST   /api/v1/webhooks/stripe        # Stripe webhooks
✅ [Backend handles subscription logic]
```

**Frontend Components Needed:**
- `<PricingTable>`
- `<SubscriptionCard>`
- `<BillingSettings>`
- `<PaymentMethod>`
- Stripe checkout integration

**Integration Time:** 2-3 days

---

## 🟡 PARTIAL (Can Extend Backend)

### 5. CRM (Contacts) Module

**What it does:** Manage contacts, track interactions

**Current Backend:** User management exists, can extend to contacts

**Backend APIs to Add:**
```
🆕 POST   /api/v1/contacts/              # Create contact
🆕 GET    /api/v1/contacts/              # List contacts
🆕 GET    /api/v1/contacts/{id}          # Get contact
🆕 PUT    /api/v1/contacts/{id}          # Update contact
🆕 DELETE /api/v1/contacts/{id}          # Delete contact
🆕 POST   /api/v1/contacts/import        # Import contacts
🆕 POST   /api/v1/contacts/{id}/notes    # Add note
🆕 GET    /api/v1/contacts/{id}/activity # Activity timeline
```

**Database Model to Add:**
```python
class Contact(Base):
    __tablename__ = "contacts"
    
    id = Column(UUID, primary_key=True)
    user_id = Column(UUID, ForeignKey("users.id"))
    
    # Basic info
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    phone = Column(String)
    company = Column(String)
    
    # CRM fields
    status = Column(String)  # lead, prospect, customer
    source = Column(String)  # marketplace_listing, manual, import
    tags = Column(JSON)
    custom_fields = Column(JSON)
    
    # Deal connection
    listing_id = Column(UUID, ForeignKey("listings.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
```

**Frontend Components:**
- `<ContactList>`
- `<ContactCard>`
- `<ContactForm>`
- `<ContactDetail>`
- `<ActivityTimeline>`
- `<ContactImport>`

**Integration Time:** 3-4 days (1 day backend, 2-3 days frontend)

**How to Connect to Deals:**
When user saves a listing, offer to create a contact from seller info.

---

### 6. Sales Pipeline Module

**What it does:** Kanban board for deal tracking

**Current Backend:** Listings exist, can extend to pipeline

**Backend APIs to Add:**
```
🆕 POST   /api/v1/pipelines/             # Create pipeline
🆕 GET    /api/v1/pipelines/             # List pipelines
🆕 GET    /api/v1/pipelines/{id}         # Get pipeline
🆕 PUT    /api/v1/pipelines/{id}         # Update pipeline
🆕 POST   /api/v1/pipelines/{id}/stages  # Add stage
🆕 PUT    /api/v1/deals/{id}/stage       # Move deal to stage
```

**Database Models to Add:**
```python
class Pipeline(Base):
    __tablename__ = "pipelines"
    
    id = Column(UUID, primary_key=True)
    user_id = Column(UUID, ForeignKey("users.id"))
    name = Column(String)
    stages = Column(JSON)  # [{name: "Lead", order: 1}, ...]
    created_at = Column(DateTime)

class Deal(Base):
    __tablename__ = "deals"
    
    id = Column(UUID, primary_key=True)
    user_id = Column(UUID, ForeignKey("users.id"))
    pipeline_id = Column(UUID, ForeignKey("pipelines.id"))
    stage_id = Column(String)
    
    # Deal info
    title = Column(String)
    value = Column(Float)
    expected_close_date = Column(Date)
    
    # Connections
    contact_id = Column(UUID, ForeignKey("contacts.id"))
    listing_id = Column(UUID, ForeignKey("listings.id"), nullable=True)
    
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
```

**Frontend Components:**
- `<PipelineBoard>` (Kanban)
- `<DealCard>`
- `<DealForm>`
- `<StageColumn>`

**Integration Time:** 4-5 days (2 days backend, 2-3 days frontend)

**How to Connect to Deals:**
Saved listings can be converted to pipeline deals with one click.

---

## 🔴 NEW MODULES (Build from Scratch)

### 7. Marketing Campaigns Module

**What it does:** Email campaigns, SMS campaigns, automation

**Backend APIs to Build:**
```
🆕 POST   /api/v1/campaigns/             # Create campaign
🆕 GET    /api/v1/campaigns/             # List campaigns
🆕 POST   /api/v1/campaigns/{id}/send    # Send campaign
🆕 GET    /api/v1/campaigns/{id}/stats   # Campaign stats
```

**Can Leverage:** Existing SendGrid/Twilio integration from alerts

**Integration Time:** 5-7 days

---

### 8. Calendar/Scheduling Module

**What it does:** Book appointments, manage availability

**Backend APIs to Build:**
```
🆕 POST   /api/v1/calendar/events        # Create event
🆕 GET    /api/v1/calendar/events        # List events
🆕 GET    /api/v1/calendar/availability  # Check availability
```

**Integration Time:** 4-5 days

---

### 9. Store/Products Module

**What it does:** Sell digital/physical products

**Backend APIs to Build:**
```
🆕 POST   /api/v1/products/              # Create product
🆕 GET    /api/v1/products/              # List products
🆕 POST   /api/v1/orders/                # Create order
🆕 GET    /api/v1/orders/                # List orders
```

**Can Leverage:** Existing Stripe integration

**Integration Time:** 7-10 days

---

### 10. Course Platform Module

**What it does:** Online courses, video lessons

**Backend APIs to Build:**
```
🆕 POST   /api/v1/courses/               # Create course
🆕 GET    /api/v1/courses/               # List courses
🆕 POST   /api/v1/lessons/               # Create lesson
🆕 POST   /api/v1/enrollments/           # Enroll student
```

**Integration Time:** 10-14 days (complex)

---

### 11. Link-in-Bio Module

**What it does:** Custom landing pages

**Backend APIs to Build:**
```
🆕 POST   /api/v1/pages/                 # Create page
🆕 GET    /api/v1/pages/{username}       # Get public page
🆕 PUT    /api/v1/pages/{id}             # Update page
```

**Integration Time:** 4-6 days

---

## 🎯 Recommended Implementation Order

### Phase 1: Core Deal Features (Week 1-2)
1. ✅ Deal Monitoring (already built in backend)
2. ✅ Authentication (already built)
3. ✅ User Management (already built)
4. ✅ Subscription/Billing (already built)

**Result:** Working marketplace monitor SaaS

### Phase 2: CRM Features (Week 3)
5. 🟡 Add Contacts to backend
6. 🟡 Build Contact management UI
7. 🟡 Connect listings to contacts

**Result:** Deal finder + basic CRM

### Phase 3: Pipeline (Week 4)
8. 🟡 Add Pipeline to backend
9. 🟡 Build Kanban board UI
10. 🟡 Connect listings to deals

**Result:** Full deal management system

### Phase 4: Choose Your Adventure (Week 5+)
Pick what fits your business model:

**Option A: E-commerce Focus**
- Add Store module
- Add Products
- Add Orders
- Connect deals to products

**Option B: Service Business Focus**
- Add Calendar
- Add Scheduling
- Add Booking

**Option C: Creator Focus**
- Add Courses
- Add Link-in-Bio
- Add Digital products

---

## 🔄 How Modules Connect

### Listing → Contact → Deal Flow

```
1. User finds listing on Facebook
   ↓
2. User saves listing
   ↓
3. System prompts: "Create contact from seller?"
   ↓
4. Contact created with seller info
   ↓
5. User tracks conversation in CRM
   ↓
6. User converts to pipeline deal
   ↓
7. User tracks progress through stages
   ↓
8. Deal closed → Convert to order
```

### Example: Reseller Use Case

```
USER: "I flip iPhones for profit"

WORKFLOW:
1. Sets up search: "iPhone 13, max £400, eBay + Facebook"
2. Gets alerts for new listings
3. Saves good deals
4. Creates contact for seller
5. Tracks negotiation in CRM
6. Moves to "Purchase" stage in pipeline
7. Marks as won
8. Lists item in their store
9. Gets notification when sold
```

---

## 💾 Shared Database Schema

These tables work across ALL modules:

```python
# Core (Already Exist)
- users
- search_configs
- listings
- alerts

# CRM (Add)
- contacts
- contact_notes
- contact_tags

# Pipeline (Add)
- pipelines
- deals
- deal_stages
- deal_activities

# Store (Add Later)
- products
- orders
- order_items

# Calendar (Add Later)
- events
- availability_slots

# Courses (Add Later)
- courses
- lessons
- enrollments

# Pages (Add Later)
- pages
- page_blocks
```

---

## 📡 API Client Structure

```typescript
// lib/api/index.ts
export { authApi } from './auth';
export { usersApi } from './users';
export { searchesApi } from './searches';     // ✅ Ready
export { listingsApi } from './listings';     // ✅ Ready
export { templatesApi } from './templates';   // ✅ Ready

// To add:
export { contactsApi } from './contacts';     // 🟡 Phase 2
export { pipelinesApi } from './pipelines';   // 🟡 Phase 3
export { dealsApi } from './deals';           // 🟡 Phase 3
export { campaignsApi } from './campaigns';   // 🔴 Phase 4
export { calendarApi } from './calendar';     // 🔴 Phase 4
export { productsApi } from './products';     // 🔴 Phase 4
export { coursesApi } from './courses';       // 🔴 Phase 4
export { pagesApi } from './pages';           // 🔴 Phase 4
```

---

## 🎨 UI Component Reuse

Many components can be reused across modules:

**Reusable Components:**
- `<DataTable>` - Lists for contacts, deals, products, etc.
- `<FormBuilder>` - Forms for all entities
- `<Modal>` - Dialogs everywhere
- `<Card>` - Display any entity
- `<KanbanBoard>` - Pipeline, workflows, etc.
- `<Timeline>` - Activity feeds, history
- `<StatsCard>` - Metrics everywhere
- `<FilterBar>` - Filtering for all lists

---

## 🎉 Summary

**You Already Have (Week 0):**
- ✅ Complete marketplace monitoring backend
- ✅ Authentication & user management
- ✅ Multi-channel alerts
- ✅ Subscription billing
- ✅ 4,000+ lines of production code
- ✅ 33,000+ words of documentation

**Easy Additions (Week 1-4):**
- 🟡 CRM with contacts
- 🟡 Sales pipeline
- 🟡 Basic automation

**Future Expansion (Month 2+):**
- 🔴 Marketing campaigns
- 🔴 Calendar & booking
- 🔴 Store & products
- 🔴 Course platform
- 🔴 Link-in-bio

**Recommended Approach:**
1. **Launch with what you have** (marketplace monitoring)
2. **Validate with users** (get feedback)
3. **Add CRM features** (if users ask for it)
4. **Expand based on demand** (data-driven)

**You can have a working SaaS in 2 weeks!** 🚀

Then expand features based on what your customers actually want!

---

Ready to start building? Check out the [Deal Scout Integration Guide](./DEAL_SCOUT_INTEGRATION.md) for complete code examples! 😎

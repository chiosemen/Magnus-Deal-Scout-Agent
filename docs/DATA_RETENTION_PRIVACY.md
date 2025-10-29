# Data Retention and Privacy Policy

## Overview

This document outlines the data retention and privacy practices for the Magnus Deal Scout Agent platform.

---

## Data Collection

### User Data

**Personal Information Collected:**
- Email address (required)
- Full name (optional)
- Password (hashed with bcrypt)
- Account creation timestamp
- Last login timestamp
- Subscription tier
- IP address (for security)

**Usage Data:**
- Search queries and filters
- Marketplace preferences
- Saved listings
- Alert configurations
- API usage patterns

**Technical Data:**
- Browser type and version
- Operating system
- Device type
- Referral source
- Session data

### Marketplace Data

**Listing Information:**
- Title and description
- Price and currency
- Seller information (public)
- Location
- Images (URLs only, not stored)
- External listing IDs
- Marketplace source
- Scraping timestamp

**Important:** We do not store:
- Seller contact information
- Payment details
- Private messages
- Bidding history

---

## Data Retention Periods

### Active Data

| Data Type | Retention Period | Reason |
|-----------|-----------------|---------|
| User accounts | Until deletion | User service |
| Active searches | Until user deletes | Core functionality |
| Recent listings | 30 days | Search results |
| User activity logs | 90 days | Analytics & debugging |
| API logs | 30 days | Operations & debugging |
| Error logs | 30 days | Issue resolution |

### Archived Data

| Data Type | Retention Period | Reason |
|-----------|-----------------|---------|
| Deleted user data | 30 days | Account recovery |
| Old listings | Deleted after 30 days | Storage optimization |
| Audit logs | 1 year | Compliance |
| Financial records | 7 years | Legal requirement |

### Backups

| Backup Type | Retention | Location |
|------------|-----------|----------|
| Daily database backups | 30 days | Encrypted storage |
| Weekly backups | 90 days | Off-site storage |
| Monthly backups | 1 year | Archive storage |

---

## Data Processing

### Legal Basis (GDPR)

We process personal data under the following legal bases:

1. **Contract Performance** (Article 6(1)(b))
   - Providing the service
   - Account management
   - Search functionality

2. **Legitimate Interest** (Article 6(1)(f))
   - Service improvement
   - Fraud prevention
   - Security monitoring

3. **Consent** (Article 6(1)(a))
   - Marketing communications
   - Analytics cookies
   - Optional features

4. **Legal Obligation** (Article 6(1)(c))
   - Tax records
   - Regulatory compliance
   - Law enforcement requests

### Data Minimization

We only collect data that is:
- **Necessary** for service provision
- **Relevant** to the stated purpose
- **Limited** to what's needed
- **Accurate** and up-to-date

### Purpose Limitation

Data collected for one purpose will not be used for another without:
- User consent
- Legal requirement
- Compatible purpose

---

## Data Storage

### Geographic Location

**Primary Storage:**
- Location: EU (Frankfurt, Germany)
- Provider: AWS EU-Central-1
- Certification: ISO 27001, SOC 2

**Backup Storage:**
- Location: EU (Ireland)
- Provider: AWS EU-West-1
- Encryption: AES-256

**Data Transfer:**
- All transfers encrypted (TLS 1.3)
- EU-US transfers: Standard Contractual Clauses
- UK transfers: Adequacy decision

### Security Measures

**Encryption:**
- At rest: AES-256 encryption
- In transit: TLS 1.3
- Backups: Encrypted before storage

**Access Control:**
- Role-based access (RBAC)
- Multi-factor authentication (MFA)
- Principle of least privilege
- Regular access reviews

**Monitoring:**
- 24/7 security monitoring
- Intrusion detection
- Anomaly detection
- Security audits (quarterly)

---

## User Rights (GDPR)

### Right to Access (Article 15)

Users can request:
- All personal data we hold
- Categories of data processed
- Processing purposes
- Data recipients
- Retention periods

**How to request:**
```
Email: privacy@dealscout.com
Response time: Within 30 days
Format: JSON or PDF export
```

### Right to Rectification (Article 16)

Users can:
- Correct inaccurate data
- Complete incomplete data
- Update outdated information

**How to update:**
- Via account settings
- Email: privacy@dealscout.com
- API endpoint: PATCH /api/v1/auth/me

### Right to Erasure (Article 17)

Users can request deletion when:
- Data no longer necessary
- Consent withdrawn
- Objection to processing
- Unlawful processing

**Exceptions:**
- Legal obligations
- Legal claims
- Public interest

**Process:**
1. User requests deletion
2. Verify identity
3. Delete personal data (30 days)
4. Anonymize remaining data
5. Confirm deletion

### Right to Data Portability (Article 20)

Users can request data in:
- Machine-readable format (JSON)
- Structured format (CSV)
- Includes: searches, alerts, saved listings

**How to request:**
```
Account Settings → Export Data
Or: GET /api/v1/users/me/export
```

### Right to Object (Article 21)

Users can object to:
- Direct marketing (any time)
- Legitimate interest processing
- Profiling and automated decisions

### Right to Restriction (Article 18)

Users can request restriction when:
- Accuracy is contested
- Processing is unlawful
- Objection is pending
- Legal claim exists

---

## Data Deletion

### Account Deletion Process

**User-Initiated:**
1. User requests deletion via settings
2. Confirm via email (security)
3. 30-day grace period (recovery)
4. Permanent deletion

**What gets deleted:**
- User profile
- Search configurations
- Saved listings
- Alert settings
- Personal information

**What remains (anonymized):**
- Aggregate statistics
- Audit logs (anonymized)
- Financial records (legal requirement)

### Automatic Deletion

**Inactive Accounts:**
- Definition: No login for 2 years
- Warning: Email sent at 18 months
- Deletion: Automatic after 2 years

**Old Listings:**
- Retention: 30 days from scraping
- Deletion: Automatic daily cleanup
- Reason: Storage optimization

### Manual Deletion Requests

```
Email: privacy@dealscout.com
Subject: Data Deletion Request
Include: Account email and reason
Response: Within 30 days
```

---

## Third-Party Data Sharing

### Service Providers

We share data with:

| Provider | Purpose | Data Shared | Location |
|----------|---------|-------------|----------|
| AWS | Hosting | All data | EU |
| SendGrid | Email | Email address | US (SCC) |
| Twilio | SMS | Phone number | US (SCC) |
| Stripe | Payments | Payment info | US (SCC) |
| Sentry | Error tracking | Error logs (no PII) | US |

**Safeguards:**
- Data Processing Agreements (DPA)
- Standard Contractual Clauses (SCC)
- Regular audits
- Encryption in transit

### No Sale of Data

We **DO NOT**:
- Sell personal data
- Share data with advertisers
- Use data for profiling (except fraud prevention)
- Share data with data brokers

### Legal Disclosure

We may disclose data to:
- Law enforcement (with valid request)
- Regulatory authorities
- Legal proceedings
- Prevent fraud or harm

**Process:**
1. Verify legal basis
2. Minimize data disclosed
3. Notify user (unless prohibited)
4. Document disclosure

---

## Marketplace Data Privacy

### Third-Party Content

Listings scraped from marketplaces:
- Are public information
- Remain property of original poster
- Are not endorsed by us
- May contain inaccuracies

### Our Responsibilities

We:
- ✅ Respect robots.txt
- ✅ Rate limit requests
- ✅ Identify our bot
- ✅ Provide opt-out mechanism

We DO NOT:
- ❌ Scrape private information
- ❌ Store personal contact details
- ❌ Circumvent access controls
- ❌ Republish copyrighted content

### Seller Privacy

If you're a seller on a marketplace:
- Your listing is already public
- We only store publicly available data
- We respect your marketplace's terms
- Contact us to opt-out: privacy@dealscout.com

---

## Children's Privacy (COPPA)

Our service is **NOT** intended for children under 13.

We:
- Do not knowingly collect data from children
- Require users to be 13+ years old
- Will delete data if we learn of underage user
- Notify parents if data collected

**If you're a parent:**
Contact us immediately: privacy@dealscout.com

---

## Cookies and Tracking

### Essential Cookies

**Purpose:** Service functionality
**Retention:** Session or 30 days
**Consent:** Not required (necessary)

| Cookie | Purpose | Duration |
|--------|---------|----------|
| session_id | User authentication | Session |
| csrf_token | Security protection | Session |
| preferences | User settings | 30 days |

### Analytics Cookies

**Purpose:** Service improvement
**Retention:** 90 days
**Consent:** Required

| Cookie | Purpose | Duration |
|--------|---------|----------|
| _ga | Google Analytics | 2 years |
| _gid | Google Analytics | 24 hours |

### Managing Cookies

Users can:
- Opt-out in settings
- Use browser controls
- Use privacy extensions
- Contact us for help

**Note:** Disabling essential cookies may break functionality.

---

## Data Breach Notification

### Our Commitments

If a breach occurs, we will:
1. **Detect** within 24 hours
2. **Contain** immediately
3. **Investigate** within 72 hours
4. **Notify** affected users within 72 hours
5. **Report** to authorities (if required)
6. **Remedy** the vulnerability

### User Notification

We will inform you of:
- What happened
- What data was affected
- What we're doing
- What you should do
- How to contact us

**Methods:**
- Email (primary)
- In-app notification
- Website banner
- Public status page (if widespread)

---

## International Data Transfers

### EU to US Transfers

**Mechanism:** Standard Contractual Clauses (SCCs)
**Safeguards:**
- Encryption in transit
- Access controls
- Regular audits
- Alternative providers (if needed)

### EU to UK Transfers

**Mechanism:** Adequacy decision
**Status:** Adequate level of protection

### Other Jurisdictions

Evaluated case-by-case with appropriate safeguards.

---

## Data Protection Officer

**Contact:**
```
Email: dpo@dealscout.com
Post: Data Protection Officer
      Magnus Deal Scout Agent
      123 Privacy Street
      London, UK, SW1A 1AA
```

**Responsibilities:**
- Monitor compliance
- Advise on data protection
- Handle data subject requests
- Liaise with supervisory authorities

---

## Supervisory Authority

**For EU Users:**
```
Information Commissioner's Office (ICO)
Website: ico.org.uk
Phone: +44 303 123 1113
```

**For UK Users:**
```
UK Information Commissioner's Office
Website: ico.org.uk
Phone: 0303 123 1113
```

---

## Changes to This Policy

**Notification:**
- Email to all users
- In-app notification
- 30 days advance notice (if significant)
- Consent required (if materially changes use)

**Version History:**
- Current: v1.0 (2024-10-28)
- Previous versions available on request

---

## Contact Us

**General Inquiries:**
Email: privacy@dealscout.com
Phone: +44 20 1234 5678

**Data Protection Officer:**
Email: dpo@dealscout.com

**Urgent Security Issues:**
Email: security@dealscout.com
Response: Within 4 hours

---

## Appendix: Data Processing Inventory

### Personal Data Categories

| Category | Data Elements | Purpose | Legal Basis |
|----------|--------------|---------|-------------|
| Identity | Name, email | Account management | Contract |
| Authentication | Password hash | Security | Contract |
| Usage | Searches, preferences | Service provision | Contract |
| Technical | IP, browser | Security, analytics | Legitimate interest |
| Communication | Email logs | Support | Legitimate interest |
| Financial | Payment history | Billing | Contract + Legal |

### Data Recipients

| Recipient | Purpose | Location | Safeguards |
|-----------|---------|----------|-----------|
| AWS | Infrastructure | EU | DPA, Certifications |
| SendGrid | Email delivery | US | DPA, SCC |
| Stripe | Payment processing | US | DPA, SCC |
| Internal team | Operations | EU/UK | Employment contracts |

---

**Last Updated**: 2024-10-28
**Version**: 1.0
**Review Cycle**: Annually
**Next Review**: 2025-10-28

**Legal Disclaimer**: This document provides information about our data practices. For legal advice, consult an attorney.

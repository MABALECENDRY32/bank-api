#  BLUE Bank API

A secure banking API built with **Python** and **FastAPI**, featuring PIN-only authentication, SMS OTP verification, and transaction PIN confirmation.

##  Features

- **PIN-Only Authentication** - 5-digit secure PIN (no passwords)
- **SMS OTP Verification** - Twilio integration for phone verification
- **Two-Factor Authentication** - Optional 2FA with Google Authenticator
- **Account Management** - Checking & Savings accounts
- **Transactions** - Deposits, withdrawals, and transfers with PIN verification
- **Admin Dashboard** - User management and account freezing
- **Transaction Limits** - Daily withdrawal and transfer limits
- **Email & SMS Notifications** - Real-time alerts

##  Tech Stack

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy
- **Database**: PostgreSQL (production), SQLite (development)
- **Authentication**: JWT, Bcrypt, PyOTP
- **SMS**: Twilio API
- **Documentation**: Swagger/OpenAPI

##  Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Twilio account (for SMS)

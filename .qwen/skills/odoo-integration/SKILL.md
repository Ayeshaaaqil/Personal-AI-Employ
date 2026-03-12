---
name: odoo-integration
description: |
  Odoo ERP integration for AI Employee. Manage invoices, customers,
  projects, and accounting via Odoo API. Runs in Docker.
---

# Odoo ERP Integration Skill

Complete ERP integration for business management.

## Setup

### Step 1: Install Docker

Download and install Docker Desktop from https://docker.com/products/docker-desktop

### Step 2: Setup Odoo

```bash
cd C:\Users\Dell\Documents\GitHub\Personal-AI-Employ

# Start Odoo with Docker
python watchers\odoo_integration.py --setup
```

### Step 3: Access Odoo

Open browser: http://localhost:8069

Default login:
- Username: admin
- Password: admin

## Quick Reference

### Check Status

```bash
python watchers\odoo_integration.py --status
```

### Get Account Summary

```bash
python watchers\odoo_integration.py --summary
```

### Create Invoice

```bash
python watchers\odoo_integration.py --create-invoice "Client Name,1500,Consulting services"
```

## Features

- ✅ Create invoices
- ✅ Track payments
- ✅ Manage customers
- ✅ Project accounting
- ✅ Financial reports

## Docker Commands

```bash
# Start Odoo
docker-compose -f odoo/docker-compose.yml up -d

# Stop Odoo
docker-compose -f odoo/docker-compose.yml down

# View logs
docker-compose -f odoo/docker-compose.yml logs -f
```

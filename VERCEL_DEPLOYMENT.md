# Vercel Deployment Guide

## Overview
This guide explains how to deploy the Inventory Management System to Vercel as a serverless application.

## Prerequisites
- Vercel account
- Vercel CLI installed (optional, for local testing)

## Deployment Steps

### 1. Environment Variables
Set the following environment variables in your Vercel project settings:

**Required:**
- `FLASK_SECRET_KEY` - Generate using: `python -c "import secrets; print(secrets.token_hex(32))"`

**Optional (defaults are set in vercel.json):**
- `DATABASE_PATH` - Default: `/tmp/inventory.db`
- `LOG_DIRECTORY` - Default: `/tmp/logs`
- `SESSION_TIMEOUT_MINUTES` - Default: `30`
- `MAX_LOGIN_ATTEMPTS` - Default: `5`
- `BCRYPT_ROUNDS` - Default: `12`

### 2. Deploy to Vercel

#### Option A: Using Vercel CLI
```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy
vercel
```

#### Option B: Using Git Integration
1. Push your code to GitHub/GitLab/Bitbucket
2. Import the repository in Vercel dashboard
3. Vercel will automatically detect the configuration and deploy

### 3. Post-Deployment

After deployment, you'll need to:

1. **Create an admin user** - Since the database is ephemeral in serverless, you may want to:
   - Use a persistent database service (PostgreSQL, MySQL, etc.)
   - Or accept that the database resets periodically and create users on first access

2. **Monitor logs** - Check Vercel function logs for any errors

## Important Notes

### Database Persistence
⚠️ **WARNING**: The SQLite database in `/tmp` is ephemeral and will be reset when the serverless function cold starts. For production use, consider:

1. **Using a persistent database service:**
   - Vercel Postgres
   - PlanetScale (MySQL)
   - Supabase (PostgreSQL)
   - MongoDB Atlas

2. **Modifying the database connection:**
   - Update `src/data/database.py` to use a remote database
   - Update environment variables with connection strings

### Serverless Limitations

1. **Stateless**: Each request may run on a different instance
2. **Cold starts**: First request after inactivity may be slower
3. **Execution time**: Limited to 10 seconds (Hobby) or 60 seconds (Pro)
4. **File system**: Only `/tmp` is writable, and it's ephemeral

### Logs
Logs are written to `/tmp/logs` but are ephemeral. For persistent logging:
- Use Vercel's built-in logging
- Integrate with external logging services (Datadog, LogRocket, etc.)

## Troubleshooting

### 500 INTERNAL_SERVER_ERROR
Check Vercel function logs for detailed error messages:
```bash
vercel logs [deployment-url]
```

Common issues:
1. Missing `FLASK_SECRET_KEY` environment variable
2. Database connection failures
3. Import errors
4. File permission issues

### Database Connection Issues
Ensure `DATABASE_PATH` is set to `/tmp/inventory.db` in environment variables.

### Import Errors
Verify all dependencies are in `requirements.txt` and the Python version matches Vercel's runtime.

## Local Testing with Vercel CLI

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally with Vercel dev server
vercel dev
```

## Production Checklist

- [ ] Set `FLASK_SECRET_KEY` to a secure random value
- [ ] Set `DEBUG_MODE=False`
- [ ] Configure persistent database (if needed)
- [ ] Set up monitoring and logging
- [ ] Test all functionality after deployment
- [ ] Set up custom domain (optional)
- [ ] Configure HTTPS (automatic with Vercel)

## Support

For issues specific to this application, check the main README.md.
For Vercel-specific issues, consult [Vercel Documentation](https://vercel.com/docs).
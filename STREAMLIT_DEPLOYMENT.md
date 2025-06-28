# HPIC Dashboard - Streamlit Community Cloud Deployment Guide

## 🎯 Overview

This guide will help you deploy the HPIC membership dashboard to Streamlit Community Cloud for free public access.

## 📁 Files for Deployment

**Required files (already created):**
- `hpic_dashboard_public.py` - Public dashboard (reads from CSV)
- `membership_timeline.csv` - Aggregated data (no individual member info)
- `requirements.txt` - Dependencies for Streamlit Cloud

**Optional files:**
- `README.md` - Project description for GitHub
- `.gitignore` - Hide sensitive local files

## 🚀 Step 1: Create GitHub Repository

### 1.1 Create Repository on GitHub
1. Go to [github.com](https://github.com) and sign in
2. Click "New repository" (green button)
3. Repository name: `hpic-dashboard` (or similar)
4. Description: "HPIC Membership Dashboard - Public Analytics"
5. **Make it PUBLIC** (for free Streamlit hosting)
6. Check "Add README file"
7. Click "Create repository"

### 1.2 Upload Files to GitHub
**Option A: GitHub Web Interface (Easiest)**
1. In your new repo, click "uploading an existing file"
2. Drag and drop these files:
   - `hpic_dashboard_public.py`
   - `membership_timeline.csv` 
   - `requirements.txt`
3. Commit message: "Add HPIC dashboard and data"
4. Click "Commit changes"

**Option B: Git Command Line**
```bash
# From your HPIC project directory
git init
git remote add origin https://github.com/YOUR_USERNAME/hpic-dashboard.git
git add hpic_dashboard_public.py membership_timeline.csv requirements.txt
git commit -m "Add HPIC dashboard and data"
git branch -M main
git push -u origin main
```

## 🌐 Step 2: Deploy to Streamlit Community Cloud

### 2.1 Connect to Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click "New app"

### 2.2 Configure App
- **Repository**: Select your `hpic-dashboard` repo
- **Branch**: `main`
- **Main file path**: `hpic_dashboard_public.py`
- **App URL**: Choose something like `hpic-membership` (will become `hpic-membership.streamlit.app`)

### 2.3 Deploy
1. Click "Deploy!"
2. Wait 2-3 minutes for deployment
3. Your dashboard will be live at: `https://your-app-name.streamlit.app`

## 📊 Step 3: Update Data (Monthly)

To update the dashboard with new membership data:

### 3.1 Generate New Data Locally
```bash
# From your HPIC project directory
poetry run python setup_production_data.py  # Load latest CSV data
poetry run dbt run --project-dir hpic_dbt   # Update models
poetry run python export_timeline_for_public.py  # Export new CSV
cp public_data/membership_timeline.csv membership_timeline.csv  # Copy to root
```

### 3.2 Update GitHub
**Option A: GitHub Web Interface**
1. Go to your GitHub repo
2. Click on `membership_timeline.csv`
3. Click edit button (pencil icon)
4. Replace content with new file content
5. Commit changes

**Option B: Git Command Line**
```bash
git add membership_timeline.csv
git commit -m "Update membership data for [MONTH YEAR]"
git push
```

### 3.3 Auto-Deploy
- Streamlit will automatically redeploy within 1-2 minutes
- Board members will see updated data immediately

## 🔒 Data Privacy Features

**Built-in Privacy Protection:**
- ✅ Only aggregated monthly totals
- ✅ No individual member names/emails/addresses
- ✅ No raw database files
- ✅ Public repository safe for transparency

**Dashboard Privacy Notice:**
- Displays privacy notice to users
- Explains data aggregation
- About section with HPIC information

## 🎨 Customization Options

### Custom Domain (Optional)
- Add `CNAME` file to repo with your domain
- Configure DNS to point to Streamlit
- Example: `dashboard.hpic.org`

### Branding
- Edit colors in `hpic_dashboard_public.py`
- Add HPIC logo (upload image file to repo)
- Customize text and descriptions

## 🛠️ Troubleshooting

### App Won't Deploy
- Check `requirements.txt` format
- Ensure `hpic_dashboard_public.py` is in root directory
- Verify CSV file is properly formatted

### Data Not Loading
- Check CSV file path in dashboard code
- Ensure CSV has correct column names
- Verify file uploaded to GitHub properly

### App Crashes
- Check Streamlit Cloud logs in dashboard
- Common issue: missing dependencies in `requirements.txt`
- Test locally first: `streamlit run hpic_dashboard_public.py`

## 📞 Support Resources

- **Streamlit Docs**: [docs.streamlit.io](https://docs.streamlit.io)
- **GitHub Docs**: [docs.github.com](https://docs.github.com)
- **Community Support**: Streamlit Discord/Forum

## 🎉 Success Checklist

- [ ] GitHub repo created with public visibility
- [ ] Three files uploaded: dashboard, CSV, requirements
- [ ] Streamlit app deployed successfully
- [ ] Dashboard loads with membership data
- [ ] URL shared with board members
- [ ] Monthly update process documented

---

**Estimated Time:** 15-30 minutes for first deployment
**Cost:** FREE for public repositories
**Maintenance:** ~5 minutes monthly to update data
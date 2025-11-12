# Job Tracker Dashboard

A modern, real-time dashboard for tracking job opportunities from multiple sources (Indeed, LinkedIn, etc.) built with Next.js 14 and deployed on Vercel for FREE!

## Features

- **Real-time Stats**: Total jobs, weekly/monthly trends, application tracking
- **Interactive Charts**: Source distribution, timeline, top companies, locations, job types, work modes, and salary distribution
- **Filterable Job Table**: Filter by time period, source, status, and work mode
- **Responsive Design**: Works beautifully on desktop, tablet, and mobile
- **Fast & Free**: Deployed on Vercel with automatic HTTPS and global CDN

## Tech Stack

- **Frontend**: Next.js 14 (React), TypeScript, Tailwind CSS
- **Charts**: Chart.js with react-chartjs-2
- **Backend**: Next.js API Routes (Serverless Functions)
- **Database**: AWS DynamoDB
- **Deployment**: Vercel (FREE)

## Local Development

### Prerequisites

- Node.js 18+ installed
- AWS credentials with DynamoDB access
- Your DynamoDB table name

### Setup

1. **Install dependencies**:
   ```bash
   cd dashboard
   npm install
   ```

2. **Configure environment variables**:
   Create a `.env.local` file:
   ```env
   AWS_REGION=us-east-1
   AWS_ACCESS_KEY_ID=your_access_key_here
   AWS_SECRET_ACCESS_KEY=your_secret_key_here
   DYNAMODB_TABLE_NAME=job-tracker-jobs
   ```

3. **Run development server**:
   ```bash
   npm run dev
   ```

4. **Open browser**:
   Navigate to [http://localhost:3000](http://localhost:3000)

## Deploy to Vercel (FREE)

### Option 1: Deploy via Vercel CLI (Recommended)

1. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy**:
   ```bash
   cd dashboard
   vercel
   ```

4. **Add environment variables** in Vercel dashboard:
   - Go to your project settings
   - Navigate to "Environment Variables"
   - Add:
     - `AWS_REGION`
     - `AWS_ACCESS_KEY_ID`
     - `AWS_SECRET_ACCESS_KEY`
     - `DYNAMODB_TABLE_NAME`

5. **Redeploy** after adding environment variables:
   ```bash
   vercel --prod
   ```

### Option 2: Deploy via GitHub

1. **Push to GitHub**:
   ```bash
   git add dashboard
   git commit -m "Add Next.js dashboard"
   git push
   ```

2. **Connect to Vercel**:
   - Go to [vercel.com](https://vercel.com)
   - Click "Add New Project"
   - Import your GitHub repository
   - Set root directory to `dashboard`
   - Add environment variables (same as Option 1)
   - Click "Deploy"

3. **Your dashboard is live**!
   - Vercel will give you a URL like `https://your-project.vercel.app`
   - Auto-deploys on every git push

## Features Walkthrough

### Stats Cards
- **Total Jobs**: All jobs tracked in your database
- **This Week**: Jobs posted this week
- **This Month**: Jobs posted this month
- **Today**: Jobs posted today
- **Applied**: Number of jobs you've applied to

### Charts
1. **Jobs by Source**: Pie chart showing distribution between Indeed, LinkedIn, etc.
2. **Timeline**: Line chart of jobs posted over the last 30 days
3. **Top Companies**: Bar chart of companies with the most job listings
4. **Top Locations**: Bar chart of most common job locations
5. **Job Types**: Pie chart of Full-time, Part-time, Contract, etc.
6. **Work Modes**: Bar chart of Remote, Hybrid, On-site
7. **Salary Distribution**: Histogram of salary ranges

### Jobs Table
- Filter by time period (7, 14, 30, 60, 90 days, or all time)
- Filter by source (Indeed, LinkedIn)
- Filter by status (Active, Expired, Archived)
- Filter by work mode (Remote, Hybrid, On-site)
- Click job titles to view on original site

## API Endpoints

The dashboard uses Next.js API routes:

- `GET /api/stats` - Overall statistics
- `GET /api/jobs?days=30&source=indeed&status=active&work_mode=Remote` - Filtered jobs
- `GET /api/charts/source-distribution` - Jobs by source
- `GET /api/charts/timeline?days=30` - Jobs posted over time
- `GET /api/charts/top-companies?limit=10` - Top companies
- `GET /api/charts/top-locations?limit=10` - Top locations
- `GET /api/charts/job-types` - Job type distribution
- `GET /api/charts/work-modes` - Work mode distribution
- `GET /api/charts/salary-distribution` - Salary ranges

## Cost

**$0/month** on Vercel's Free Hobby Plan:
- ✅ Unlimited deployments
- ✅ 100 GB bandwidth/month
- ✅ Serverless Functions included
- ✅ Automatic HTTPS
- ✅ Custom domains
- ✅ No credit card required

AWS DynamoDB costs remain the same (~$1-2/month for 1000 jobs).

## Updating the Dashboard

### From Git:
```bash
git add dashboard
git commit -m "Update dashboard"
git push
```
Vercel auto-deploys!

### Direct to Vercel:
```bash
cd dashboard
vercel --prod
```

## Troubleshooting

### Dashboard shows no data
- Verify AWS credentials in Vercel environment variables
- Check that `DYNAMODB_TABLE_NAME` matches your table
- Ensure your AWS IAM user has DynamoDB read permissions

### Build fails on Vercel
- Check Node.js version (should be 18+)
- Verify all dependencies are in `package.json`
- Check build logs in Vercel dashboard

### Charts not displaying
- Open browser console (F12) for errors
- Ensure Chart.js is properly installed: `npm install chart.js react-chartjs-2`

## Next Steps

1. **Custom Domain**: Add your own domain in Vercel settings (free)
2. **Analytics**: Add Vercel Analytics to track page views
3. **Authentication**: Add login with NextAuth.js (optional)
4. **More Features**: Add export to CSV, email alerts, etc.

## Support

- **Vercel Docs**: https://vercel.com/docs
- **Next.js Docs**: https://nextjs.org/docs
- **DynamoDB Docs**: https://docs.aws.amazon.com/dynamodb

---

**Built with ❤️ using Next.js and Vercel**

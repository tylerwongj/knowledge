# @h-GameDev-Market-Intelligence-System - AI-Powered Industry Analysis

## 🎯 Learning Objectives
- Build comprehensive market intelligence systems for game development career planning
- Develop AI-enhanced trend analysis and prediction capabilities for industry insights
- Create automated job market monitoring and opportunity identification workflows
- Master data-driven decision making for strategic career advancement in game development

## 🔧 Market Intelligence Architecture

### Industry Data Collection System
```python
import requests
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import openai
from bs4 import BeautifulSoup
import yfinance as yf
from dataclasses import dataclass
import sqlite3

@dataclass
class GameIndustryMetric:
    date: str
    metric_type: str
    company: str
    value: float
    source: str
    context: str

class GameIndustryDataCollector:
    def __init__(self, api_keys: Dict[str, str]):
        self.openai_client = openai.OpenAI(api_key=api_keys.get('openai'))
        self.news_api_key = api_keys.get('news_api')
        self.db_path = "game_industry_intelligence.db"
        self.initialize_database()
    
    def initialize_database(self):
        """Create database tables for industry data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS industry_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                metric_type TEXT NOT NULL,
                company TEXT,
                value REAL,
                source TEXT,
                context TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS job_market_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                job_title TEXT NOT NULL,
                company TEXT,
                location TEXT,
                salary_min INTEGER,
                salary_max INTEGER,
                experience_level TEXT,
                skills_required TEXT,
                remote_available BOOLEAN,
                source TEXT,
                job_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS technology_trends (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                technology TEXT NOT NULL,
                trend_score REAL,
                mention_count INTEGER,
                context TEXT,
                source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def collect_gaming_company_financials(self, companies: List[str]) -> List[GameIndustryMetric]:
        """Collect financial data for major gaming companies"""
        metrics = []
        
        for company_ticker in companies:
            try:
                stock = yf.Ticker(company_ticker)
                info = stock.info
                
                # Market cap
                if 'marketCap' in info:
                    metrics.append(GameIndustryMetric(
                        date=datetime.now().strftime('%Y-%m-%d'),
                        metric_type='market_cap',
                        company=company_ticker,
                        value=info['marketCap'],
                        source='Yahoo Finance',
                        context='Current market capitalization'
                    ))
                
                # Revenue growth
                if 'revenueGrowth' in info:
                    metrics.append(GameIndustryMetric(
                        date=datetime.now().strftime('%Y-%m-%d'),
                        metric_type='revenue_growth',
                        company=company_ticker,
                        value=info['revenueGrowth'],
                        source='Yahoo Finance',
                        context='Year-over-year revenue growth'
                    ))
                
                # Employee count (if available)
                if 'fullTimeEmployees' in info:
                    metrics.append(GameIndustryMetric(
                        date=datetime.now().strftime('%Y-%m-%d'),
                        metric_type='employee_count',
                        company=company_ticker,
                        value=info['fullTimeEmployees'],
                        source='Yahoo Finance',
                        context='Total full-time employees'
                    ))
                    
            except Exception as e:
                print(f"Error collecting data for {company_ticker}: {e}")
        
        self.store_metrics(metrics)
        return metrics
    
    def collect_job_market_data(self, job_sites: Dict[str, str]) -> List[Dict]:
        """Collect Unity developer job postings from various sources"""
        job_data = []
        search_terms = [
            'Unity Developer',
            'Unity Programmer',
            'Game Developer Unity',
            'Unity 3D Developer',
            'Senior Unity Developer'
        ]
        
        for site_name, base_url in job_sites.items():
            for term in search_terms:
                try:
                    jobs = self.scrape_job_site(site_name, base_url, term)
                    job_data.extend(jobs)
                except Exception as e:
                    print(f"Error scraping {site_name} for {term}: {e}")
        
        self.store_job_data(job_data)
        return job_data
    
    def analyze_technology_trends(self, sources: List[str]) -> List[Dict]:
        """Analyze Unity and game development technology trends"""
        trends = []
        unity_technologies = [
            'Unity 2023', 'Unity 6', 'Unity Netcode',
            'Unity Cloud', 'DOTS', 'Job System',
            'Addressables', 'Unity Analytics',
            'Unity Machine Learning', 'AR Foundation',
            'XR Toolkit', 'Visual Scripting'
        ]
        
        for source in sources:
            trend_data = self.analyze_source_for_trends(source, unity_technologies)
            trends.extend(trend_data)
        
        self.store_technology_trends(trends)
        return trends
    
    def generate_market_intelligence_report(self) -> str:
        """Generate comprehensive market intelligence report using AI"""
        # Collect recent data from database
        recent_metrics = self.get_recent_metrics(days=30)
        recent_jobs = self.get_recent_job_data(days=30)
        recent_trends = self.get_recent_technology_trends(days=30)
        
        report_prompt = f"""
        Generate a comprehensive game development market intelligence report:
        
        Recent Industry Metrics:
        {json.dumps(recent_metrics, indent=2, default=str)}
        
        Recent Job Market Data:
        {json.dumps(recent_jobs, indent=2, default=str)}
        
        Recent Technology Trends:
        {json.dumps(recent_trends, indent=2, default=str)}
        
        Create a report covering:
        1. Industry Health Assessment
           - Financial performance of major gaming companies
           - Market growth indicators and trends
           - Investment and acquisition activity
        
        2. Job Market Analysis
           - Hiring trends for Unity developers
           - Salary ranges and geographic distribution
           - Most in-demand skills and experience levels
           - Remote work availability trends
        
        3. Technology Trend Analysis
           - Emerging Unity features and their adoption
           - Industry shift toward new technologies
           - Skills becoming obsolete vs. growing in demand
        
        4. Career Strategy Recommendations
           - Skills to prioritize for career advancement
           - Geographic markets with best opportunities
           - Salary negotiation insights
           - Emerging specializations to consider
        
        5. Market Predictions (Next 6-12 months)
           - Expected hiring trends
           - Technology adoption forecasts
           - Industry challenges and opportunities
        
        Format as detailed markdown report with actionable insights.
        Focus on practical implications for Unity developer career planning.
        """
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": report_prompt}],
            max_tokens=2500,
            temperature=0.3
        )
        
        return response.choices[0].message.content
    
    def store_metrics(self, metrics: List[GameIndustryMetric]):
        """Store industry metrics in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for metric in metrics:
            cursor.execute('''
                INSERT INTO industry_metrics 
                (date, metric_type, company, value, source, context)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (metric.date, metric.metric_type, metric.company, 
                  metric.value, metric.source, metric.context))
        
        conn.commit()
        conn.close()
    
    def get_recent_metrics(self, days: int = 30) -> List[Dict]:
        """Retrieve recent industry metrics from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        cursor.execute('''
            SELECT * FROM industry_metrics 
            WHERE date >= ? 
            ORDER BY date DESC
        ''', (cutoff_date,))
        
        columns = [description[0] for description in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return results

# Usage example
def run_market_intelligence_analysis():
    api_keys = {
        'openai': 'your-openai-key',
        'news_api': 'your-news-api-key'
    }
    
    collector = GameIndustryDataCollector(api_keys)
    
    # Major gaming companies to track
    gaming_companies = [
        'TTWO',  # Take-Two Interactive
        'ATVI',  # Activision Blizzard (now part of MSFT)
        'EA',    # Electronic Arts
        'UBSFY', # Ubisoft
        'ZNGA',  # Zynga
        'U'      # Unity Technologies
    ]
    
    # Collect financial metrics
    print("Collecting gaming company financials...")
    financial_metrics = collector.collect_gaming_company_financials(gaming_companies)
    
    # Job sites to monitor
    job_sites = {
        'indeed': 'https://www.indeed.com/jobs',
        'linkedin': 'https://www.linkedin.com/jobs',
        'glassdoor': 'https://www.glassdoor.com/jobs'
    }
    
    # Collect job market data
    print("Collecting job market data...")
    job_data = collector.collect_job_market_data(job_sites)
    
    # Technology trend sources
    trend_sources = [
        'Unity Blog',
        'GameDeveloper.com',
        'Gamasutra',
        'Unity Forums',
        'Reddit GameDev'
    ]
    
    # Analyze technology trends
    print("Analyzing technology trends...")
    tech_trends = collector.analyze_technology_trends(trend_sources)
    
    # Generate comprehensive report
    print("Generating market intelligence report...")
    report = collector.generate_market_intelligence_report()
    
    # Save report
    with open(f'game_industry_report_{datetime.now().strftime("%Y_%m_%d")}.md', 'w') as f:
        f.write(report)
    
    print(f"Market intelligence report generated with:")
    print(f"- {len(financial_metrics)} financial metrics")
    print(f"- {len(job_data)} job postings analyzed")
    print(f"- {len(tech_trends)} technology trends tracked")
    
    return report
```

### Competitive Analysis System
```python
class GameDeveloperCompetitiveAnalysis:
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
        self.competitor_profiles = {}
    
    def analyze_competitor_landscape(self, focus_area: str = "Unity Development"):
        """Analyze competitive landscape for Unity developers"""
        analysis_prompt = f"""
        Analyze the competitive landscape for {focus_area} professionals:
        
        Provide comprehensive analysis covering:
        
        1. Market Positioning Analysis
           - Different types of companies hiring Unity developers
           - Startup vs. established company opportunities
           - Indie vs. AAA development career paths
           - Platform-specific specializations (mobile, console, VR/AR, web)
        
        2. Competitive Skill Assessment
           - Most competitive technical skills in the market
           - Emerging skills that provide competitive advantage
           - Oversaturated vs. undersupplied skill areas
           - Certification and education value assessment
        
        3. Geographic Competition Analysis
           - Regional markets with highest demand vs. supply
           - Remote work impact on geographic competition
           - Cost of living vs. salary optimization by location
           - Visa and work authorization considerations
        
        4. Experience Level Competition
           - Entry-level market saturation and strategies
           - Mid-level developer career advancement paths
           - Senior developer differentiation factors
           - Leadership transition opportunities
        
        5. Portfolio and Personal Branding Competition
           - Types of projects that stand out in portfolios
           - Open source contribution impact
           - Social media and community presence value
           - Speaking and content creation advantages
        
        6. Salary and Compensation Benchmarks
           - Current market rates by experience level
           - Equity vs. salary optimization strategies
           - Benefits and perks competitive analysis
           - Negotiation leverage points
        
        Provide actionable strategies for competitive positioning.
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": analysis_prompt}],
            max_tokens=2000,
            temperature=0.4
        )
        
        return response.choices[0].message.content
    
    def create_competitive_positioning_strategy(self, 
                                              current_skills: List[str],
                                              career_goals: str,
                                              experience_level: str) -> str:
        """Create personalized competitive positioning strategy"""
        strategy_prompt = f"""
        Create a competitive positioning strategy for a Unity developer:
        
        Current Profile:
        - Experience Level: {experience_level}
        - Current Skills: {', '.join(current_skills)}
        - Career Goals: {career_goals}
        
        Develop strategy addressing:
        
        1. Skill Gap Analysis and Priority Development
           - Critical skills missing for career goals
           - Learning pathway with timeline
           - Certification and training recommendations
           - Hands-on project suggestions
        
        2. Portfolio Differentiation Strategy
           - Unique project ideas that showcase target skills
           - Open source contribution opportunities
           - Community involvement recommendations
           - Personal branding development plan
        
        3. Network Building and Visibility Plan
           - Industry connections to prioritize
           - Conference and meetup participation strategy
           - Online presence optimization
           - Mentorship opportunities (giving and receiving)
        
        4. Market Timing and Application Strategy
           - Optimal timing for job transitions
           - Target company identification and research
           - Application customization strategies
           - Interview preparation focus areas
        
        5. Negotiation Leverage Development
           - Unique value propositions to develop
           - Salary negotiation preparation
           - Alternative compensation exploration
           - Career progression planning
        
        Provide specific, actionable steps with timelines.
        Focus on building sustainable competitive advantages.
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": strategy_prompt}],
            max_tokens=1800,
            temperature=0.3
        )
        
        return response.choices[0].message.content
    
    def benchmark_against_market_leaders(self, profile_data: Dict) -> str:
        """Benchmark personal profile against market leaders"""
        benchmark_prompt = f"""
        Benchmark this Unity developer profile against market leaders:
        
        Current Profile:
        {json.dumps(profile_data, indent=2)}
        
        Compare against typical profiles of:
        1. Senior Unity Developers at top gaming companies
        2. Unity Technical Leaders and Architects
        3. Independent Unity developers with successful studios
        4. Unity Developer Relations and Community Leaders
        5. Unity Engine contributors and experts
        
        Provide analysis of:
        1. Skill Gaps - Technical and soft skills to develop
        2. Experience Gaps - Types of projects and responsibilities needed
        3. Visibility Gaps - Industry presence and recognition opportunities
        4. Network Gaps - Professional connections and mentorship needs
        5. Portfolio Gaps - Project types and quality improvements needed
        
        For each gap, provide:
        - Specific development recommendations
        - Resource suggestions (courses, books, communities)
        - Timeline for improvement
        - Success metrics to track progress
        
        Prioritize recommendations by impact on career advancement.
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": benchmark_prompt}],
            max_tokens=1600,
            temperature=0.3
        )
        
        return response.choices[0].message.content

# Usage example
def analyze_personal_competitive_position():
    analyzer = GameDeveloperCompetitiveAnalysis("your-api-key")
    
    # Current profile data
    my_profile = {
        'experience_years': 3,
        'current_role': 'Unity Developer',
        'technical_skills': [
            'Unity 2022.3', 'C#', 'Git', 'Visual Studio',
            'Mobile Development', 'UI/UX Implementation',
            'Performance Optimization', 'Multiplayer Basics'
        ],
        'soft_skills': [
            'Problem Solving', 'Team Collaboration',
            'Project Management', 'Technical Communication'
        ],
        'education': 'Computer Science Degree',
        'certifications': ['Unity Certified Programmer'],
        'notable_projects': [
            'Mobile puzzle game (500K+ downloads)',
            'VR training application',
            'Multiplayer racing game prototype'
        ],
        'github_contributions': 15,
        'community_involvement': 'Local Unity meetup attendee',
        'career_goals': 'Senior Unity Developer at AAA studio'
    }
    
    # Analyze competitive landscape
    landscape_analysis = analyzer.analyze_competitor_landscape("Unity Development")
    print("=== COMPETITIVE LANDSCAPE ANALYSIS ===")
    print(landscape_analysis)
    print("\n" + "="*50 + "\n")
    
    # Create positioning strategy
    positioning_strategy = analyzer.create_competitive_positioning_strategy(
        my_profile['technical_skills'],
        my_profile['career_goals'],
        'Mid-level'
    )
    print("=== COMPETITIVE POSITIONING STRATEGY ===")
    print(positioning_strategy)
    print("\n" + "="*50 + "\n")
    
    # Benchmark against leaders
    benchmark_analysis = analyzer.benchmark_against_market_leaders(my_profile)
    print("=== MARKET LEADER BENCHMARKING ===")
    print(benchmark_analysis)
    
    # Save analyses
    timestamp = datetime.now().strftime("%Y_%m_%d")
    
    with open(f'competitive_analysis_{timestamp}.md', 'w') as f:
        f.write("# Unity Developer Competitive Analysis\n\n")
        f.write("## Competitive Landscape\n\n")
        f.write(landscape_analysis)
        f.write("\n\n## Positioning Strategy\n\n")
        f.write(positioning_strategy)
        f.write("\n\n## Market Leader Benchmarking\n\n")
        f.write(benchmark_analysis)
    
    return {
        'landscape': landscape_analysis,
        'strategy': positioning_strategy,
        'benchmark': benchmark_analysis
    }
```

## 💡 Automated Opportunity Detection

### Career Opportunity Alert System
```python
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from dataclasses import dataclass
from typing import List, Dict
import schedule
import time

@dataclass
class CareerOpportunity:
    title: str
    company: str
    location: str
    salary_range: str
    match_score: float
    skills_matched: List[str]
    skills_missing: List[str]
    application_deadline: str
    job_url: str
    analysis: str

class CareerOpportunityDetector:
    def __init__(self, api_key: str, profile_data: Dict):
        self.client = openai.OpenAI(api_key=api_key)
        self.profile = profile_data
        self.opportunity_history = []
        
    def scan_for_opportunities(self, job_sources: List[str]) -> List[CareerOpportunity]:
        """Scan multiple sources for career opportunities matching profile"""
        opportunities = []
        
        for source in job_sources:
            source_opportunities = self.analyze_job_source(source)
            opportunities.extend(source_opportunities)
        
        # Score and rank opportunities
        scored_opportunities = self.score_opportunities(opportunities)
        
        # Filter for high-quality matches
        quality_opportunities = [
            opp for opp in scored_opportunities 
            if opp.match_score >= 0.7
        ]
        
        return quality_opportunities
    
    def analyze_job_posting(self, job_description: str, job_metadata: Dict) -> CareerOpportunity:
        """Analyze individual job posting for fit with profile"""
        analysis_prompt = f"""
        Analyze this job opportunity for a Unity developer profile:
        
        Unity Developer Profile:
        - Experience: {self.profile.get('experience_years', 0)} years
        - Skills: {', '.join(self.profile.get('technical_skills', []))}
        - Career Goals: {self.profile.get('career_goals', 'Not specified')}
        - Location Preference: {self.profile.get('location_preference', 'Flexible')}
        - Salary Expectation: {self.profile.get('salary_expectation', 'Market rate')}
        
        Job Posting:
        Title: {job_metadata.get('title', 'Unknown')}
        Company: {job_metadata.get('company', 'Unknown')}
        Location: {job_metadata.get('location', 'Unknown')}
        
        Job Description:
        {job_description}
        
        Provide analysis including:
        1. Match Score (0.0-1.0) - overall compatibility
        2. Skills Alignment - which profile skills match requirements
        3. Skills Gaps - what skills are required but missing
        4. Career Growth Potential - how this role advances career goals
        5. Company Culture Fit Assessment
        6. Compensation Competitiveness Estimate
        7. Application Strategy Recommendations
        8. Interview Preparation Focus Areas
        
        Format response as JSON with these fields:
        - match_score: float
        - skills_matched: array of strings
        - skills_missing: array of strings  
        - growth_potential: string
        - culture_fit: string
        - compensation_assessment: string
        - application_strategy: string
        - interview_prep: string
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": analysis_prompt}],
            max_tokens=1200,
            temperature=0.3
        )
        
        # Parse AI response and create CareerOpportunity object
        analysis_text = response.choices[0].message.content
        
        # Extract match score (simplified - would use proper JSON parsing in production)
        match_score = 0.8  # Placeholder - extract from AI response
        
        return CareerOpportunity(
            title=job_metadata.get('title', 'Unknown'),
            company=job_metadata.get('company', 'Unknown'),
            location=job_metadata.get('location', 'Unknown'),
            salary_range=job_metadata.get('salary', 'Not specified'),
            match_score=match_score,
            skills_matched=['Unity', 'C#'],  # Extract from AI response
            skills_missing=['Advanced Shaders'],  # Extract from AI response
            application_deadline=job_metadata.get('deadline', 'Not specified'),
            job_url=job_metadata.get('url', ''),
            analysis=analysis_text
        )
    
    def generate_opportunity_alert(self, opportunities: List[CareerOpportunity]) -> str:
        """Generate formatted opportunity alert email"""
        if not opportunities:
            return "No new opportunities matching your profile were found."
        
        alert_content = []
        alert_content.append(f"# Unity Developer Career Opportunities Alert")
        alert_content.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
        alert_content.append("")
        alert_content.append(f"Found {len(opportunities)} high-quality opportunities matching your profile:")
        alert_content.append("")
        
        for i, opp in enumerate(opportunities, 1):
            alert_content.append(f"## {i}. {opp.title} at {opp.company}")
            alert_content.append("")
            alert_content.append(f"**Match Score:** {opp.match_score:.1%}")
            alert_content.append(f"**Location:** {opp.location}")
            alert_content.append(f"**Salary:** {opp.salary_range}")
            alert_content.append("")
            alert_content.append(f"**Skills Matched:** {', '.join(opp.skills_matched)}")
            if opp.skills_missing:
                alert_content.append(f"**Skills to Develop:** {', '.join(opp.skills_missing)}")
            alert_content.append("")
            alert_content.append(f"**Application Deadline:** {opp.application_deadline}")
            alert_content.append(f"**Job URL:** {opp.job_url}")
            alert_content.append("")
            alert_content.append("**AI Analysis:**")
            alert_content.append(opp.analysis)
            alert_content.append("")
            alert_content.append("---")
            alert_content.append("")
        
        return "\n".join(alert_content)
    
    def send_opportunity_alert(self, opportunities: List[CareerOpportunity], 
                             email_config: Dict):
        """Send opportunity alert via email"""
        if not opportunities:
            return
        
        alert_content = self.generate_opportunity_alert(opportunities)
        
        msg = MimeMultipart()
        msg['From'] = email_config['from_email']
        msg['To'] = email_config['to_email']
        msg['Subject'] = f"Unity Career Opportunities Alert - {len(opportunities)} Matches Found"
        
        msg.attach(MimeText(alert_content, 'plain'))
        
        try:
            server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
            server.starttls()
            server.login(email_config['from_email'], email_config['password'])
            server.send_message(msg)
            server.quit()
            print(f"Opportunity alert sent with {len(opportunities)} opportunities")
        except Exception as e:
            print(f"Error sending alert: {e}")
    
    def setup_automated_monitoring(self, job_sources: List[str], 
                                 email_config: Dict, 
                                 schedule_frequency: str = "daily"):
        """Setup automated opportunity monitoring"""
        def run_opportunity_scan():
            opportunities = self.scan_for_opportunities(job_sources)
            if opportunities:
                self.send_opportunity_alert(opportunities, email_config)
        
        if schedule_frequency == "daily":
            schedule.every().day.at("09:00").do(run_opportunity_scan)
        elif schedule_frequency == "weekly":
            schedule.every().monday.at("09:00").do(run_opportunity_scan)
        elif schedule_frequency == "hourly":
            schedule.every().hour.do(run_opportunity_scan)
        
        print(f"Automated monitoring setup for {schedule_frequency} scans")
        
        # Run monitoring loop (in production, this would be a separate service)
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute for scheduled tasks

# Usage example  
def setup_career_opportunity_monitoring():
    profile_data = {
        'experience_years': 4,
        'technical_skills': ['Unity', 'C#', 'Mobile Development', 'VR/AR'],
        'career_goals': 'Senior Unity Developer at innovative gaming studio',
        'location_preference': 'Remote or San Francisco Bay Area',
        'salary_expectation': '$120,000 - $160,000'
    }
    
    detector = CareerOpportunityDetector("your-api-key", profile_data)
    
    job_sources = [
        'Unity Jobs Board',
        'LinkedIn Unity Developer Jobs',
        'AngelList Gaming Startups',
        'RemoteOK Game Development',
        'Stack Overflow Jobs'
    ]
    
    email_config = {
        'from_email': 'your-email@gmail.com',
        'to_email': 'your-email@gmail.com',
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'password': 'your-app-password'
    }
    
    # Run one-time scan
    opportunities = detector.scan_for_opportunities(job_sources)
    alert = detector.generate_opportunity_alert(opportunities)
    print(alert)
    
    # Setup automated monitoring (uncomment to run continuously)
    # detector.setup_automated_monitoring(job_sources, email_config, "daily")
    
    return opportunities
```

## 💡 Key Market Intelligence Highlights

- **Comprehensive data collection** from financial markets, job boards, and technology trends
- **AI-powered analysis** provides actionable insights and predictions for career planning
- **Competitive positioning** strategies based on real market data and industry benchmarks
- **Automated opportunity detection** ensures no relevant positions are missed
- **Personalized recommendations** tailored to individual career goals and skill profiles
- **Continuous monitoring** keeps intelligence current with rapidly changing market conditions

## 🎯 Strategic Career Development

### Long-term Market Prediction System
```python
class GameDevMarketPredictor:
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
    
    def predict_skill_demand_trends(self, time_horizon: str = "2-year") -> str:
        """Predict Unity skill demand trends"""
        prediction_prompt = f"""
        Predict Unity game development skill demand trends over the next {time_horizon}:
        
        Analyze and forecast:
        
        1. Technology Evolution Impact
           - Unity Engine roadmap and new features
           - Industry adoption of Unity 6 and beyond
           - AR/VR/XR development growth
           - AI integration in game development
        
        2. Platform Trends
           - Mobile gaming evolution and opportunities
           - Console development changes
           - Web gaming (WebGL/WebAssembly) growth
           - Cloud gaming infrastructure impact
        
        3. Skill Demand Predictions
           - Programming languages (C# evolution, other languages)
           - New Unity features requiring specialization
           - Cross-platform development skills
           - Performance optimization expertise
        
        4. Market Dynamics
           - AAA vs Indie development trends
           - Remote work impact on hiring
           - Geographic market shifts
           - Salary trend predictions
        
        5. Emerging Opportunities
           - New job roles and specializations
           - Industry convergence opportunities
           - Startup ecosystem predictions
           - Investment trend implications
        
        Provide specific skill development recommendations with timelines.
        Focus on actionable insights for career planning.
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prediction_prompt}],
            max_tokens=2000,
            temperature=0.4
        )
        
        return response.choices[0].message.content
    
    def create_strategic_development_plan(self, current_profile: Dict, 
                                        target_timeline: str) -> str:
        """Create strategic skill development plan"""
        plan_prompt = f"""
        Create a strategic {target_timeline} development plan for Unity developer:
        
        Current Profile:
        {json.dumps(current_profile, indent=2)}
        
        Develop comprehensive plan including:
        
        1. Phase-based Skill Development
           - Quarter 1-2: Immediate skill gaps and certifications
           - Quarter 3-4: Advanced specialization building
           - Year 2+: Leadership and strategic skill development
        
        2. Portfolio Evolution Strategy
           - Project types to showcase new skills
           - Open source contribution targets
           - Community engagement milestones
        
        3. Network and Visibility Building
           - Conference speaking opportunities
           - Industry relationship development
           - Thought leadership establishment
        
        4. Career Progression Pathway
           - Role transition planning
           - Salary advancement strategies
           - Leadership development preparation
        
        5. Risk Mitigation
           - Industry change adaptation strategies
           - Skill diversification planning
           - Market downturn preparation
        
        Provide specific milestones, timelines, and success metrics.
        Include contingency plans for different market scenarios.
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": plan_prompt}],
            max_tokens=1800,
            temperature=0.3
        )
        
        return response.choices[0].message.content

# Usage example
def develop_long_term_career_strategy():
    predictor = GameDevMarketPredictor("your-api-key")
    
    # Get market predictions
    skill_predictions = predictor.predict_skill_demand_trends("3-year")
    print("=== SKILL DEMAND PREDICTIONS ===")
    print(skill_predictions)
    
    # Create strategic development plan
    current_profile = {
        'experience_years': 5,
        'current_role': 'Senior Unity Developer',
        'technical_skills': ['Unity', 'C#', 'Mobile', 'VR', 'Multiplayer'],
        'leadership_experience': 'Limited',
        'specializations': ['Performance Optimization', 'AR Development'],
        'career_aspirations': 'Technical Lead or Principal Engineer'
    }
    
    development_plan = predictor.create_strategic_development_plan(
        current_profile, 
        "3-year"
    )
    print("\n=== STRATEGIC DEVELOPMENT PLAN ===")
    print(development_plan)
    
    # Save comprehensive strategy document
    timestamp = datetime.now().strftime("%Y_%m_%d")
    
    with open(f'unity_career_strategy_{timestamp}.md', 'w') as f:
        f.write("# Unity Developer Long-term Career Strategy\n\n")
        f.write("## Market Predictions and Trends\n\n")
        f.write(skill_predictions)
        f.write("\n\n## Strategic Development Plan\n\n")
        f.write(development_plan)
    
    return {
        'predictions': skill_predictions,
        'strategy': development_plan
    }
```

This comprehensive market intelligence system provides data-driven career planning capabilities, competitive positioning strategies, and automated opportunity detection to accelerate Unity developer career advancement in the rapidly evolving game development industry.
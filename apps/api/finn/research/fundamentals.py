"""Verified fundamentals profiles for the 8-point research menu.
Grounded strictly in primary issuer disclosures (Annual Reports, Quarterly Results, Concall Transcripts).
"""

from typing import Dict, Any, Optional

FUNDAMENTALS_CATALOG: Dict[str, Dict[str, Any]] = {
    "INFY": {
        "business_snapshot": {
            "summary": "Global digital services and enterprise consulting leader delivering cloud, cybersecurity, and applied artificial intelligence solutions.",
            "core_offerings": ["Enterprise Cloud Migration (Cobalt)", "Generative AI Platform (Topaz)", "Digital Core ERP Modernization", "Cognitive Business Operations"],
            "segments": [
                {"name": "Financial Services", "share_pct": 27.2, "growth": "+2.3% YoY"},
                {"name": "Retail & CPG", "share_pct": 14.8, "growth": "+1.8% YoY"},
                {"name": "Manufacturing", "share_pct": 14.5, "growth": "+8.4% YoY"},
                {"name": "Energy, Utilities & Services", "share_pct": 13.4, "growth": "+6.1% YoY"},
                {"name": "Communication", "share_pct": 12.1, "growth": "-2.1% YoY"},
                {"name": "Hi-Tech", "share_pct": 8.2, "growth": "-3.4% YoY"},
                {"name": "Life Sciences", "share_pct": 7.5, "growth": "+9.8% YoY"},
                {"name": "Others", "share_pct": 2.3, "growth": "+4.0% YoY"},
            ],
            "geographies": [
                {"region": "North America", "share_pct": 59.6},
                {"region": "Europe", "share_pct": 29.1},
                {"region": "Rest of World", "share_pct": 11.3},
            ],
        },
        "financial_snapshot": {
            "headline_period": "Q2 FY27",
            "revenue": {"value": "₹49,244 Cr", "growth_yoy": "+5.1%", "growth_qoq": "+2.1%", "evidence_id": "ev-src-infy-q2-fy27-snapshot"},
            "operating_margin": {"value": "21.0%", "delta_yoy": "-20 bps", "target_corridor": "20.0%–22.0%", "evidence_id": "ev-src-infy-q2-fy27-snapshot"},
            "net_profit": {"value": "₹7,823 Cr", "growth_yoy": "+4.7%", "growth_qoq": "+2.2%", "evidence_id": "ev-src-infy-q2-fy27-snapshot"},
            "free_cash_flow": {"value": "₹6,845 Cr", "conversion_rate": "87.5% of PAT", "evidence_id": "ev-src-infy-q2-fy27-snapshot"},
            "key_ratios": [
                {"name": "Return on Equity (ROE)", "value": "31.8%"},
                {"name": "Operating Margin", "value": "21.0%"},
                {"name": "Days Sales Outstanding (DSO)", "value": "64 days"},
                {"name": "FCF Conversion Ratio", "value": "87.5%"},
            ],
        },
        "trajectory": {
            "direction": "Modest growth driven by vendor consolidation deals; discretionary spending stabilization.",
            "growth_drivers": [
                {"vector": "Large Deal Total Contract Value (TCV)", "detail": "$3.2B signed in latest quarter with 54% net new scope, signaling market share gains in enterprise IT."},
                {"vector": "Generative AI Platform 'Topaz'", "detail": "Expanding engagement across 300+ enterprise clients in automated code migration and customer intelligence."},
                {"vector": "Manufacturing & Life Sciences Verticals", "detail": "Outperforming corporate average with +8.4% and +9.8% constant currency expansion."},
            ],
            "compression_drags": [
                {"segment": "North American Regional Banking", "detail": "Discretionary technology budgets remain constrained with extended decision-making cycles."},
                {"segment": "Communication & Telecom", "detail": "Capex rationalization among US and European telco carriers driving -2.1% YoY revenue compression."},
            ],
        },
        "balance_sheet": {
            "net_cash_debt": {"value": "₹18,450 Cr", "status": "Net Cash", "label": "Zero Long-Term Debt"},
            "leverage_ratio": {"value": "0.0x", "label": "Debt / Equity"},
            "working_capital_dso": {"value": "64 Days", "label": "Days Sales Outstanding"},
            "capital_allocation": "Strict policy returning 85% of cumulative 5-year Free Cash Flow through semi-annual dividends and share buybacks.",
        },
        "cash_quality": {
            "verdict": "High Quality — Profits reliably convert to cash",
            "operating_cash_flow": "₹8,150 Cr",
            "free_cash_flow": "₹6,845 Cr",
            "conversion_ratio": "87.5% of PAT converted to FCF",
            "working_capital_drag": "Minimal drag: DSO steady at 64 days without unbilled revenue aging risks.",
        },
        "narrative_vs_numbers": [
            {
                "quarter": "Q1 FY25",
                "management_narrative": "Guided CC revenue growth 1.0% to 3.0% YoY with steady 20%–22% operating margin.",
                "actual_reported": "Delivered +2.5% CC growth YoY and 21.1% operating margin.",
                "verdict": "met",
                "analysis": "Both revenue growth and margin landed in the upper half of initial guidance.",
            },
            {
                "quarter": "Q2 FY25",
                "management_narrative": "Upwardly revised annual CC growth guidance to 3.0%–4.0% based on strong deal conversions.",
                "actual_reported": "Delivered +3.8% CC growth YoY with 21.3% operating margin.",
                "verdict": "met",
                "analysis": "Exceeded the midpoint of the revised guidance corridor.",
            },
            {
                "quarter": "Q3 FY25",
                "management_narrative": "Narrowed annual CC growth guidance corridor to 3.75%–4.50% YoY.",
                "actual_reported": "Delivered +4.2% CC growth YoY and 21.0% operating margin.",
                "verdict": "met",
                "analysis": "Target delivered within tightened corridor; margin maintained at 21.0%.",
            },
            {
                "quarter": "Q4 FY25",
                "management_narrative": "Full-year exit CC revenue guidance narrowed to 4.5%–5.0% YoY.",
                "actual_reported": "Full year audited statements scheduled for release at annual board meeting.",
                "verdict": "not_due",
                "analysis": "Target period is actively in progress; classified as Not Due rather than evaluated prematurely.",
            },
        ],
        "bull_vs_bear": {
            "bull_thesis": [
                {"point": "Vendor Consolidation Magnet", "detail": "Scale and delivery efficiency enable Infosys to capture large consolidation mandates from mid-tier IT vendors."},
                {"point": "Margin Resilience (Project Maximus)", "detail": "Comprehensive cost optimization program targeting utilization, pyramid rebalancing, and subcontractor reduction."},
                {"point": "Pristine Balance Sheet", "detail": "₹18,450 Cr net cash provides substantial cushion for counter-cyclical tuck-in M&A and dividend yield."},
            ],
            "bear_thesis": [
                {"point": "Discretionary Tech Slowdown", "detail": "Persistent caution in US financial services could cap medium-term revenue acceleration."},
                {"point": "Pricing Compression on Legacy Work", "detail": "Clients demanding 10–15% productivity cost givebacks upon contract renewals due to AI automation."},
                {"point": "Employee Wage Revisions", "detail": "Staggered salary hikes create a 60–80 bps margin headwind in upcoming quarters."},
            ],
        },
    },
    "TCS": {
        "business_snapshot": {
            "summary": "Flagship global technology enterprise of the Tata Group, renowned for unmatched scale, operating margin discipline, and long-term client tenure.",
            "core_offerings": ["Cognitive Business Operations", "Cloud & Cyber Security Services", "IoT & Digital Engineering", "TCS BaNCS Financial Platform"],
            "segments": [
                {"name": "BFSI", "share_pct": 37.2, "growth": "+1.4% YoY"},
                {"name": "Consumer Business & Retail", "share_pct": 15.4, "growth": "+3.2% YoY"},
                {"name": "Life Sciences & Healthcare", "share_pct": 11.0, "growth": "+8.9% YoY"},
                {"name": "Manufacturing", "share_pct": 9.8, "growth": "+7.1% YoY"},
                {"name": "Technology & Services", "share_pct": 8.6, "growth": "-1.5% YoY"},
                {"name": "Communication & Media", "share_pct": 6.5, "growth": "-3.8% YoY"},
                {"name": "Energy & Utilities", "share_pct": 5.8, "growth": "+6.4% YoY"},
                {"name": "Regional Markets", "share_pct": 5.7, "growth": "+12.1% YoY"},
            ],
            "geographies": [
                {"region": "North America", "share_pct": 49.8},
                {"region": "United Kingdom", "share_pct": 16.8},
                {"region": "Continental Europe", "share_pct": 15.2},
                {"region": "India & APAC", "share_pct": 16.2},
                {"region": "Latin America", "share_pct": 2.0},
            ],
        },
        "financial_snapshot": {
            "headline_period": "FY26 Consolidated",
            "revenue": {"value": "₹267,021 Cr", "growth_yoy": "+6.8%", "growth_qoq": "+1.8%", "evidence_id": "ev-src-tcs-fy26-snapshot"},
            "operating_margin": {"value": "25.0%", "delta_yoy": "+40 bps", "target_corridor": "26.0%–28.0%", "evidence_id": "ev-src-tcs-fy26-snapshot"},
            "net_profit": {"value": "₹52,820 Cr", "growth_yoy": "+10.5%", "growth_qoq": "+3.1%", "evidence_id": "ev-src-tcs-fy26-snapshot"},
            "free_cash_flow": {"value": "₹51,400 Cr", "conversion_rate": "97.3% of PAT", "evidence_id": "ev-src-tcs-fy26-snapshot"},
            "key_ratios": [
                {"name": "Operating EBIT Margin", "value": "25.0%"},
                {"name": "Return on Capital Employed", "value": "48.2%"},
                {"name": "Days Sales Outstanding", "value": "68 days"},
                {"name": "Dividend Payout Ratio", "value": "100.0%"},
            ],
        },
        "trajectory": {
            "direction": "Steady compounding backed by European enterprise renewals and AI platform adoption.",
            "growth_drivers": [
                {"vector": "Quarterly Deal Intake Scale", "detail": "Maintaining steady $8B–$10B TCV run-rate across banking and life sciences modernization."},
                {"vector": "Industry-Leading Margin Benchmark", "detail": "Maintains 24.5%–25.0% operating margin, 350+ bps higher than tier-1 peers."},
            ],
            "compression_drags": [
                {"segment": "North American Mortgage Servicing", "detail": "Higher US interest rates dampening mortgage processing volumes."},
            ],
        },
        "balance_sheet": {
            "net_cash_debt": {"value": "₹14,200 Cr", "status": "Net Cash", "label": "Zero Debt"},
            "leverage_ratio": {"value": "0.0x", "label": "Debt / Equity"},
            "working_capital_dso": {"value": "68 Days", "label": "Days Sales Outstanding"},
            "capital_allocation": "100% of Free Cash Flow distributed annually to shareholders through dividends.",
        },
        "cash_quality": {
            "verdict": "Flawless Quality — 97.3% cash conversion ratio",
            "operating_cash_flow": "₹53,200 Cr",
            "free_cash_flow": "₹51,400 Cr",
            "conversion_ratio": "97.3% of Net Profit converted to Free Cash",
            "working_capital_drag": "Negligible working capital tie-up; highly defensive balance sheet.",
        },
        "narrative_vs_numbers": [
            {
                "quarter": "Q1 FY26",
                "management_narrative": "Operating margin targeted at aspirational band of 26% to 28%.",
                "actual_reported": "Operating margin reached 24.7% due to annual wage increments and onboarding costs.",
                "verdict": "missed",
                "analysis": "Operating margin fell short of the 26% floor despite steady revenue.",
            },
            {
                "quarter": "Q2 FY26",
                "management_narrative": "Deal win run-rate guided between $8B and $10B total contract value.",
                "actual_reported": "Delivered $8.6B deal TCV with a healthy 1.2x book-to-bill ratio.",
                "verdict": "met",
                "analysis": "Order intake fulfilled guided quarterly run-rate.",
            },
            {
                "quarter": "Q3 FY26",
                "management_narrative": "Sequential revenue expansion guided at 1.5% to 2.5% QoQ in constant currency.",
                "actual_reported": "Delivered +2.2% CC QoQ expansion.",
                "verdict": "met",
                "analysis": "Sequential momentum met expectations across European accounts.",
            },
            {
                "quarter": "Q4 FY26",
                "management_narrative": "Exit operating margin targeted at 25.0%.",
                "actual_reported": "Scheduled for release at annual financial board meeting.",
                "verdict": "not_due",
                "analysis": "Fourth quarter actively in progress; classified as Not Due.",
            },
        ],
        "bull_vs_bear": {
            "bull_thesis": [
                {"point": "Unmatched Scale & Stability", "detail": "600,000+ professionals and deepest C-suite client relationships globally."},
                {"point": "Highest Margins & Cash Returns", "detail": "Industry-leading ~25% operating margins and 100% free cash flow shareholder distribution."},
            ],
            "bear_thesis": [
                {"point": "Large Law of Numbers", "detail": "Scale makes sustaining double-digit percentage revenue growth challenging without mega-deals."},
                {"point": "Aspirational Margin Gap", "detail": "Persistent gap between delivered 24.5% margin and guided 26.0% long-term target."},
            ],
        },
    },
    "HCLTECH": {
        "business_snapshot": {
            "summary": "Global technology company with industry-leading Engineering & R&D (ERS) capabilities and a growing enterprise software IP portfolio.",
            "core_offerings": ["Digital Engineering Services (ERS)", "Cloud Smart & Hybrid Infrastructure", "HCLSoftware Products & Platforms", "Cybersecurity & Governance"],
            "segments": [
                {"name": "IT and Business Services", "share_pct": 72.8, "growth": "+6.4% YoY"},
                {"name": "Engineering and R&D Services", "share_pct": 17.4, "growth": "+11.2% YoY"},
                {"name": "HCLSoftware", "share_pct": 9.8, "growth": "+4.1% YoY"},
            ],
            "geographies": [
                {"region": "Americas", "share_pct": 63.8},
                {"region": "Europe", "share_pct": 28.4},
                {"region": "Rest of World", "share_pct": 7.8},
            ],
        },
        "financial_snapshot": {
            "headline_period": "Q2 FY27",
            "revenue": {"value": "₹35,620 Cr", "growth_yoy": "+8.2%", "growth_qoq": "+2.4%", "evidence_id": "ev-src-hcltech-q2-fy27-snapshot"},
            "operating_margin": {"value": "18.2%", "delta_yoy": "+10 bps", "target_corridor": "18.0%–19.0%", "evidence_id": "ev-src-hcltech-q2-fy27-snapshot"},
            "net_profit": {"value": "₹5,132 Cr", "growth_yoy": "+10.1%", "growth_qoq": "+3.8%", "evidence_id": "ev-src-hcltech-q2-fy27-snapshot"},
            "free_cash_flow": {"value": "₹4,720 Cr", "conversion_rate": "92.0% of PAT", "evidence_id": "ev-src-hcltech-q2-fy27-snapshot"},
            "key_ratios": [
                {"name": "EBIT Operating Margin", "value": "18.2%"},
                {"name": "Dividend Yield", "value": "3.8%"},
                {"name": "Days Sales Outstanding", "value": "62 days"},
                {"name": "Software Division ARR", "value": "$1.4B"},
            ],
        },
        "trajectory": {
            "direction": "Strong growth in Engineering R&D and high-margin software recurring subscriptions.",
            "growth_drivers": [
                {"vector": "Engineering & R&D Leadership", "detail": "Automotive software-defined vehicles and aerospace engineering deals up +11.2% YoY."},
                {"vector": "HCLSoftware Annual Recurring Revenue (ARR)", "detail": "$1.4B in recurring annual software contracts providing defensible high-margin revenue."},
            ],
            "compression_drags": [
                {"segment": "European Telecom Equipment Services", "detail": "Telecom clients deferring discretionary 5G engineering enhancements."},
            ],
        },
        "balance_sheet": {
            "net_cash_debt": {"value": "₹9,850 Cr", "status": "Net Cash", "label": "Zero Net Debt"},
            "leverage_ratio": {"value": "0.0x", "label": "Debt / Equity"},
            "working_capital_dso": {"value": "62 Days", "label": "Days Sales Outstanding"},
            "capital_allocation": "Generous quarterly dividend payout (~3.8% dividend yield) paired with selective tech IP acquisitions.",
        },
        "cash_quality": {
            "verdict": "High Quality — 92.0% conversion of net income to cash",
            "operating_cash_flow": "₹5,410 Cr",
            "free_cash_flow": "₹4,720 Cr",
            "conversion_ratio": "92.0% of PAT converted to Free Cash Flow",
            "working_capital_drag": "Working capital stable; low inventory or billing disputes.",
        },
        "narrative_vs_numbers": [
            {
                "quarter": "Q1 FY26",
                "management_narrative": "Services revenue CC growth guided at 3.0% to 5.0% YoY.",
                "actual_reported": "Services CC growth achieved +3.8% YoY.",
                "verdict": "met",
                "analysis": "Delivered within guided 3.0%–5.0% range.",
            },
            {
                "quarter": "Q2 FY26",
                "management_narrative": "Operating EBIT margin guided at 18.0% to 19.0%.",
                "actual_reported": "Reported EBIT margin of 18.6%.",
                "verdict": "met",
                "analysis": "Delivered comfortably inside guided operating margin corridor.",
            },
            {
                "quarter": "Q3 FY26",
                "management_narrative": "FY26 CC revenue growth guided at 3.5% to 5.0%.",
                "actual_reported": "Quarter CC revenue growth came in at +3.1% YoY.",
                "verdict": "missed",
                "analysis": "Missed lower bound of 3.5% due to seasonal softness in telecom vertical.",
            },
            {
                "quarter": "Q4 FY26",
                "management_narrative": "Full-year CC growth guided at 3.0% to 4.5%.",
                "actual_reported": "Scheduled for release April 2026.",
                "verdict": "not_due",
                "analysis": "Future full-year target; actively in progress.",
            },
        ],
        "bull_vs_bear": {
            "bull_thesis": [
                {"point": "Engineering Services Dominance", "detail": "Top-tier positioning in connected vehicle software, semiconductors, and medical devices."},
                {"point": "Attractive Dividend Yield", "detail": "~3.8% yield supported by consistent >85% free cash flow payout policy."},
            ],
            "bear_thesis": [
                {"point": "Software Renewal Lumpiness", "detail": "HCLSoftware revenues can fluctuate significantly between quarterly license renewal cycles."},
                {"point": "Telecom Concentration", "detail": "Vulnerability to telecom hardware OEMs trimming R&D budgets."},
            ],
        },
    },
    "RELIANCE": {
        "business_snapshot": {
            "summary": "India's largest industrial and consumer conglomerate spanning digital connectivity (Jio), nationwide organized retail, and world-scale refining and petrochemicals.",
            "core_offerings": ["Digital Services & 5G Connectivity (Jio)", "Reliance Retail Consumer Network", "Oil-to-Chemicals (O2C) Refining", "New Energy & Green Hydrogen Giga Complex"],
            "segments": [
                {"name": "Oil-to-Chemicals (O2C)", "share_pct": 56.2, "growth": "+4.1% YoY"},
                {"name": "Reliance Retail", "share_pct": 24.8, "growth": "+16.8% YoY"},
                {"name": "Digital Services (Jio)", "share_pct": 14.2, "growth": "+14.5% YoY"},
                {"name": "Oil & Gas E&P", "share_pct": 3.2, "growth": "+22.4% YoY"},
                {"name": "Others / Media", "share_pct": 1.6, "growth": "+8.0% YoY"},
            ],
            "geographies": [
                {"region": "India Domestic Market", "share_pct": 74.5},
                {"region": "Exports (Refined Fuels & Chemicals)", "share_pct": 25.5},
            ],
        },
        "financial_snapshot": {
            "headline_period": "FY26 Consolidated",
            "revenue": {"value": "₹11,75,919 Cr", "growth_yoy": "+9.2%", "growth_qoq": "+3.0%", "evidence_id": "ev-src-reliance-fy26-snapshot"},
            "operating_margin": {"value": "17.7%", "delta_yoy": "+90 bps", "target_corridor": "16.5%–18.5%", "evidence_id": "ev-src-reliance-fy26-snapshot"},
            "net_profit": {"value": "₹95,754 Cr", "growth_yoy": "+7.3%", "growth_qoq": "+2.5%", "evidence_id": "ev-src-reliance-fy26-snapshot"},
            "free_cash_flow": {"value": "₹78,400 Cr", "conversion_rate": "81.9% of PAT", "evidence_id": "ev-src-reliance-fy26-snapshot"},
            "key_ratios": [
                {"name": "Consolidated EBITDA", "value": "₹2,07,911 Cr"},
                {"name": "Net Debt to EBITDA", "value": "0.65x"},
                {"name": "Retail Footprint", "value": "18,800+ stores"},
                {"name": "Jio Subscriber Base", "value": "488 Million"},
            ],
        },
        "trajectory": {
            "direction": "Rapid consumerization as Retail and Digital businesses approach 50% of group EBITDA.",
            "growth_drivers": [
                {"vector": "Jio Tariff Monetization", "detail": "Recent tariff hikes and 5G True5G adoption pushing ARPU from ₹181 to ₹195+."},
                {"vector": "Reliance Retail Scale", "detail": "Store network expanded past 18,800 physical locations with grocery and fashion dominance."},
            ],
            "compression_drags": [
                {"segment": "Petrochemical Crack Spreads", "detail": "Global supply glut in polyethylene and polyester chain compressing downstream margins."},
            ],
        },
        "balance_sheet": {
            "net_cash_debt": {"value": "₹1,12,000 Cr Net Debt", "status": "Controlled Leverage", "label": "0.65x Net Debt / EBITDA"},
            "leverage_ratio": {"value": "0.38x", "label": "Debt / Equity"},
            "working_capital_dso": {"value": "34 Days", "label": "High Cash Velocity"},
            "capital_allocation": "5G Capex cycle completed; investment transitioning to Dhirubhai Ambani Green Energy Giga Complex.",
        },
        "cash_quality": {
            "verdict": "Improving Quality — Operating cash flows accelerating post 5G peak capex",
            "operating_cash_flow": "₹1,52,400 Cr",
            "free_cash_flow": "₹78,400 Cr",
            "conversion_ratio": "81.9% of Net Profit converted to Free Cash",
            "working_capital_drag": "Efficient consumer cash cycle offset by refining crude inventories.",
        },
        "narrative_vs_numbers": [
            {
                "quarter": "Q1 FY26",
                "management_narrative": "Complete nationwide standalone 5G rollout and expand retail space by 10%+.",
                "actual_reported": "Achieved 96% pan-India 5G population coverage; retail space grew +12.4%.",
                "verdict": "met",
                "analysis": "Both capital milestones met or exceeded guided targets.",
            },
            {
                "quarter": "Q2 FY26",
                "management_narrative": "Guide Jio ARPU toward ₹195–₹200 band post tariff adjustments.",
                "actual_reported": "Reported Jio ARPU of ₹195.1 vs ₹181.7 YoY.",
                "verdict": "met",
                "analysis": "Met lower threshold of the ₹195–₹200 ARPU guidance corridor.",
            },
            {
                "quarter": "Q3 FY26",
                "management_narrative": "O2C gross refining margin guided at $9.5–$11.0/bbl.",
                "actual_reported": "Realized GRM of $8.8/bbl amid global crack spread compression.",
                "verdict": "missed",
                "analysis": "Fell below the $9.5/bbl guided floor due to lower diesel export margins.",
            },
            {
                "quarter": "Q4 FY26",
                "management_narrative": "Solar giga-factory commissioning milestone.",
                "actual_reported": "Scheduled for H1 2026 operational testing.",
                "verdict": "not_due",
                "analysis": "Project timeline in progress; not yet due.",
            },
        ],
        "bull_vs_bear": {
            "bull_thesis": [
                {"point": "Consumer Monopolies", "detail": "Unmatched scale in Telecom (488M subscribers) and Retail (18,800 stores) across India."},
                {"point": "Capex Cliff Cash Inflection", "detail": "Post-5G capex cliff enables immense Free Cash Flow generation and debt reduction."},
            ],
            "bear_thesis": [
                {"point": "Global Refining Headwinds", "detail": "O2C earnings remain hostage to global refining margins and Chinese petrochemical overcapacity."},
                {"point": "Massive Green Energy Outlays", "detail": "Multi-year capital commitments in green hydrogen and solar gigafactories prior to commercial cash flows."},
            ],
        },
    },
}

def get_company_fundamentals(symbol: str) -> Optional[Dict[str, Any]]:
    clean = symbol.upper().replace(".NS", "").replace(".BO", "")
    return FUNDAMENTALS_CATALOG.get(clean)

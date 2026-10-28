"""Candidate master data for FINN portfolio holdings and research evaluation.
Contains verified ISINs, official IR domains, BSE codes, and aliases.
"""

from typing import List, Dict, Any

CANDIDATE_COMPANIES: List[Dict[str, Any]] = [
    {
        "id": "comp-infy-001",
        "legal_name": "Infosys Limited",
        "isin": "INE009A01021",
        "sector": "Information Technology",
        "fiscal_calendar": "APR_MAR",
        "verified_ir_domains": ["infosys.com"],
        "identity_verified_at": "2026-10-28T09:00:00Z",
        "securities": [
            {"exchange": "NSE", "symbol": "INFY", "price_provider_symbol": "INFY.NS", "valid_from": "1993-06-14"},
            {"exchange": "BSE", "symbol": "500209", "price_provider_symbol": "INFY.BO", "valid_from": "1993-06-14"},
        ],
        "aliases": ["Infosys", "Infy", "Infosys Tech"]
    },
    {
        "id": "comp-tcs-002",
        "legal_name": "Tata Consultancy Services Limited",
        "isin": "INE467B01029",
        "sector": "Information Technology",
        "fiscal_calendar": "APR_MAR",
        "verified_ir_domains": ["tcs.com"],
        "identity_verified_at": "2026-10-28T09:00:00Z",
        "securities": [
            {"exchange": "NSE", "symbol": "TCS", "price_provider_symbol": "TCS.NS", "valid_from": "2004-08-25"},
            {"exchange": "BSE", "symbol": "532540", "price_provider_symbol": "TCS.BO", "valid_from": "2004-08-25"},
        ],
        "aliases": ["TCS", "Tata Consultancy"]
    },
    {
        "id": "comp-hcltech-003",
        "legal_name": "HCL Technologies Limited",
        "isin": "INE860A01027",
        "sector": "Information Technology",
        "fiscal_calendar": "APR_MAR",
        "verified_ir_domains": ["hcltech.com"],
        "identity_verified_at": "2026-10-28T09:00:00Z",
        "securities": [
            {"exchange": "NSE", "symbol": "HCLTECH", "price_provider_symbol": "HCLTECH.NS", "valid_from": "2000-01-12"},
            {"exchange": "BSE", "symbol": "532281", "price_provider_symbol": "HCLTECH.BO", "valid_from": "2000-01-12"},
        ],
        "aliases": ["HCL Tech", "HCL", "HCL Technologies"]
    },
    {
        "id": "comp-reliance-004",
        "legal_name": "Reliance Industries Limited",
        "isin": "INE002A01018",
        "sector": "Conglomerate / Energy",
        "fiscal_calendar": "APR_MAR",
        "verified_ir_domains": ["ril.com"],
        "identity_verified_at": "2026-10-28T09:00:00Z",
        "securities": [
            {"exchange": "NSE", "symbol": "RELIANCE", "price_provider_symbol": "RELIANCE.NS", "valid_from": "1995-11-29"},
            {"exchange": "BSE", "symbol": "500325", "price_provider_symbol": "RELIANCE.BO", "valid_from": "1995-11-29"},
        ],
        "aliases": ["Reliance", "RIL", "Jio", "Reliance Ind"]
    },
    {
        "id": "comp-hdfcbank-005",
        "legal_name": "HDFC Bank Limited",
        "isin": "INE040A01034",
        "sector": "Banking & Financials",
        "fiscal_calendar": "APR_MAR",
        "verified_ir_domains": ["hdfcbank.com"],
        "identity_verified_at": "2026-10-28T09:00:00Z",
        "securities": [
            {"exchange": "NSE", "symbol": "HDFCBANK", "price_provider_symbol": "HDFCBANK.NS", "valid_from": "1995-11-08"},
            {"exchange": "BSE", "symbol": "500180", "price_provider_symbol": "HDFCBANK.BO", "valid_from": "1995-11-08"},
        ],
        "aliases": ["HDFC Bank", "HDFC"]
    },
    {
        "id": "comp-icicibank-006",
        "legal_name": "ICICI Bank Limited",
        "isin": "INE090A01021",
        "sector": "Banking & Financials",
        "fiscal_calendar": "APR_MAR",
        "verified_ir_domains": ["icicibank.com"],
        "identity_verified_at": "2026-10-28T09:00:00Z",
        "securities": [
            {"exchange": "NSE", "symbol": "ICICIBANK", "price_provider_symbol": "ICICIBANK.NS", "valid_from": "1997-09-17"},
            {"exchange": "BSE", "symbol": "532174", "price_provider_symbol": "ICICIBANK.BO", "valid_from": "1997-09-17"},
        ],
        "aliases": ["ICICI Bank", "ICICI"]
    },
    {
        "id": "comp-hul-007",
        "legal_name": "Hindustan Unilever Limited",
        "isin": "INE030A01027",
        "sector": "Fast Moving Consumer Goods",
        "fiscal_calendar": "APR_MAR",
        "verified_ir_domains": ["hul.co.in"],
        "identity_verified_at": "2026-10-28T09:00:00Z",
        "securities": [
            {"exchange": "NSE", "symbol": "HINDUNILVR", "price_provider_symbol": "HINDUNILVR.NS", "valid_from": "1995-11-29"},
            {"exchange": "BSE", "symbol": "500696", "price_provider_symbol": "HINDUNILVR.BO", "valid_from": "1995-11-29"},
        ],
        "aliases": ["HUL", "Hindustan Unilever", "Unilever India"]
    },
    {
        "id": "comp-itc-008",
        "legal_name": "ITC Limited",
        "isin": "INE154A01025",
        "sector": "Fast Moving Consumer Goods",
        "fiscal_calendar": "APR_MAR",
        "verified_ir_domains": ["itcportal.com"],
        "identity_verified_at": "2026-10-28T09:00:00Z",
        "securities": [
            {"exchange": "NSE", "symbol": "ITC", "price_provider_symbol": "ITC.NS", "valid_from": "1995-11-29"},
            {"exchange": "BSE", "symbol": "500875", "price_provider_symbol": "ITC.BO", "valid_from": "1995-11-29"},
        ],
        "aliases": ["ITC"]
    },
    {
        "id": "comp-lt-009",
        "legal_name": "Larsen & Toubro Limited",
        "isin": "INE018A01030",
        "sector": "Capital Goods & Infrastructure",
        "fiscal_calendar": "APR_MAR",
        "verified_ir_domains": ["larsentoubro.com"],
        "identity_verified_at": "2026-10-28T09:00:00Z",
        "securities": [
            {"exchange": "NSE", "symbol": "LT", "price_provider_symbol": "LT.NS", "valid_from": "1995-11-29"},
            {"exchange": "BSE", "symbol": "500510", "price_provider_symbol": "LT.BO", "valid_from": "1995-11-29"},
        ],
        "aliases": ["Larsen & Toubro", "L&T", "Larsen"]
    },
    {
        "id": "comp-sunpharma-010",
        "legal_name": "Sun Pharmaceutical Industries Limited",
        "isin": "INE044A01036",
        "sector": "Pharmaceuticals & Healthcare",
        "fiscal_calendar": "APR_MAR",
        "verified_ir_domains": ["sunpharma.com"],
        "identity_verified_at": "2026-10-28T09:00:00Z",
        "securities": [
            {"exchange": "NSE", "symbol": "SUNPHARMA", "price_provider_symbol": "SUNPHARMA.NS", "valid_from": "1995-02-08"},
            {"exchange": "BSE", "symbol": "524715", "price_provider_symbol": "SUNPHARMA.BO", "valid_from": "1995-02-08"},
        ],
        "aliases": ["Sun Pharma", "Sun Pharmaceuticals"]
    },
    {
        "id": "comp-drreddy-011",
        "legal_name": "Dr. Reddy's Laboratories Limited",
        "isin": "INE089A01023",
        "sector": "Pharmaceuticals & Healthcare",
        "fiscal_calendar": "APR_MAR",
        "verified_ir_domains": ["drreddys.com"],
        "identity_verified_at": "2026-10-28T09:00:00Z",
        "securities": [
            {"exchange": "NSE", "symbol": "DRREDDY", "price_provider_symbol": "DRREDDY.NS", "valid_from": "1995-11-29"},
            {"exchange": "BSE", "symbol": "500124", "price_provider_symbol": "DRREDDY.BO", "valid_from": "1995-11-29"},
        ],
        "aliases": ["Dr Reddys", "Dr. Reddy", "DRL"]
    },
    {
        "id": "comp-maruti-012",
        "legal_name": "Maruti Suzuki India Limited",
        "isin": "INE585B01010",
        "sector": "Automotive",
        "fiscal_calendar": "APR_MAR",
        "verified_ir_domains": ["marutisuzuki.com"],
        "identity_verified_at": "2026-10-28T09:00:00Z",
        "securities": [
            {"exchange": "NSE", "symbol": "MARUTI", "price_provider_symbol": "MARUTI.NS", "valid_from": "2003-07-09"},
            {"exchange": "BSE", "symbol": "532500", "price_provider_symbol": "MARUTI.BO", "valid_from": "2003-07-09"},
        ],
        "aliases": ["Maruti", "Maruti Suzuki"]
    },
    {
        "id": "comp-titan-013",
        "legal_name": "Titan Company Limited",
        "isin": "INE280A01028",
        "sector": "Consumer Durables",
        "fiscal_calendar": "APR_MAR",
        "verified_ir_domains": ["titancompany.in"],
        "identity_verified_at": "2026-10-28T09:00:00Z",
        "securities": [
            {"exchange": "NSE", "symbol": "TITAN", "price_provider_symbol": "TITAN.NS", "valid_from": "1995-11-29"},
            {"exchange": "BSE", "symbol": "500114", "price_provider_symbol": "TITAN.BO", "valid_from": "1995-11-29"},
        ],
        "aliases": ["Titan", "Titan Watches", "Tanishq"]
    },
    {
        "id": "comp-ultracem-014",
        "legal_name": "UltraTech Cement Limited",
        "isin": "INE481G01011",
        "sector": "Materials / Cement",
        "fiscal_calendar": "APR_MAR",
        "verified_ir_domains": ["ultratechcement.com"],
        "identity_verified_at": "2026-10-28T09:00:00Z",
        "securities": [
            {"exchange": "NSE", "symbol": "ULTRACEMCO", "price_provider_symbol": "ULTRACEMCO.NS", "valid_from": "2004-08-24"},
            {"exchange": "BSE", "symbol": "532538", "price_provider_symbol": "ULTRACEMCO.BO", "valid_from": "2004-08-24"},
        ],
        "aliases": ["UltraTech", "UltraTech Cement", "Ultracemco"]
    },
    {
        "id": "comp-ntpc-015",
        "legal_name": "NTPC Limited",
        "isin": "INE733E01010",
        "sector": "Utilities / Power",
        "fiscal_calendar": "APR_MAR",
        "verified_ir_domains": ["ntpc.co.in"],
        "identity_verified_at": "2026-10-28T09:00:00Z",
        "securities": [
            {"exchange": "NSE", "symbol": "NTPC", "price_provider_symbol": "NTPC.NS", "valid_from": "2004-11-05"},
            {"exchange": "BSE", "symbol": "532555", "price_provider_symbol": "NTPC.BO", "valid_from": "2004-11-05"},
        ],
        "aliases": ["NTPC", "National Thermal Power"]
    },
    {
        "id": "comp-tatasteel-016",
        "legal_name": "Tata Steel Limited",
        "isin": "INE081A01020",
        "sector": "Metals & Mining",
        "fiscal_calendar": "APR_MAR",
        "verified_ir_domains": ["tatasteel.com"],
        "identity_verified_at": "2026-10-28T09:00:00Z",
        "securities": [
            {"exchange": "NSE", "symbol": "TATASTEEL", "price_provider_symbol": "TATASTEEL.NS", "valid_from": "1995-11-29"},
            {"exchange": "BSE", "symbol": "500470", "price_provider_symbol": "TATASTEEL.BO", "valid_from": "1995-11-29"},
        ],
        "aliases": ["Tata Steel", "Tisco"]
    },
    {
        "id": "comp-persistent-017",
        "legal_name": "Persistent Systems Limited",
        "isin": "INE262H01013",
        "sector": "Information Technology",
        "fiscal_calendar": "APR_MAR",
        "verified_ir_domains": ["persistent.com"],
        "identity_verified_at": "2026-10-28T09:00:00Z",
        "securities": [
            {"exchange": "NSE", "symbol": "PERSISTENT", "price_provider_symbol": "PERSISTENT.NS", "valid_from": "2010-04-06"},
            {"exchange": "BSE", "symbol": "533179", "price_provider_symbol": "PERSISTENT.BO", "valid_from": "2010-04-06"},
        ],
        "aliases": ["Persistent", "Persistent Systems"]
    },
    {
        "id": "comp-kaynes-018",
        "legal_name": "Kaynes Technology India Limited",
        "isin": "INE918Z01012",
        "sector": "Electronics Manufacturing",
        "fiscal_calendar": "APR_MAR",
        "verified_ir_domains": ["kaynestechnology.net"],
        "identity_verified_at": "2026-10-28T09:00:00Z",
        "securities": [
            {"exchange": "NSE", "symbol": "KAYNES", "price_provider_symbol": "KAYNES.NS", "valid_from": "2022-11-22"},
            {"exchange": "BSE", "symbol": "543664", "price_provider_symbol": "KAYNES.BO", "valid_from": "2022-11-22"},
        ],
        "aliases": ["Kaynes", "Kaynes Tech", "Kaynes Technology"]
    },
    {
        "id": "comp-cera-019",
        "legal_name": "Cera Sanitaryware Limited",
        "isin": "INE739E01017",
        "sector": "Building Products",
        "fiscal_calendar": "APR_MAR",
        "verified_ir_domains": ["cera-india.com"],
        "identity_verified_at": "2026-10-28T09:00:00Z",
        "securities": [
            {"exchange": "NSE", "symbol": "CERA", "price_provider_symbol": "CERA.NS", "valid_from": "2007-07-24"},
            {"exchange": "BSE", "symbol": "532443", "price_provider_symbol": "CERA.BO", "valid_from": "2007-07-24"},
        ],
        "aliases": ["Cera", "Cera Sanitaryware"]
    },
    # Ad-hoc evaluation candidates
    {
        "id": "comp-coforge-020",
        "legal_name": "Coforge Limited",
        "isin": "INE591G01017",
        "sector": "Information Technology",
        "fiscal_calendar": "APR_MAR",
        "verified_ir_domains": ["coforge.com"],
        "identity_verified_at": "2026-10-28T09:00:00Z",
        "securities": [
            {"exchange": "NSE", "symbol": "COFORGE", "price_provider_symbol": "COFORGE.NS", "valid_from": "2004-08-30"},
            {"exchange": "BSE", "symbol": "532541", "price_provider_symbol": "COFORGE.BO", "valid_from": "2004-08-30"},
        ],
        "aliases": ["Coforge", "NIIT Technologies"]
    },
    {
        "id": "comp-dixon-021",
        "legal_name": "Dixon Technologies (India) Limited",
        "isin": "INE935N01020",
        "sector": "Electronics Manufacturing",
        "fiscal_calendar": "APR_MAR",
        "verified_ir_domains": ["dixoninfo.com"],
        "identity_verified_at": "2026-10-28T09:00:00Z",
        "securities": [
            {"exchange": "NSE", "symbol": "DIXON", "price_provider_symbol": "DIXON.NS", "valid_from": "2017-09-18"},
            {"exchange": "BSE", "symbol": "540699", "price_provider_symbol": "DIXON.BO", "valid_from": "2017-09-18"},
        ],
        "aliases": ["Dixon", "Dixon Tech", "Dixon Technologies"]
    },
    {
        "id": "comp-astral-022",
        "legal_name": "Astral Limited",
        "isin": "INE006I01046",
        "sector": "Building Products / Pipes",
        "fiscal_calendar": "APR_MAR",
        "verified_ir_domains": ["astralpipes.com"],
        "identity_verified_at": "2026-10-28T09:00:00Z",
        "securities": [
            {"exchange": "NSE", "symbol": "ASTRAL", "price_provider_symbol": "ASTRAL.NS", "valid_from": "2007-03-20"},
            {"exchange": "BSE", "symbol": "532830", "price_provider_symbol": "ASTRAL.BO", "valid_from": "2007-03-20"},
        ],
        "aliases": ["Astral", "Astral Poly", "Astral Pipes"]
    }
]

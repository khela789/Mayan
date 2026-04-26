#!/usr/bin/env python3
"""
Private Medical Clinic - Local Rank Tracker
Checks Google rankings for all locations and services using SearchAPI
"""

import requests
import csv
import time
from datetime import datetime
import os

# Configuration
API_KEY = 'htKi19wmCoEGnZk1iE1eVJ9M'
TARGET_DOMAIN = 'privatemedicalclinic.com'

# Locations and keywords
LOCATIONS = [
    'Birmingham',
    'Sutton Coldfield',
    'London',
    'Newcastle',
    'Leicester',
    'Bournemouth',
    'Oxford',
    'Derby'
]

SERVICES = {
    'Private GP': [f'private gp {loc.lower()}' for loc in LOCATIONS],
    'Hayfever Injection': [f'hayfever injection {loc.lower()}' for loc in LOCATIONS]
}

def check_ranking(keyword, location):
    """Check ranking for a single keyword in a specific location"""

    params = {
        'api_key': API_KEY,
        'engine': 'google',
        'q': keyword,
        'location': f'{location}, United Kingdom',
        'gl': 'uk',
        'hl': 'en',
        'num': 100  # Check top 100 results
    }

    try:
        response = requests.get('https://www.searchapi.io/api/v1/search', params=params)

        if response.status_code != 200:
            print(f"  ❌ API error for '{keyword}': Status {response.status_code}")
            return None, None

        data = response.json()

        # Check organic results
        organic_rank = None
        if 'organic_results' in data:
            for idx, result in enumerate(data['organic_results']):
                if 'link' in result and TARGET_DOMAIN.lower() in result['link'].lower():
                    organic_rank = idx + 1
                    break

        # Check local pack
        local_pack_rank = None
        if 'local_results' in data and 'places' in data['local_results']:
            for idx, place in enumerate(data['local_results']['places']):
                link = place.get('link', '') or place.get('website', '')
                if link and TARGET_DOMAIN.lower() in link.lower():
                    local_pack_rank = idx + 1
                    break

        return organic_rank, local_pack_rank

    except Exception as e:
        print(f"  ❌ Error checking '{keyword}': {str(e)}")
        return None, None

def main():
    """Main function to check all rankings"""

    print("=" * 60)
    print("PRIVATE MEDICAL CLINIC - RANK TRACKER")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Checking 16 keywords across 8 locations...")
    print()

    results = []
    total_keywords = sum(len(keywords) for keywords in SERVICES.values())
    current = 0

    # Check each service and location
    for service_name, keywords in SERVICES.items():
        for idx, keyword in enumerate(keywords):
            location = LOCATIONS[idx]
            current += 1

            print(f"[{current}/{total_keywords}] Checking: {keyword}")

            organic_rank, local_pack_rank = check_ranking(keyword, location)

            # Display results
            local_display = f"#{local_pack_rank}" if local_pack_rank else "Not in pack"
            organic_display = f"#{organic_rank}" if organic_rank else "Not found"

            if organic_rank and organic_rank <= 3:
                status = "🟢 Excellent"
            elif organic_rank and organic_rank <= 10:
                status = "🟡 Good"
            elif organic_rank:
                status = "⚪ OK"
            else:
                status = "🔴 Not ranked"

            print(f"  Local Pack: {local_display} | Organic: {organic_display} | {status}")

            # Store result
            results.append({
                'date': datetime.now().strftime('%Y-%m-%d'),
                'time': datetime.now().strftime('%H:%M:%S'),
                'location': location,
                'service': service_name,
                'keyword': keyword,
                'local_pack_rank': local_pack_rank or '',
                'organic_rank': organic_rank or '',
                'status': 'Found' if organic_rank else 'Not found'
            })

            # Rate limiting - 250ms between requests
            time.sleep(0.25)

    # Save to CSV
    filename = f"rank_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['date', 'time', 'location', 'service', 'keyword',
                     'local_pack_rank', 'organic_rank', 'status']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print()
    print("=" * 60)
    print("✅ COMPLETE!")
    print(f"Results saved to: {filename}")

    # Summary stats
    ranked_count = sum(1 for r in results if r['organic_rank'])
    top3_count = sum(1 for r in results if r['organic_rank'] and int(r['organic_rank']) <= 3)
    top10_count = sum(1 for r in results if r['organic_rank'] and int(r['organic_rank']) <= 10)
    local_pack_count = sum(1 for r in results if r['local_pack_rank'])

    print()
    print("SUMMARY:")
    print(f"  Keywords ranked: {ranked_count}/{total_keywords}")
    print(f"  Top 3 positions: {top3_count}")
    print(f"  Top 10 positions: {top10_count}")
    print(f"  In local pack: {local_pack_count}")

    if ranked_count > 0:
        avg_rank = sum(int(r['organic_rank']) for r in results if r['organic_rank']) / ranked_count
        print(f"  Average rank: {avg_rank:.1f}")

    print("=" * 60)

if __name__ == '__main__':
    main()

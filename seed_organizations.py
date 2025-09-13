#!/usr/bin/env python3
"""
Script to seed the database with default organizations
Run this script to populate the Organization table with common research institutions
"""

from compass import create_app
from compass.models import Organization, db

def seed_organizations():
    """Add default organizations to the database"""
    app = create_app()
    
    with app.app_context():
        # Check if organizations already exist
        existing_count = Organization.query.count()
        if existing_count > 0:
            print(f"Organizations already exist ({existing_count} found). Skipping seed.")
            return
        
        default_organizations = [
            {
                'name': 'National Centre for Polar and Ocean Research (NCPOR)',
                'short_name': 'NCPOR',
                'description': 'Premier Indian research institution for Polar and Ocean research under Ministry of Earth Sciences',
                'website': 'https://www.ncpor.res.in',
                'contact_email': 'info@ncpor.res.in',
                'country': 'India'
            },
            {
                'name': 'Indian Institute of Technology (IIT)',
                'short_name': 'IIT',
                'description': 'Premier engineering and technology institutes in India',
                'website': 'https://www.iit.ac.in',
                'country': 'India'
            },
            {
                'name': 'Indian Institute of Science (IISc)',
                'short_name': 'IISc',
                'description': 'Premier institute for research and higher education in science and engineering',
                'website': 'https://www.iisc.ac.in',
                'contact_email': 'info@iisc.ac.in',
                'country': 'India'
            },
            {
                'name': 'Council of Scientific and Industrial Research (CSIR)',
                'short_name': 'CSIR',
                'description': 'Premier national R&D organization in India',
                'website': 'https://www.csir.res.in',
                'country': 'India'
            },
            {
                'name': 'Indian Space Research Organisation (ISRO)',
                'short_name': 'ISRO',
                'description': 'National space agency of India',
                'website': 'https://www.isro.gov.in',
                'country': 'India'
            },
            {
                'name': 'Ministry of Earth Sciences (MoES)',
                'short_name': 'MoES',
                'description': 'Ministry responsible for Earth Sciences in India',
                'website': 'https://www.moes.gov.in',
                'country': 'India'
            },
            {
                'name': 'National Institute of Oceanography (NIO)',
                'short_name': 'NIO',
                'description': 'Premier institute for ocean research in India',
                'website': 'https://www.nio.org',
                'country': 'India'
            },
            {
                'name': 'Indian Meteorological Department (IMD)',
                'short_name': 'IMD',
                'description': 'National meteorological service of India',
                'website': 'https://mausam.imd.gov.in',
                'country': 'India'
            },
            {
                'name': 'Defence Research and Development Organisation (DRDO)',
                'short_name': 'DRDO',
                'description': 'Premier defence research organization of India',
                'website': 'https://www.drdo.gov.in',
                'country': 'India'
            },
            {
                'name': 'Jawaharlal Nehru University (JNU)',
                'short_name': 'JNU',
                'description': 'Premier public research university in New Delhi',
                'website': 'https://www.jnu.ac.in',
                'country': 'India'
            },
            {
                'name': 'University of Delhi',
                'short_name': 'DU',
                'description': 'Premier university in Delhi, India',
                'website': 'https://www.du.ac.in',
                'country': 'India'
            },
            {
                'name': 'International Partner Institution',
                'short_name': 'INTL',
                'description': 'For researchers from international institutions',
                'country': 'International'
            },
            {
                'name': 'Other Institution',
                'short_name': 'OTHER',
                'description': 'For institutions not listed above',
                'country': 'Other'
            }
        ]
        
        print("Adding default organizations...")
        
        for org_data in default_organizations:
            org = Organization(**org_data)
            db.session.add(org)
            print(f"  + {org_data['name']}")
        
        db.session.commit()
        print(f"\n✅ Successfully added {len(default_organizations)} organizations!")
        print("Organizations are now available for user profile setup.")

if __name__ == "__main__":
    print("🏢 COMPASS Organization Seeder")
    print("=" * 40)
    seed_organizations()

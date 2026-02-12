#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.queues.models import Service

# Create services if they don't exist
if Service.objects.count() == 0:
    services_data = [
        {
            'name': 'Birth Certificate',
            'code': 'BIRTH',
            'description': 'Birth Certificate Application and Issuance',
            'service_type': 'birth',
            'estimated_time': 30,
        },
        {
            'name': 'Death Certificate',
            'code': 'DEATH',
            'description': 'Death Certificate Application and Issuance',
            'service_type': 'death',
            'estimated_time': 20,
        },
        {
            'name': 'Marriage Certificate',
            'code': 'MARRIAGE',
            'description': 'Marriage Certificate Application and Issuance',
            'service_type': 'marriage',
            'estimated_time': 25,
        },
        {
            'name': 'Business Permit',
            'code': 'BPERM',
            'description': 'Business Permit Application and Processing',
            'service_type': 'permit',
            'estimated_time': 45,
        },
        {
            'name': 'Property Assessment',
            'code': 'ASSESS',
            'description': 'Property Assessment and Evaluation',
            'service_type': 'assessment',
            'estimated_time': 40,
        },
        {
            'name': 'General Inquiry',
            'code': 'INQUIRY',
            'description': 'General Information and Inquiry Services',
            'service_type': 'other',
            'estimated_time': 15,
        },
    ]
    
    for service_data in services_data:
        Service.objects.create(**service_data)
    
    print(f"✓ Created {len(services_data)} services successfully!")
else:
    count = Service.objects.count()
    print(f"✓ Services already exist: {count} services found")

# Display all services
print("\nAvailable Services:")
for service in Service.objects.all():
    print(f"  - {service.name} ({service.code})")

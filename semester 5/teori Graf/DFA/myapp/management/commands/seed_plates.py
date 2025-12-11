import random
from django.core.management.base import BaseCommand
from myapp.models import RegisteredPlate

class Command(BaseCommand):
    help = 'Seeds the database with random valid license plates'

    def handle(self, *args, **kwargs):
        self.stdout.write("Generating dummy plates... this may take a moment.")
        
        valid_regions = ['AA', 'AB', 'AD', 'AE', 'AG','DK','DR','EA', 'DH','EB',
                         'ED','KB','DA','KH','KT','KU','DB','DL','DM','DN','DT',
                         'DD','DP','DW','DC','PA','PB','DE','DG','BL','BB','BK',
                         'BH','BP','BD','BG','BN','BE']
        valid_suffixes = ['ABC', 'DEF', 'GHI', 'JKL', 'MNO', 'PQR', 'STU', 'VWX', 
                          'YZA', 'BCD', 'EFG', 'HIJ', 'KLM', 'NOP', 'QRS', 'TU'
                          'V', 'WXY', 'ZAB', 'CDE', 'FGH', 'IJK', 'LMN', 'OPQ', 
                          'RST', 'UVW', 'XYZ', 'BBJ']
        
        batch = []
        for _ in range(20000): # Let's start with 5,000 records
            region = random.choice(valid_regions)
            number = random.randint(1000, 9999)
            suffix = random.choice(valid_suffixes)
            
            # Format: "B 1234 XY"
            full_plate = f"{region} {number} {suffix}"
            
            batch.append(RegisteredPlate(plate_number=full_plate))
        
        # Bulk create is much faster than loop saving
        RegisteredPlate.objects.bulk_create(batch, ignore_conflicts=True)
        
        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {len(batch)} plates!'))
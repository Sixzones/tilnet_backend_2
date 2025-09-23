from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from projects.models import Material, Unit

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate the database with basic materials for tiling projects'

    def handle(self, *args, **options):
        # Create units first
        units_data = [
            {'name': 'Bag (50kg)', 'abbreviation': 'bag'},
            {'name': 'Cubic Meter', 'abbreviation': 'm³'},
            {'name': 'Square Meter', 'abbreviation': 'm²'},
            {'name': 'Box', 'abbreviation': 'box'},
            {'name': 'Bucket', 'abbreviation': 'bucket'},
            {'name': 'Kilogram', 'abbreviation': 'kg'},
            {'name': 'Pack', 'abbreviation': 'pack'},
            {'name': 'Liter', 'abbreviation': 'L'},
            {'name': 'Roll', 'abbreviation': 'roll'},
            {'name': 'Piece', 'abbreviation': 'pcs'},
        ]

        for unit_data in units_data:
            unit, created = Unit.objects.get_or_create(
                name=unit_data['name'],
                defaults={'abbreviation': unit_data['abbreviation']}
            )
            if created:
                self.stdout.write(f'Created unit: {unit.name}')
            else:
                self.stdout.write(f'Unit already exists: {unit.name}')

        # Get the units for material creation
        bag_unit = Unit.objects.get(name='Bag (50kg)')
        cubic_meter_unit = Unit.objects.get(name='Cubic Meter')
        sq_meter_unit = Unit.objects.get(name='Square Meter')
        box_unit = Unit.objects.get(name='Box')
        bucket_unit = Unit.objects.get(name='Bucket')
        kg_unit = Unit.objects.get(name='Kilogram')
        pack_unit = Unit.objects.get(name='Pack')
        liter_unit = Unit.objects.get(name='Liter')
        roll_unit = Unit.objects.get(name='Roll')
        piece_unit = Unit.objects.get(name='Piece')

        # Create materials for tiling projects
        materials_data = [
            {
                'name': 'Cement',
                'unit': 'bag',
                'unit_price': 15.00,
                'coverage_area': 0.1
            },
            {
                'name': 'Sand',
                'unit': 'cubic_meter',
                'unit_price': 25.00,
                'coverage_area': 1.0
            },
            {
                'name': 'Tiles',
                'unit': 'sq_meter',
                'unit_price': 45.00,
                'coverage_area': 1.0
            },
            {
                'name': 'Tile adhesive',
                'unit': 'bag',
                'unit_price': 12.00,
                'coverage_area': 0.1
            },
            {
                'name': 'Grout',
                'unit': 'kg',
                'unit_price': 8.00,
                'coverage_area': 0.05
            },
            {
                'name': 'Spacers',
                'unit': 'pack',
                'unit_price': 5.00,
                'coverage_area': 0.1
            },
            {
                'name': 'Primer',
                'unit': 'liter',
                'unit_price': 20.00,
                'coverage_area': 0.1
            },
            {
                'name': 'Waterproofing',
                'unit': 'liter',
                'unit_price': 35.00,
                'coverage_area': 0.1
            },
            {
                'name': 'Sealant',
                'unit': 'piece',
                'unit_price': 15.00,
                'coverage_area': 0.1
            },
            {
                'name': 'Leveling compound',
                'unit': 'bag',
                'unit_price': 18.00,
                'coverage_area': 0.1
            }
        ]

        # Create materials
        for material_data in materials_data:
            material, created = Material.objects.get_or_create(
                name=material_data['name'],
                defaults={
                    'unit': material_data['unit'],
                    'default_unit_price': material_data['unit_price'],
                    'default_coverage_area': material_data['coverage_area']
                }
            )
            if created:
                self.stdout.write(f'Created material: {material.name}')
            else:
                self.stdout.write(f'Material already exists: {material.name}')

        self.stdout.write(
            self.style.SUCCESS('Successfully populated materials and units!')
        )

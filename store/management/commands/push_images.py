import os
from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings
from store.models import Product

class Command(BaseCommand):
    help = 'Uploads local media files (images) to the Cloudinary storage backend.'

    def handle(self, *args, **kwargs):
        # Define the local media root directory
        local_media_root = os.path.join(settings.BASE_DIR, 'media')
        
        self.stdout.write("Starting existing image migration to Cloudinary...")

        for product in Product.objects.all():
            
            # Check if the product has an image field populated that is not already a URL
            if product.image and not str(product.image).startswith('http'):
                db_path = str(product.image)
                local_full_path = os.path.join(local_media_root, db_path)

                # Verify the file exists locally before attempting to open it
                if os.path.exists(local_full_path):
                    self.stdout.write(f'Processing {product.name} ({db_path})...')
                    
                    try:
                        with open(local_full_path, 'rb') as f:
                            # Re-save the image to trigger upload to Cloudinary
                            product.image.save(os.path.basename(db_path), File(f), save=True)
                        
                        self.stdout.write(self.style.SUCCESS(f'Successfully uploaded {product.name}'))
                    except Exception as e:
                         self.stdout.write(self.style.ERROR(f'Failed to upload {product.name}: {e}'))

                else:
                    self.stdout.write(self.style.WARNING(f'File not found locally for {product.name}. Skipping.'))
            elif product.image and str(product.image).startswith('http'):
                 self.stdout.write(f'{product.name} image already appears to be hosted. Skipping.')

        self.stdout.write(self.style.SUCCESS('Image migration complete.'))
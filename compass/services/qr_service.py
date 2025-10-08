"""
QR Code generation service with logo embedding for COMPASS shipment tracking
"""
import qrcode
from PIL import Image, ImageDraw, ImageFont
import os
import io
import secrets
from flask import current_app
from ..models import PackageQRCode, db

class QRCodeService:
    """Service class for generating QR codes with NCPOR logo embedding"""
    
    def __init__(self):
        self.qr_storage_dir = os.path.join(current_app.static_folder, 'qr_codes')
        self.qr_codes_dir = os.path.join(current_app.static_folder, 'qrcodes')  # Alternative directory
        self.logo_path = os.path.join(current_app.static_folder, 'images', 'ncpor_logo.png')
        
        # Ensure both QR codes directories exist
        os.makedirs(self.qr_storage_dir, exist_ok=True)
        os.makedirs(self.qr_codes_dir, exist_ok=True)
    
    def generate_package_qr_code(self, shipment, package_number, package_data, base_url):
        """
        Generate a QR code for a specific package with embedded NCPOR logo
        
        Args:
            shipment: Shipment model instance
            package_number: Package number within the shipment (1, 2, 3, etc.)
            package_data: Dictionary containing package information
            base_url: Base URL for the application
            
        Returns:
            PackageQRCode instance with generated QR code
        """
        try:
            # Generate unique tracking code
            unique_code = PackageQRCode.generate_unique_code()
            tracking_url = f"{base_url}/track/{unique_code}"
            
            # Create PackageQRCode record
            package_qr = PackageQRCode(
                shipment_id=shipment.id,
                package_number=package_number,
                unique_code=unique_code,
                qr_code_url=tracking_url,
                package_type=package_data.get('type'),
                package_description=package_data.get('description'),
                package_weight=package_data.get('weight'),
                package_dimensions=package_data.get('dimensions'),
                attention_person_id=package_data.get('attention_person_id')
            )
            
            # Generate QR code image
            qr_image_path = self._create_qr_code_image(tracking_url, unique_code)
            package_qr.qr_image_path = qr_image_path
            
            # Save to database
            db.session.add(package_qr)
            db.session.commit()
            
            return package_qr
            
        except Exception as e:
            current_app.logger.error(f"Error generating QR code for shipment {shipment.id}: {str(e)}")
            return None
    
    def _create_qr_code_image(self, tracking_url, unique_code):
        """
        Create QR code image with embedded NCPOR logo
        
        Args:
            tracking_url: URL to embed in QR code
            unique_code: Unique tracking code for filename
            
        Returns:
            Relative path to saved QR code image
        """
        try:
            # Create QR code instance with optimal settings
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction for logo embedding
                box_size=10,
                border=4,
            )
            
            qr.add_data(tracking_url)
            qr.make(fit=True)
            
            # Generate QR code image with NCPOR colors (blue theme)
            qr_image = qr.make_image(
                fill_color=(30, 63, 102),  # NCPOR dark blue
                back_color=(255, 255, 255)  # White background
            )
            
            # Convert to RGB if needed
            qr_image = qr_image.convert('RGB')
            
            # Embed NCPOR logo in the center
            qr_with_logo = self._embed_logo(qr_image)
            
            # Add tracking code text below QR code
            final_image = self._add_tracking_text(qr_with_logo, unique_code)
            
            # Save image
            filename = f"package_{unique_code}.png"
            file_path = os.path.join(self.qr_storage_dir, filename)
            final_image.save(file_path, 'PNG', quality=95)
            
            # Return relative path for web access
            return f"static/qr_codes/{filename}"
            
        except Exception as e:
            current_app.logger.error(f"Error creating QR code image: {str(e)}")
            # Return a fallback image path or None
            return None
    
    def _embed_logo(self, qr_image):
        """
        Embed NCPOR logo in the center of QR code
        
        Args:
            qr_image: PIL Image of QR code
            
        Returns:
            PIL Image with embedded logo
        """
        try:
            # Load NCPOR logo
            if os.path.exists(self.logo_path):
                logo = Image.open(self.logo_path)
            else:
                # Create a simple circular logo with NCPOR text if logo file doesn't exist
                logo = self._create_fallback_logo()
            
            # Calculate logo size (should be about 1/5 of QR code size)
            qr_width, qr_height = qr_image.size
            logo_size = min(qr_width, qr_height) // 5
            
            # Resize logo while maintaining aspect ratio
            logo = logo.convert('RGBA')
            logo.thumbnail((logo_size, logo_size), Image.Resampling.LANCZOS)
            
            # Create a white circular background for the logo
            mask_size = logo_size + 20  # Add padding
            mask = Image.new('RGBA', (mask_size, mask_size), (255, 255, 255, 0))
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse([0, 0, mask_size, mask_size], fill=(255, 255, 255, 255))
            
            # Calculate position to center the logo
            logo_pos = (
                (qr_width - logo.size[0]) // 2,
                (qr_height - logo.size[1]) // 2
            )
            
            mask_pos = (
                (qr_width - mask_size) // 2,
                (qr_height - mask_size) // 2
            )
            
            # Create a copy of QR image to modify
            qr_with_logo = qr_image.copy()
            
            # Paste white circular background first
            qr_with_logo.paste(mask, mask_pos, mask)
            
            # Paste logo on top
            qr_with_logo.paste(logo, logo_pos, logo)
            
            return qr_with_logo
            
        except Exception as e:
            current_app.logger.error(f"Error embedding logo: {str(e)}")
            return qr_image  # Return original QR code if logo embedding fails
    
    def _create_fallback_logo(self):
        """
        Create a simple fallback logo if NCPOR logo file is not available
        
        Returns:
            PIL Image of fallback logo
        """
        # Create a 100x100 image with NCPOR colors
        size = 100
        logo = Image.new('RGBA', (size, size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(logo)
        
        # Draw a circle with NCPOR blue
        draw.ellipse([0, 0, size, size], fill=(30, 63, 102, 255), outline=(255, 255, 255, 255), width=3)
        
        # Try to add NCPOR text (fallback if font loading fails)
        try:
            # Use a system font if available
            font = ImageFont.truetype("arial.ttf", 16)
        except:
            font = ImageFont.load_default()
        
        # Calculate text position
        text = "NCPOR"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = (size - text_width) // 2
        text_y = (size - text_height) // 2
        
        # Draw text
        draw.text((text_x, text_y), text, fill=(255, 255, 255, 255), font=font)
        
        return logo
    
    def _add_tracking_text(self, qr_image, unique_code):
        """
        Add tracking code text below the QR code
        
        Args:
            qr_image: PIL Image of QR code with logo
            unique_code: Tracking code to display
            
        Returns:
            PIL Image with tracking text added
        """
        try:
            # Calculate new image size with space for text
            qr_width, qr_height = qr_image.size
            text_height = 40
            new_height = qr_height + text_height
            
            # Create new image with extra space
            final_image = Image.new('RGB', (qr_width, new_height), (255, 255, 255))
            
            # Paste QR code at the top
            final_image.paste(qr_image, (0, 0))
            
            # Add tracking code text
            draw = ImageDraw.Draw(final_image)
            
            try:
                font = ImageFont.truetype("arial.ttf", 12)
            except:
                font = ImageFont.load_default()
            
            # Format tracking code for display
            display_text = f"Track: {unique_code}"
            
            # Calculate text position (centered)
            bbox = draw.textbbox((0, 0), display_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_x = (qr_width - text_width) // 2
            text_y = qr_height + 10
            
            # Draw text
            draw.text((text_x, text_y), display_text, fill=(30, 63, 102), font=font)
            
            return final_image
            
        except Exception as e:
            current_app.logger.error(f"Error adding tracking text: {str(e)}")
            return qr_image  # Return QR image without text if adding text fails
    
    def regenerate_qr_code(self, package_qr, base_url):
        """
        Regenerate QR code for an existing package
        
        Args:
            package_qr: PackageQRCode instance
            base_url: Base URL for the application
            
        Returns:
            Updated PackageQRCode instance
        """
        try:
            # Generate new QR code image
            qr_image_path = self._create_qr_code_image(package_qr.qr_code_url, package_qr.unique_code)
            
            if qr_image_path:
                # Remove old QR code file if it exists
                if package_qr.qr_image_path:
                    old_path = os.path.join(current_app.root_path, package_qr.qr_image_path)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                
                # Update database record
                package_qr.qr_image_path = qr_image_path
                db.session.commit()
            
            return package_qr
            
        except Exception as e:
            current_app.logger.error(f"Error regenerating QR code: {str(e)}")
            return package_qr
    
    def get_qr_code_url(self, package_qr):
        """
        Get the URL to access the QR code image
        
        Args:
            package_qr: PackageQRCode instance
            
        Returns:
            URL string for accessing QR code image
        """
        if package_qr.qr_image_path:
            return f"/{package_qr.qr_image_path}"
        return None
    
    def cleanup_orphaned_qr_codes(self):
        """
        Clean up QR code files that no longer have database records
        """
        try:
            # Get all QR code files in the directory
            qr_files = []
            if os.path.exists(self.qr_storage_dir):
                qr_files = [f for f in os.listdir(self.qr_storage_dir) if f.endswith('.png')]
            
            # Get all QR code paths from database
            db_paths = db.session.query(PackageQRCode.qr_image_path).filter(
                PackageQRCode.qr_image_path.isnot(None)
            ).all()
            db_filenames = [os.path.basename(path[0]) for path in db_paths if path[0]]
            
            # Remove orphaned files
            removed_count = 0
            for filename in qr_files:
                if filename not in db_filenames:
                    file_path = os.path.join(self.qr_storage_dir, filename)
                    try:
                        os.remove(file_path)
                        removed_count += 1
                    except Exception as e:
                        current_app.logger.error(f"Error removing orphaned QR file {filename}: {str(e)}")
            
            current_app.logger.info(f"Cleaned up {removed_count} orphaned QR code files")
            return removed_count
            
        except Exception as e:
            current_app.logger.error(f"Error during QR cleanup: {str(e)}")
            return 0
    
    def generate_webapp_qr_code(self, base_url):
        """
        Generate QR code for the COMPASS web app homepage
        
        Args:
            base_url (str): The base URL of the web application
            
        Returns:
            str: Path to the generated QR code image
        """
        try:
            current_app.logger.info(f"Starting webapp QR generation for URL: {base_url}")
            
            # Create QR code instance
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction for logo
                box_size=12,  # Slightly larger for better scanning
                border=4,
            )
            
            # Add web app URL
            qr.add_data(base_url)
            qr.make(fit=True)
            
            current_app.logger.info("QR code data added successfully")
            
            # Generate QR code image with COMPASS branding colors
            qr_image = qr.make_image(
                fill_color=(30, 63, 102),  # NCPOR dark blue
                back_color=(255, 255, 255)  # White background
            )
            
            current_app.logger.info("QR code image generated successfully")
            
            # Convert to RGB
            qr_image = qr_image.convert('RGB')
            current_app.logger.info("QR code converted to RGB")
            
            # Embed NCPOR logo in the center
            current_app.logger.info(f"Checking logo path: {self.logo_path}")
            if os.path.exists(self.logo_path):
                try:
                    current_app.logger.info("Logo file found, starting embedding process")
                    logo = Image.open(self.logo_path)
                    
                    # Calculate logo size (15% of QR code size)
                    qr_width, qr_height = qr_image.size
                    logo_size = min(qr_width, qr_height) // 6
                    
                    # Resize logo maintaining aspect ratio
                    logo = logo.resize((logo_size, logo_size), Image.LANCZOS)
                    
                    # Create a white background for the logo
                    logo_bg = Image.new('RGB', (logo_size + 20, logo_size + 20), (255, 255, 255))
                    logo_bg_pos = ((logo_bg.size[0] - logo.size[0]) // 2, 
                                  (logo_bg.size[1] - logo.size[1]) // 2)
                    
                    # Handle transparency
                    if logo.mode == 'RGBA':
                        logo_bg.paste(logo, logo_bg_pos, logo)
                    else:
                        logo_bg.paste(logo, logo_bg_pos)
                    
                    # Calculate center position
                    logo_pos = ((qr_width - logo_bg.size[0]) // 2, 
                               (qr_height - logo_bg.size[1]) // 2)
                    
                    # Paste logo onto QR code
                    qr_image.paste(logo_bg, logo_pos)
                    current_app.logger.info("Logo embedded successfully")
                    
                except Exception as e:
                    current_app.logger.warning(f"Could not embed logo in webapp QR code: {str(e)}")
            else:
                current_app.logger.warning(f"Logo file not found at: {self.logo_path}")
            
            # Save the QR code image
            qr_image_path = os.path.join(self.qr_codes_dir, 'webapp_qr.png')
            current_app.logger.info(f"Saving QR code to: {qr_image_path}")
            qr_image.save(qr_image_path, 'PNG', optimize=True, quality=95)
            current_app.logger.info("QR code saved successfully")
            
            current_app.logger.info(f"Generated webapp QR code: {qr_image_path}")
            return qr_image_path
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            current_app.logger.error(f"Error generating webapp QR code: {str(e)}\n{error_details}")
            raise Exception(f"QR generation failed: {str(e)}")

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
        self.logo_path = os.path.join(current_app.static_folder, 'images', 'ncpor_logo.png')
        
        # Ensure QR codes directory exists
        os.makedirs(self.qr_storage_dir, exist_ok=True)
    
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
            # Create QR code instance with PRINT-QUALITY settings
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction for logo embedding
                box_size=20,  # Increased from 10 to 20 for higher resolution
                border=6,     # Slightly larger border for print clarity
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
            
            # Save image with PRINT-QUALITY settings
            filename = f"package_{unique_code}.png"
            file_path = os.path.join(self.qr_storage_dir, filename)
            
            # Save at high resolution with optimal settings for printing
            final_image.save(file_path, 'PNG', 
                           optimize=False,  # Don't compress for print quality
                           dpi=(300, 300),  # High DPI for printing
                           quality=100)     # Maximum quality
            
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
            # Calculate new image size with space for text (larger for print)
            qr_width, qr_height = qr_image.size
            text_height = 80  # Increased height for better print visibility
            new_height = qr_height + text_height
            
            # Create new image with extra space
            final_image = Image.new('RGB', (qr_width, new_height), (255, 255, 255))
            
            # Paste QR code at the top
            final_image.paste(qr_image, (0, 0))
            
            # Add tracking code text with print-optimized settings
            draw = ImageDraw.Draw(final_image)
            
            # Use larger font for print clarity
            try:
                # Try multiple font sizes for optimal print visibility
                font_large = ImageFont.truetype("arial.ttf", 24)  # Larger font for print
                font_small = ImageFont.truetype("arial.ttf", 16)
            except:
                try:
                    font_large = ImageFont.load_default()
                    font_small = ImageFont.load_default()
                except:
                    font_large = None
                    font_small = None
            
            # Main tracking code (larger)
            display_text = f"{unique_code}"
            
            if font_large:
                # Calculate text position (centered)
                bbox = draw.textbbox((0, 0), display_text, font=font_large)
                text_width = bbox[2] - bbox[0]
                text_x = (qr_width - text_width) // 2
                text_y = qr_height + 15
                
                # Draw main tracking code with thick text for print clarity
                draw.text((text_x, text_y), display_text, fill=(30, 63, 102), font=font_large)
                
                # Add "COMPASS NCPOR" subtitle
                subtitle = "COMPASS NCPOR"
                if font_small:
                    bbox_sub = draw.textbbox((0, 0), subtitle, font=font_small)
                    sub_width = bbox_sub[2] - bbox_sub[0]
                    sub_x = (qr_width - sub_width) // 2
                    sub_y = text_y + 35
                    draw.text((sub_x, sub_y), subtitle, fill=(100, 100, 100), font=font_small)
            
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
    
    def create_print_sheet(self, package_qr_codes, sheet_layout=(2, 1)):
        """
        Create a printable A4 sheet with multiple QR codes
        
        Args:
            package_qr_codes: List of PackageQRCode instances
            sheet_layout: Tuple (cols, rows) for QR code arrangement
            
        Returns:
            PIL Image of printable sheet
        """
        try:
            # A4 dimensions at 300 DPI (print quality)
            a4_width = int(8.27 * 300)   # 2481 pixels
            a4_height = int(11.69 * 300)  # 3507 pixels
            
            # Create white A4 sheet
            sheet = Image.new('RGB', (a4_width, a4_height), (255, 255, 255))
            
            cols, rows = sheet_layout
            max_qr_codes = cols * rows
            
            # Calculate QR code size and spacing
            margin = 150  # 0.5 inch margins
            available_width = a4_width - (2 * margin)
            available_height = a4_height - (2 * margin)
            
            qr_width = available_width // cols
            qr_height = available_height // rows
            
            # Process QR codes
            for i, package_qr in enumerate(package_qr_codes[:max_qr_codes]):
                if package_qr.qr_image_path:
                    try:
                        # Load QR code image
                        qr_image_path = os.path.join(current_app.static_folder, 
                                                   package_qr.qr_image_path.replace('static/', ''))
                        qr_image = Image.open(qr_image_path)
                        
                        # Resize QR code to fit in allocated space (with padding)
                        max_qr_size = min(qr_width - 100, qr_height - 200)  # Leave space for info
                        qr_image.thumbnail((max_qr_size, max_qr_size), Image.Resampling.LANCZOS)
                        
                        # Calculate position
                        row = i // cols
                        col = i % cols
                        
                        x = margin + (col * qr_width) + (qr_width - qr_image.width) // 2
                        y = margin + (row * qr_height) + 50  # 50px from top of cell
                        
                        # Paste QR code
                        sheet.paste(qr_image, (x, y))
                        
                        # Add package information below QR code
                        self._add_package_info_to_sheet(sheet, package_qr, x, y + qr_image.height + 20, qr_width)
                        
                    except Exception as e:
                        current_app.logger.error(f"Error adding QR code {i} to sheet: {str(e)}")
                        continue
            
            return sheet
            
        except Exception as e:
            current_app.logger.error(f"Error creating print sheet: {str(e)}")
            return None
    
    def _add_package_info_to_sheet(self, sheet, package_qr, x, y, width):
        """Add package information text to print sheet"""
        try:
            draw = ImageDraw.Draw(sheet)
            
            # Load fonts
            try:
                font_title = ImageFont.truetype("arial.ttf", 20)
                font_info = ImageFont.truetype("arial.ttf", 14)
            except:
                font_title = ImageFont.load_default()
                font_info = ImageFont.load_default()
            
            # Package info lines
            lines = [
                f"Shipment ID: {package_qr.shipment.id}",
                f"Package: {package_qr.package_number}",
                f"Type: {package_qr.package_type or 'N/A'}",
                f"Weight: {package_qr.package_weight or 'N/A'}",
                f"Track: {package_qr.unique_code}"
            ]
            
            line_height = 25
            for i, line in enumerate(lines):
                font = font_title if i == 0 else font_info
                color = (30, 63, 102) if i == 0 else (50, 50, 50)
                
                # Center text in the allocated width
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                text_x = x + (width - text_width) // 2
                text_y = y + (i * line_height)
                
                draw.text((text_x, text_y), line, fill=color, font=font)
                
        except Exception as e:
            current_app.logger.error(f"Error adding package info to sheet: {str(e)}")

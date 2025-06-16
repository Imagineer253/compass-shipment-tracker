#!/usr/bin/env python3
"""
Script to update base.html template with NCPOR branding
"""

def update_base_template():
    # Read the current base.html
    with open('compass/templates/base.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace the navigation logo section
    old_nav = '''                    <a href="/" class="flex items-center space-x-2">
                        <span class="text-2xl font-bold text-deep-arctic">❄️ COMPASS</span>
                    </a>'''
    
    new_nav = '''                    <a href="/" class="flex items-center space-x-3">
                        <!-- NCPOR Logo placeholder -->
                        <div class="w-10 h-10 bg-deep-arctic rounded-full flex items-center justify-center">
                            <span class="text-white font-bold text-sm">NCPOR</span>
                        </div>
                        <div class="flex flex-col">
                            <span class="text-lg font-bold text-deep-arctic">COMPASS</span>
                            <span class="text-xs text-gray-600">Arctic Research System</span>
                        </div>
                    </a>'''
    
    # Replace the content
    updated_content = content.replace(old_nav, new_nav)
    
    # Write the updated content back
    with open('compass/templates/base.html', 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print("✓ Base template updated with NCPOR branding!")

if __name__ == '__main__':
    update_base_template() 
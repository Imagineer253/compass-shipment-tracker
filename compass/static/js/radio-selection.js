// Universal Radio Button Selection Handler for COMPASS Application
document.addEventListener('DOMContentLoaded', function() {
    
    // Generic radio button handler
    function setupRadioButtonSelection(radioSelector, cardSelector) {
        const radios = document.querySelectorAll(radioSelector);
        radios.forEach(radio => {
            radio.addEventListener('change', function() {
                if (this.checked) {
                    // Remove selected class from all cards with the same name
                    const radioName = this.name;
                    document.querySelectorAll(`input[name="${radioName}"]`).forEach(input => {
                        const card = input.nextElementSibling;
                        if (card && card.classList.contains('radio-card')) {
                            card.classList.remove('selected');
                        }
                    });
                    
                    // Add selected class to current selection
                    const card = this.nextElementSibling;
                    if (card && card.classList.contains('radio-card')) {
                        card.classList.add('selected');
                    }
                }
            });
        });
    }

    // Package type radio buttons (dynamic names)
    function setupPackageTypeRadios() {
        const packageTypeRadios = document.querySelectorAll('.package-type-radio');
        packageTypeRadios.forEach(radio => {
            radio.addEventListener('change', function() {
                if (this.checked) {
                    const packageName = this.name;
                    
                    // Remove selected class from all package type cards with the same name
                    document.querySelectorAll(`input[name="${packageName}"]`).forEach(input => {
                        const card = input.nextElementSibling;
                        if (card && card.classList.contains('package-type-card')) {
                            card.classList.remove('selected');
                        }
                    });
                    
                    // Add selected class to current selection
                    const card = this.nextElementSibling;
                    if (card && card.classList.contains('package-type-card')) {
                        card.classList.add('selected');
                    }
                }
            });
        });
    }

    // Cold shipment box type radio buttons (dynamic names)
    function setupBoxTypeRadios() {
        const boxTypeRadios = document.querySelectorAll('input[name*="box_"][name*="_type"]');
        boxTypeRadios.forEach(radio => {
            radio.addEventListener('change', function() {
                if (this.checked) {
                    const boxName = this.name;
                    
                    // Remove selected class from all box type cards with the same name
                    document.querySelectorAll(`input[name="${boxName}"]`).forEach(input => {
                        const card = input.nextElementSibling;
                        if (card && card.classList.contains('radio-card')) {
                            card.classList.remove('selected');
                        }
                    });
                    
                    // Add selected class to current selection
                    const card = this.nextElementSibling;
                    if (card && card.classList.contains('radio-card')) {
                        card.classList.add('selected');
                    }
                }
            });
        });
    }

    // Setup all radio button types - handle both new class-based and old attribute-based selections
    setupRadioButtonSelection('.return-type-radio', '.radio-card');
    setupRadioButtonSelection('.exporter-radio', '.radio-card');
    setupRadioButtonSelection('.shipper-radio', '.radio-card');
    setupRadioButtonSelection('.consignee-radio', '.radio-card');
    setupRadioButtonSelection('.importer-radio', '.radio-card');
    setupRadioButtonSelection('.import-purpose-radio', '.radio-card');
    setupRadioButtonSelection('.export-type-radio', '.radio-card');
    
    // Handle radio buttons that don't have specific classes yet
    setupRadioButtonSelection('input[name="exporter"]', '.radio-card');
    setupRadioButtonSelection('input[name="consignee"]', '.radio-card');
    setupRadioButtonSelection('input[name="shipper"]', '.radio-card');
    setupRadioButtonSelection('input[name="consignee_org"]', '.radio-card');
    setupRadioButtonSelection('input[name="importer_type"]', '.radio-card');
    setupRadioButtonSelection('input[name="import_purpose"]', '.radio-card');
    
    // Additional radio button types for comprehensive coverage
    setupRadioButtonSelection('input[name="export_purpose"]', '.radio-card');
    setupRadioButtonSelection('input[name="transport_mode"]', '.radio-card');
    setupRadioButtonSelection('input[name="urgency"]', '.radio-card');
    setupRadioButtonSelection('input[name="customs_status"]', '.radio-card');
    
    // Handle any remaining radio buttons that might be missed
    const allRadios = document.querySelectorAll('input[type="radio"]:not(.package-type-radio):not(.return-type-radio):not(.exporter-radio):not(.shipper-radio):not(.consignee-radio):not(.importer-radio):not(.import-purpose-radio)');
    allRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.checked) {
                const radioName = this.name;
                // Remove selected class from all cards with the same name
                document.querySelectorAll(`input[name="${radioName}"]`).forEach(input => {
                    const card = input.nextElementSibling;
                    if (card && card.classList.contains('radio-card')) {
                        card.classList.remove('selected');
                    }
                });
                
                // Add selected class to current selection
                const card = this.nextElementSibling;
                if (card && card.classList.contains('radio-card')) {
                    card.classList.add('selected');
                }
            }
        });
    });
    
    // Setup dynamic radio buttons
    setupPackageTypeRadios();
    setupBoxTypeRadios();

    // Initial state setup - mark checked radios as selected
    function setInitialState() {
        const allRadios = document.querySelectorAll('input[type="radio"]:checked');
        allRadios.forEach(radio => {
            const card = radio.nextElementSibling;
            if (card && (card.classList.contains('radio-card') || card.classList.contains('package-type-card'))) {
                card.classList.add('selected');
            }
        });
    }

    // Enhanced initialization - run on DOM ready and after dynamic content loads
    setInitialState();
    
    // Re-run setup when new content is dynamically added
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                // Check if new radio buttons were added
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === 1) { // Element node
                        const newRadios = node.querySelectorAll ? node.querySelectorAll('input[type="radio"]') : [];
                        if (newRadios.length > 0) {
                            // Re-setup radio button handling for new elements
                            setupPackageTypeRadios();
                            setupBoxTypeRadios();
                            setInitialState();
                        }
                    }
                });
            }
        });
    });

    // Observe the document for changes
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
}); 
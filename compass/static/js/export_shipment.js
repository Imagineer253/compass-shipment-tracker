// Export Shipment Form JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Elements for invoice number generation
    const requesterName = document.getElementById('requesterName');
    const expeditionYear = document.getElementById('expeditionYear');
    const batchNumber = document.getElementById('batchNumber');
    const returnTypeInputs = document.getElementsByName('return_type');
    const invoicePreview = document.getElementById('invoiceNumberPreview');

    // Set current date in hidden field
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('invoiceDateHidden').value = today;

    // Set max year as current year + 1
    const maxYear = new Date().getFullYear() + 1;
    expeditionYear.setAttribute('max', maxYear);
    expeditionYear.setAttribute('min', '2000');

    // Function to generate invoice number
    function updateInvoiceNumber() {
        let firstName = 'FIRSTNAME';
        if (requesterName.value) {
            const nameParts = requesterName.value.trim().split(' ');
            // If we have title + first name (or more)
            if (nameParts.length > 1) {
                firstName = nameParts[1].toUpperCase(); // Take second word as first name
            } else {
                firstName = nameParts[0].toUpperCase(); // If only one word, use that
            }
        }

        const year = expeditionYear.value || 'YYYY';
        const batch = (batchNumber.value || 'BATCH').toUpperCase();
        let returnType = 'TYPE';
        
        for (const input of returnTypeInputs) {
            if (input.checked) {
                returnType = input.value;
                break;
            }
        }

        const invoiceNumber = `NCPOR/ARC/${year}/${returnType}/${batch}/${firstName}`;
        invoicePreview.textContent = invoiceNumber;
    }

    // Add event listeners for invoice number generation
    requesterName.addEventListener('input', updateInvoiceNumber);
    expeditionYear.addEventListener('input', updateInvoiceNumber);
    batchNumber.addEventListener('input', updateInvoiceNumber);
    returnTypeInputs.forEach(input => {
        input.addEventListener('change', updateInvoiceNumber);
    });

    // Elements for package handling
    const totalPackagesInput = document.getElementById('totalPackagesInput');
    const packageDetailsContainer = document.getElementById('packageDetailsContainer');
    const packageDetailsTemplate = document.getElementById('packageDetailsTemplate');
    const itemDetailsTemplate = document.getElementById('itemDetailsTemplate');
    const packageSummary = document.getElementById('packageSummary');

    // Function to handle package type selection
    function initializePackageTypeHandlers(packageElement) {
        const typeRadios = packageElement.querySelectorAll('input[type="radio"]');
        const otherTypeInput = packageElement.querySelector('.other-type-input');

        typeRadios.forEach(radio => {
            radio.addEventListener('change', function() {
                otherTypeInput.classList.toggle('hidden', this.value !== 'other');
                otherTypeInput.querySelector('input').required = (this.value === 'other');
            });
        });
    }

    // Function to update total calculations
    function updateTotals() {
        let totalItems = 0;
        let totalNetWeight = 0;
        let totalValue = 0;

        document.querySelectorAll('.item-quantity').forEach(quantityInput => {
            totalItems += parseInt(quantityInput.value) || 0;
        });

        document.querySelectorAll('.item-weight').forEach(weightInput => {
            const quantity = parseInt(weightInput.closest('.items-container').querySelector('.item-quantity').value) || 0;
            totalNetWeight += (parseFloat(weightInput.value) || 0) * quantity;
        });

        document.querySelectorAll('.item-total').forEach(totalElement => {
            totalValue += parseFloat(totalElement.textContent) || 0;
        });

        // Update summary display
        document.getElementById('totalPackagesDisplay').textContent = totalPackagesInput.value || '0';
        document.getElementById('totalItemsDisplay').textContent = totalItems;
        document.getElementById('totalNetWeightDisplay').textContent = `${totalNetWeight.toFixed(2)} kg`;
        document.getElementById('totalValueDisplay').textContent = `${totalValue.toFixed(2)} USD`;
    }

    // Function to calculate item total value
    function calculateItemTotal(prefix) {
        const quantity = parseInt(document.querySelector(`[name="${prefix}_quantity"]`).value) || 0;
        const unitValue = parseFloat(document.querySelector(`[name="${prefix}_unit_value"]`).value) || 0;
        const total = quantity * unitValue;
        document.getElementById(`${prefix}_total`).textContent = `${total.toFixed(2)} USD`;
        updateTotals();
    }

    // Function to generate item details
    function generateItemDetails(packageNum, itemCount, container) {
        container.innerHTML = '';
        for (let itemNum = 1; itemNum <= itemCount; itemNum++) {
            const prefix = `package_${packageNum}_item_${itemNum}`;
            const itemHtml = itemDetailsTemplate.innerHTML
                .replaceAll('{itemNumber}', itemNum)
                .replaceAll('{prefix}', prefix);
            
            const itemElement = document.createElement('div');
            itemElement.innerHTML = itemHtml;
            container.appendChild(itemElement);

            // Add event listeners for calculations
            const inputs = container.querySelectorAll(`[data-prefix="${prefix}"]`);
            inputs.forEach(input => {
                input.addEventListener('input', () => calculateItemTotal(prefix));
            });
        }
    }

    // Function to generate package details
    function generatePackageDetails(totalPackages) {
        packageDetailsContainer.innerHTML = '';
        for (let packageNum = 1; packageNum <= totalPackages; packageNum++) {
            const packageHtml = packageDetailsTemplate.innerHTML
                .replaceAll('{packageNumber}', packageNum)
                .replaceAll('{totalPackages}', totalPackages);
            
            const packageElement = document.createElement('div');
            packageElement.innerHTML = packageHtml;
            packageDetailsContainer.appendChild(packageElement);

            // Initialize handlers for this package
            initializePackageTypeHandlers(packageElement);
            
            // Handle items count for this package
            const itemsCountInput = packageElement.querySelector('.package-items-count');
            const itemsContainer = packageElement.querySelector('.items-container');
            
            itemsCountInput.addEventListener('change', function() {
                const itemCount = parseInt(this.value) || 0;
                if (itemCount > 0) {
                    generateItemDetails(packageNum, itemCount, itemsContainer);
                    updateTotals();
                } else {
                    itemsContainer.innerHTML = '';
                    updateTotals();
                }
            });
        }
    }

    // Handle total packages input
    totalPackagesInput.addEventListener('change', function() {
        const totalPackages = parseInt(this.value) || 0;
        if (totalPackages > 0) {
            packageDetailsContainer.classList.remove('hidden');
            packageSummary.classList.remove('hidden');
            generatePackageDetails(totalPackages);
        } else {
            packageDetailsContainer.classList.add('hidden');
            packageSummary.classList.add('hidden');
        }
    });

    // Initialize exporters and consignees sections
    const exporterNcporRadio = document.getElementById('exporterNcporRadio');
    const exporterOtherRadio = document.getElementById('exporterOtherRadio');
    const ncporExporterDetails = document.getElementById('ncporExporterDetails');
    const otherExporterDetails = document.getElementById('otherExporterDetails');

    const consigneeHimadriRadio = document.getElementById('consigneeHimadriRadio');
    const consigneeOtherRadio = document.getElementById('consigneeOtherRadio');
    const himadriConsigneeDetails = document.getElementById('himadriConsigneeDetails');
    const otherConsigneeDetails = document.getElementById('otherConsigneeDetails');

    // Function to toggle required fields
    function toggleRequiredFields(container, required) {
        const inputs = container.querySelectorAll('input, textarea');
        inputs.forEach(input => {
            input.required = required;
        });
    }

    // Function to handle exporter selection
    function handleExporterSelection() {
        if (exporterNcporRadio.checked) {
            ncporExporterDetails.classList.remove('hidden');
            otherExporterDetails.classList.add('hidden');
            toggleRequiredFields(otherExporterDetails, false);
        } else {
            ncporExporterDetails.classList.add('hidden');
            otherExporterDetails.classList.remove('hidden');
            toggleRequiredFields(otherExporterDetails, true);
        }
    }

    // Function to handle consignee selection
    function handleConsigneeSelection() {
        if (consigneeHimadriRadio.checked) {
            himadriConsigneeDetails.classList.remove('hidden');
            otherConsigneeDetails.classList.add('hidden');
            toggleRequiredFields(otherConsigneeDetails, false);
        } else {
            himadriConsigneeDetails.classList.add('hidden');
            otherConsigneeDetails.classList.remove('hidden');
            toggleRequiredFields(otherConsigneeDetails, true);
        }
    }

    // Add event listeners
    exporterNcporRadio.addEventListener('change', handleExporterSelection);
    exporterOtherRadio.addEventListener('change', handleExporterSelection);
    consigneeHimadriRadio.addEventListener('change', handleConsigneeSelection);
    consigneeOtherRadio.addEventListener('change', handleConsigneeSelection);

    // Initial setup
    handleExporterSelection();
    handleConsigneeSelection();

    // Form validation
    const form = document.querySelector('form');
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (!form.checkValidity()) {
            // Find the first invalid input
            const firstInvalid = form.querySelector(':invalid');
            if (firstInvalid) {
                firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
                firstInvalid.focus();
            }
            return false;
        }

        // Additional validation
        const totalPackages = parseInt(totalPackagesInput.value) || 0;
        if (totalPackages === 0) {
            alert('Please enter at least one package');
            totalPackagesInput.focus();
            return false;
        }

        // All validations passed, submit the form
        this.submit();
    });
}); 
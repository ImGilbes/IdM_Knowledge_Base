function toggle_filters() {
    const element = document
                    .getElementById('filters-div');
    element.classList.toggle('visible');
}

function get_checkboxes_categories(){
    let checkboxes = document.getElementsByName('filter_checkbox');
    let result = new Array();
    for (let i = 0; i < checkboxes.length; i++) {
        if (checkboxes[i].checked) {
            result.push(checkboxes[i].value);
        }
    }
    return result;
}

function updateFilters(){
    const filter_mode= document.getElementById("filter_mode_select").value;
    if (filter_mode == "columns") {
        updateFiltersColumns();
    }
    if (filter_mode == "rows") {
        updateFiltersRows();
    }
}

function updateFiltersColumns(){
    // applies only to the displayed entities
    loaded.forEach(entity => {
        if(displayed.indexOf(entity) != -1){
            const checked = get_checkboxes_categories();

            const table = document.getElementById(entity+"_table");
            const headers = table.querySelectorAll("thead th");
            const rows = table.querySelectorAll("tbody tr");

            headers.forEach((header, i) => {
                if (checked.indexOf(header.textContent) == -1) { // if not in the checked list, then display it
                    if(header.classList.contains("hidden")){
                        header.classList.remove("hidden");
                        rows.forEach(row => {
                            const cell = row.cells[i];
                            cell.classList.remove("hidden");
                        });
                    }
                } 
                else {
                    if(!header.classList.contains("hidden")){
                        header.classList.add("hidden");
                        rows.forEach(row => {
                            const cell = row.cells[i];
                            cell.classList.add("hidden");
                        });
                    }
                }
            });
        }
    });
}

function updateFiltersRows(){
    const filter_value = document.getElementById("filter_row_value_select").value;
    loaded.forEach(entity => {
        if(displayed.indexOf(entity) != -1){

            if(entity != current_main_entity){ //just to avoid filtering rows of the main entity in the specific page

                const checked = get_checkboxes_categories();

                const table = document.getElementById(entity+"_table");
                const headers = table.querySelectorAll("thead th");
                const rows = table.querySelectorAll("tbody tr");

                rows.forEach((row, i) => {
                    headers.forEach((header,k) => {
                        if(!header.classList.contains("hidden")){
                            if(checked.indexOf(header.textContent) != -1){
                                const cell = row.cells[k];
                                console.log(cell.textContent);
                                if(cell.textContent == filter_value){
                                    row.classList.add("hidden");
                                }
                            }
                        }
                    });
                });
            }
        }
    });
    
}

function resetRows(){
    loaded.forEach(entity => {
        if(displayed.indexOf(entity) != -1){
            const table = document.getElementById(entity+"_table");
            const headers = table.querySelectorAll("thead th");
            const rows = table.querySelectorAll("tbody tr");
            rows.forEach(row => {
                // if(row.classList.contains("hidden"))
                row.classList.remove("hidden");
            });
        }
    });
}

function resetCheckboxes(){
    let checkboxes = document.getElementsByName('filter_checkbox');
    for (let i = 0; i < checkboxes.length; i++) {
        checkboxes[i].checked = false;
    }
}

function resetFilters(){
    resetCheckboxes();
    resetRows();
    updateFiltersColumns(); //if you reset the checkboxes before, this resets the columns
}

function selectAllFilters(){
    const checkboxes = document.querySelectorAll('#filters-div input[type="checkbox"]');
    // Set each checkbox to checked
    checkboxes.forEach(checkbox => {
        checkbox.checked = true;
    });
}
function unselectAllFilters(){
    const checkboxes = document.querySelectorAll('#filters-div input[type="checkbox"]');
    // Set each checkbox to checked
    checkboxes.forEach(checkbox => {
        checkbox.checked = false;
    });
}

// Toggle columns view: hide all columns except the first across all data tables
function toggleColumnsView(){
    const btn = document.getElementById('toggleColumnsBtn');
    const active = document.body.classList.toggle('names-only');
    if(btn) btn.setAttribute('aria-pressed', active ? 'true' : 'false');
    if(btn) btn.innerText = active ? 'Show full tables' : 'Show only names';

    // apply to already-loaded tables
    document.querySelectorAll('.data-table').forEach(table => applyNamesOnlyToTable(table));
}

function applyNamesOnlyToTable(table){
    if(!table) return;
    const namesOnly = document.body.classList.contains('names-only');
    // hide all th/td except the first cell in each row/thead
    // For thead
    const thead = table.querySelector('thead');
    if(thead){
        thead.querySelectorAll('th').forEach((th, idx) => {
            th.style.display = (idx === 0 || !namesOnly) ? '' : 'none';
        });
    }
    // For tbody
    const rows = table.querySelectorAll('tbody tr');
    rows.forEach(row => {
        row.querySelectorAll('td').forEach((td, idx) => {
            td.style.display = (idx === 0 || !namesOnly) ? '' : 'none';
        });
    });
}

// Ensure that when new tables are loaded (loadTable sets innerHTML), we re-apply names-only styling.
// Wrap existing loadTable if present: call original, then apply styling to the newly inserted table.
if (typeof window.loadTable === 'function'){
    const originalLoadTable = window.loadTable;
    window.loadTable = async function(entity){
        await originalLoadTable(entity);
        const container = document.getElementById(entity+'_table');
        if(container){
            const table = container.querySelector('.data-table');
            if(table) applyNamesOnlyToTable(table);
        }
    }
}
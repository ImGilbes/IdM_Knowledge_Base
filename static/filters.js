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
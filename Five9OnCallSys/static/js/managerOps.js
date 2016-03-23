 // When the document is ready
    $(document).ready(function () {
        
        $('#startdate').datepicker({
            format: "mm/dd/yyyy",
            minDate: new Date(),
        });  
    
    });
    $(document).ready(function () {
        
        $('#enddate').datepicker({
            format: "mm/dd/yyyy"
        });  
    
    });
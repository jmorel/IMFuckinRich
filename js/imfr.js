$(document).ready(function() {	

	// PLOT
	
	// set up plot structure and style
	function setGraph(data) {
		var plot = $.plot(	
			$("#placeholder"),
			[data],
			{ // options
				//yaxis: {min: 0, max: 3},
				//xaxis: {min:0, max: 10},
				//, min: data[0][0], data[max_index][1]
				xaxis: {mode: 'time'},
				zoom: {interactive: 'true'},
				pan: {interactive: 'true'},
				series: {lines: {show: true}, points: {show: true}},
				grid: {hoverable: true, clickable: true} 
			}
		);
	}
	// retrieve data
	var default_currency = '';
	var points = [];	
	var transactions;
	
	
	// we need the username first
	var username = $("div.misc div#username").text();
	// ask for the whole data
	var data = {username: $("div.misc div#username").text()};	
	function reload_graph() {
	
		$.ajax({
			url: 'data',
			type: 'POST',
			data: data,
			dataType: 'json',
			error: function(a,b,c) {alert("Couldn't retrieve data: no connection to /data\n"+a+'\n'+b+'\n'+c)},
			success: function(res) {
				if(res.error_code == 0) {
					alert("Something weird occured. Are you sure you're not trying to do something weird ?");
				} else {
					var i=0;
					var total_amount=0;
					default_currency = res.default_currency
					transactions = res.data;
					for(i=0;i<res.data.length;i++) {
						var row = res.data[i];
						total_amount = total_amount + row.amount_in_default_currency;
						points.push([row.date*1000, total_amount]);
					}
					// bring graph to today
					var d = new Date();
					var t = d.getTime();
					if(t > row.date*1000) {
						points.push([d, total_amount]);
					}
			    	setGraph({
			    		label: 'your money in '+default_currency, 
			    		data: points,
			    		color: '#14456e'});
				}
			}
		});
	}
	reload_graph();
	// callback for click on a point
	$("#placeholder").bind("plotclick", function (event, pos, item) {
        if (item) {
        	var details = transactions[item.dataIndex];
        	var data = {username: $("div.misc div#username").text(), transactionID: details.id};
	    	$.ajax({
				url: 'transactionform',
				type: 'POST',
				data: data,
				dataType: 'text',
				error: function(a,b,c) {alert("Couldn't retrieve data: no connection to /transactionform\n"+a+'\n'+b+'\n'+c)},
				success: function(res) {
					$("#freespace-edit").html(res);
					$("#freespace-edit").slideDown('fast', function() {
						var x = $("#freespace-edit").offset().top - 100;
						$('html,body').animate({scrollTop: x}, 500);
					});
				}
			});
        }
    });
    
    $("span#default_zoom").click(function() {
    	setGraph({
    		label: 'your money in '+default_currency, 
    		data: points,
    		color: '#14456e'});
    });
    
    $("span#add_button").click(function() {
    	var data = {username: $("div.misc div#username").text()};
    	$.ajax({
			url: 'transactionform',
			type: 'POST',
			data: data,
			dataType: 'text',
			error: function(a,b,c) {alert("Couldn't retrieve data: no connection to /transactionform\n"+a+'\n'+b+'\n'+c)},
			success: function(res) {
				$("#freespace-new").html(res);
				$("#freespace-new").slideDown('fast', function() {
						var x = $("#freespace-new").offset().top - 50 ;
						$('html,body').animate({scrollTop: x}, 500);
				});
				// scroll to the zone
				
			}
		});
    });
    
    $("span#close_form_1").live('click', function() {
    	$(this).parent().parent().slideUp('fast');
    });
    $("span#close_form_2").live('click', function() {
    	$(this).parent().parent().parent().parent().parent().slideUp('fast');
    });


    
    $('input[type="button"]#delete_button').live('click', function () {
    	
    	var data = {
    		username: $("input[name='username']").val(),
    		transactionID: $("input[name='transactionID']").val(),
    		password: $("input[name='password']").val()
    	}
    	
    	if(data.password == '') {
    		alert('You need to enter your password in the field below.');
    	} else {
    		$.ajax({
			url: 'deletetransaction',
			type: 'POST',
			data: data,
			dataType: 'text',
			error: function(a,b,c) {alert("Couldn't retrieve data: no connection to /deteletransaction\n"+a+'\n'+b+'\n'+c)},
			success: function(res) {
				$("#freespace-edit").html(res);
				$("#freespace-edit").slideDown('fast');
				points = []
				transactions = []
				reload_graph();
			}
		});
    	}
    
    });
	
	$("form.new_transaction").live('submit', function() {
	
        var data = {
        	username: $("input[name='username']").val(),
        	transactionID: $("input[name='transactionID']").val(),
        	currency: $("select[name='currency']").val(),
        	amount: $("input[name='amount']").val(),
        	given_by: $("input[name='given_by']").val(),
        	date: $("input[name='date']").val(),
        	why: $("input[name='why']").val(),
        	notes: $("textarea[name='notes']").val(),
        	password: $("input[name='password']").val()
        };
        
    	$.ajax({
			url: 'savetransaction',
			type: 'POST',
			data: data,
			dataType: 'text',
			error: function(a,b,c) {alert("Couldn't retrieve data: no connection to /savetransaction\n"+a+'\n'+b+'\n'+c)},
			success: function(res) {
				if(data.transactionID == 'None') {
					$("#freespace-new").html(res);
					//$("#freespace-new").slideDown('fast');
					var x = $("#freespace-new").offset().top - 50 ;
					$('html,body').animate({scrollTop: x}, 500);
				} else {
					$("#freespace-edit").html(res);
					//$("#freespace-edit").slideDown('fast');
					var x = $("#freespace-edit").offset().top - 50 ;
					$('html,body').animate({scrollTop: x}, 500);
				}
				points = []
				transactions = []
				reload_graph();
			}
		});
		
        return false;
    });
    
});
(function(){

	// action is taken on a challenge
	$('.activity-action-btn').on('click', function(event) {
		event.preventDefault();

		// get data attributes on clicked button
		var content = {
			action: $(this).data('action')
		}

		console.log(content);
		
		// send ajax request to activity_action controller.  
		$.ajax({
			url: '/activity_action',
			type: 'POST',
			data: content,
		})
		.done(function(resp) {
			
		})

		// when done modal is shown 
		$('#doneModalLong').off().on('shown.bs.modal', function(e){
			var animationEnd = 'animationend oAnimationEnd mozAnimationEnd webkitAnimationEnd';
			var animationName = 'animated bounceIn'
			var element = '#doneModalLong'

			// randomly generated icon
			icons = ['<i class="far fa-star"></i>', '<i class="fas fa-award"></i>', '<i class="fas fa-trophy"></i>', '<i class="fas fa-shield-alt"></i>']
			var item = icons[Math.floor(Math.random()*icons.length)];
			$('.done-icon').html(item)


			// animation on done modal
			$(element).addClass(animationName).one(animationEnd, function(event) {
				$(element).removeClass(animationName)
			});

		})

		$('.modal').on('click', '.selector', function(event) {
			event.preventDefault();
			console.log($(this));
			console.log(this);
		});

		// when done modal is hidden
		$('#doneModalLong').off().on('hide.bs.modal', function (e) {
			
			// execute the function below
			new_activity('done')
			console.log('hide modal');
		})		

		// skip modal 
		$('#skipModal').off().on('hide.bs.modal', function (e) {
			
			// execute function below
			new_activity('skip');
			console.log('skip modal')			
		})
	});

	// delete account 
	$('.delete-account-confirm').on('click', function(event) {
		event.preventDefault();

		location.href = '/delete_account'; 
				
	});

	// receive email checkbox
	$('.form-check .receive-email').change(function(event) {
		/* Act on the event */
		$('.receive-email-updated').remove();
		
		// ajax request to profile page
		$.ajax({
			url: '/profile',
			type: 'POST'
		})
		.done(function(resp) {
			// add a success button 
			$('.receive-email-label').append('<span class="ml-5 receive-email-updated badge badge-success">Updated successfully.</span>')

			// delete success button after 5 seconds.
			$('.receive-email-updated').show().delay(5000).fadeOut(function(){
				$(this).remove();
			});

		})
	});

	// get started modal option
	$('.get-started-button').on('click' , function(event) {
		event.preventDefault();

		$.ajax({
			url: '/get_started',
			type: 'POST',
		})
		.done(function() {
			console.log("success");
		});
		
	});

}())

// function for loading new activity to the user.
function new_activity(action){
	$('.challenge-loader').removeClass('d-none')
	$('.challenge-card').addClass('d-none').removeClass('animated fast zoomIn delay-0.5s')

	$.ajax({
		url: '/new_activity',
		type: 'POST'
	})
	.done(function(resp) {
		if(!resp){ location.reload() }  
		$('.activity-timestamp').text(moment(resp[1]).format('dddd, Do MMM YYYY'));
		$('.activity-challenge').text(resp[2]);
	})
	.fail(function() {
		location.reload();
	})
	.always(function() {
		timer = setTimeout(function(args) {
			$('.challenge-loader').addClass('d-none');
			$('.challenge-card').removeClass('d-none').addClass('animated fast zoomIn delay-0.5s');

			if(action == 'done'){
				el = '.header-point'
				console.log('executed')
				point = (parseInt($(el).text()) + 3);
				$(el).text(point)
			}
		}, 1500)

	});
}

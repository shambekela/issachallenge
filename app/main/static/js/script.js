(function(){

	// action is taken on a challenge
	$('.activity-action-btn').on('click', function(event) {
		event.preventDefault();

		btn = $(this).data('action')
		// get data attributes on clicked button
		var content = {
			action: btn
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
		$('#doneModalLong').off('shown.bs.modal').on('shown.bs.modal', function(e){
			var animationEnd = 'animationend oAnimationEnd mozAnimationEnd webkitAnimationEnd';
			var animationName = 'animated bounceIn'
			var element = '#doneModalLong'
			var today = new Date();

			// randomly generated icon
			icons = ['<i class="far fa-star"></i>', 
					 '<i class="fas fa-trophy"></i>',
					 '<i class="fas fa-award"></i>',					 
					 '<i class="fas fa-trophy"></i>',
					 '<i class="far fa-star"></i>',
					 '<i class="fas fa-shield-alt"></i>',
					 '<i class="fas fa-award"></i>']
			console.log(icons.length)
			var item = icons[today.getDay()];
			$('.done-icon').html(item)

			// animation on done modal
			$(element).addClass(animationName).one(animationEnd, function(event) {
				$(element).removeClass(animationName)
			});

		})

		$('.modal').off('hide.bs.modal').on('hide.bs.modal', function (e) {
			el = e.target.id
			if(el == 'doneModalLong'){
				new_activity('done')
				console.log('done modal');
			} else if (el == 'skipModal' && btn == 'skip'){
				new_activity('skip')
				console.log('skip modal');
				console.log(btn)
			}
		})
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
		$('.activity-tag').text(resp[3]);
	})
	.fail(function() {
		location.reload();
	})
	.always(function() {
		timer = setTimeout(function(args) {
			$('.challenge-loader').addClass('d-none');
			$('.challenge-card').removeClass('d-none').addClass('animated fast zoomIn delay-0.5s');

			if(action == 'done'){
				el = '.header-point';
				point = (parseInt($(el).text()) + 3);
				$(el).text(point)
			}
		}, 1500)

	});
}

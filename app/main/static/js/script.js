(function(){

	$('#doneModalLong').off('shown.bs.modal').on('shown.bs.modal', function(e){
			var animationEnd = 'animationend oAnimationEnd mozAnimationEnd webkitAnimationEnd';
			var animationName = 'animated bounceIn'
			var element = '#doneModalLong'
			var today = new Date();

			// randomly generated icon
			icons = ['🏆', 
					 '🥇',					 
					 '🔥',
					 '🥇',
					 '🔥',
					 '🎖',
					 '🔥']
			console.log(icons.length)
			var item = icons[today.getDay()];
			$('.done-icon').html(item)

			// animation on done modal
			$(element).addClass(animationName).one(animationEnd, function(event) {
				$(element).removeClass(animationName)
			});
		})

	// action is taken on a challenge
	$('.activity-action-btn').on('click', function(event) {
		event.preventDefault();

		btn = $(this).data('action')
		response = null;

		// get data attributes on clicked button
		var content = {
			action: btn
		}

		
		// send ajax request to activity_action controller. 
		$('.challenge-loader').removeClass('d-none')
		$('.challenge-card').addClass('d-none').removeClass('animated fast zoomIn delay-0.5s')
		$('.current-challenge-header').addClass('d-none')
		
		$.ajax({
			url: '/activity_action',
			type: 'POST',
			data: content,
		})
		.done(function(resp) {
			response = resp

			if(btn == 'done'){
				new_activity(resp, 'done')
			} 

			if (btn == 'skip'){
				new_activity(resp, 'skip')
			}
		})

		// when done modal is shown 
		$('.modal').off('hide.bs.modal').on('hide.bs.modal', function (e) {

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

	$('#welcomeModal').on('hidden.bs.modal', function(event){
		$('#secondWelcomeModal').modal('show');
	})

	// get started modal option
	$('#secondWelcomeModal').on('hidden.bs.modal', function(event){
		
		event.preventDefault();

		$.ajax({
			url: '/get_started',
			type: 'POST',
		})
		.fail(function() {
			location.reload()
		});	
	})
}())

// function for loading new activity to the user.
function new_activity(response, action){
	
	$('.activity-timestamp').text(moment(response[1]).format('dddd, Do MMM YYYY'));
	$('.activity-challenge').text(response[2]);
	$('.activity-tag').text(" "+response[3]);

	timer = setTimeout(function(args) {
		$('.challenge-loader').addClass('d-none');
		$('.challenge-card').removeClass('d-none').addClass('animated fast zoomIn delay-0.5s');
		$('.current-challenge-header').removeClass('d-none');

		if(action == 'done'){
			el = '.header-point';
			point = (parseInt($(el).text()) + 3);
			$(el).text(point)
		}
	}, 800)
}

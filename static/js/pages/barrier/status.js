ma.pages.barrier.status = function( data ){

	if( !ma.components.ConditionalRadioContent ){ return; }

	var validTypes = data.validTypes;
	var i = 0;
	var l = validTypes.length;

	for( ; i < l; i++ ){

		(function( type ){
			new ma.components.ConditionalRadioContent({
				inputContainer: '.status',
				inputName: 'status',
				conditionalElem: ( '#conditional-' + type ),
				shouldShow: function( value ){ return ( value == type ); }
			});

			if( type === data.openPendingActionValue ){

				new ma.components.ConditionalRadioContent({
					inputContainer: '.js-pending-type',
					inputName: 'pending_type',
					conditionalElem: ( '#conditional-OTHER' ),
					shouldShow: function( value ){ return ( value == "OTHER" ); }
				});
			}

		})( validTypes[ i ] );
	}
};

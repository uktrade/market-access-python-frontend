ma.pages.watchList = function(){

	if( !ma.components.ConditionalRadioContent ){ return; }

	try {

		new ma.components.ConditionalRadioContent({
			inputContainer: '.replace-or-new',
			inputName: 'replaceOrNew',
			conditionalElem: '#conditional-replace',
			shouldShow: function( value ){ return ( value === 'replace' ); }
		});

	} catch( e ){

		//ignore error as the form changes and the conditional reveal is not always required
	}
};

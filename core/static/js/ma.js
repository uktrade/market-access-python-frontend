/* eslint no-unused-vars:0 */
var ma = {

	components: {},

	pages: {
		report: {},
		barrier: {
			interactions: {}
		}
	},

	FORM_GROUP_ERROR_CLASS: 'govuk-form-group--error',
	FORM_INPUT_ERROR_CLASS: 'govuk-file-upload--error',
	FORM_ERROR_CLASS: 'govuk-error-message',

	init: function(){

		if( ma.components.Header && jessie.queryOne ){

			var header = new ma.components.Header( jessie.queryOne( '.header-wrapper' ) );
			header.init();
		}

		if( ma.components.Toast ){

			new ma.components.Toast( '.toast' );
		}
	}
};

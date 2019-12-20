ma.pages.barrier.assessment = (function(){

	function setupAttachments(){

		if( !( ma.components.FileUpload && ma.components.Attachments && ma.components.AttachmentForm && ma.components.TextArea && jessie.hasFeatures(
			'queryOne', 'cancelDefault', 'getElementData'
		) ) ){ return; }

		var fileUpload;
		var attachments;

		try {

			fileUpload = new ma.components.FileUpload( {
				group: '.js-form-group',
				input: '.js-file-input',
				limitText: '.js-max-file-size'
			} );

		} catch( e ) { return; }

		var submitButton = jessie.queryOne( '.js-submit-button' );
		var form = fileUpload.form;

		if( !submitButton ){ throw new Error( 'Submit button not found' ); }
		if( !form ){ throw new Error( 'No form found' ); }

		var deleteUrl = jessie.getElementData( form, 'xhr-delete' );

		try {

			attachments = new ma.components.Attachments( fileUpload );
			new ma.components.AttachmentForm( fileUpload, attachments, submitButton, deleteUrl );

		} catch( e ){ return; }

		return form;
	}

	return function(){

		setupAttachments();

		if( ma.components.DeleteModal ){
			new ma.components.DeleteModal();
		}
	};
})();

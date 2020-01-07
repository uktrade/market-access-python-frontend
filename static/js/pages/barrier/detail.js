ma.pages.barrier.detail = (function( doc, jessie ){

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

		if( !submitButton ){ return; }
		if( !form ){ return; }

		try {

			attachments = new ma.components.Attachments( fileUpload );
			new ma.components.AttachmentForm( fileUpload, attachments, submitButton );

		} catch( e ){ return; }

		return form;
	}

	function setupForm( form, noteErrorText ){

		if( !ma.components.TextArea ){ return; }

		var note;

		try {

			note = new ma.components.TextArea( {
				group: '.js-note-group',
				input: '.js-note-text'
			} );

		} catch( e ){ return; }

		function handleFormSubmit( e ){

			if( !note.hasValue() ){

				jessie.cancelDefault( e );
				note.setError( noteErrorText );
				note.focus();
			}
		}

		jessie.attachListener( form, 'submit', handleFormSubmit );
	}

	return function( opts ){

		var form = setupAttachments();
		if( form ){ setupForm( form, opts.noteErrorText ); }

		if( ma.components.ToggleLinks ){
			new ma.components.ToggleLinks( opts.toggleLinks );
		}

		if( ma.components.DeleteModal ){
			new ma.components.DeleteModal();
		}
	};

}( document, jessie ));

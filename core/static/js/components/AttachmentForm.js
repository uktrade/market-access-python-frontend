ma.components.AttachmentForm = (function( jessie ){

	if( !( ma.xhr2 && ( typeof FormData !== 'undefined' ) && jessie.bind ) ){ return; }

	var bind = jessie.bind;

	function AttachmentForm( fileUpload, attachments, submitButton ){

		if( !fileUpload ){ throw new Error( 'fileUpload is required' ); }
		if( !attachments ){ throw new Error( 'attachments is required' ); }
		if( !submitButton ){ throw new Error( 'submitButton is required' ); }

		this.fileUpload = fileUpload;
		this.attachments = attachments;
		this.submitButton = submitButton;

		fileUpload.events.file.subscribe( bind( this.newFile, this ) );
		attachments.events.delete.subscribe( bind( this.deleteDocument, this ) );
	}

	function getCookie(name) {
		var cookieValue = null;
		if (document.cookie && document.cookie !== '') {
			var cookies = document.cookie.split(';');
			for (var i = 0; i < cookies.length; i++) {
				var cookie = cookies[i].trim();
				// Does this cookie string begin with the name we want?
				if (cookie.substring(0, name.length + 1) === (name + '=')) {
					cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
					break;
				}
			}
		}
		return cookieValue;
	}

	AttachmentForm.prototype.showError = function( message ){

		this.submitButton.disabled = false;
		this.fileUpload.setError( message );
		this.fileUpload.showLink();
	};

	AttachmentForm.prototype.updateProgress = function( e ){

		if( e.lengthComputable ){

			if( e.loaded === e.total ){

				this.fileUpload.setProgress( 'scanning file for viruses...' );

			} else {

				this.fileUpload.setProgress( 'uploading file... ' + Math.floor( ( e.loaded / e.total ) * 100 ) + '%' );
			}
		}
	};

	AttachmentForm.prototype.transferFailed = function(){

		this.showError( 'Upload of document cancelled, try again.' );
	};

	AttachmentForm.prototype.transferCanceled = function(){

		this.showError( 'Upload of document cancelled, try again.' );
	};

	AttachmentForm.prototype.loaded = function( e ){

		var xhr = e.target;
		var responseCode = xhr.status;
		var data;

		try {

			data = JSON.parse( xhr.response );

		} catch( e ){

			data = {};
		}

		if( responseCode === 200 ){

			var documentId = data.documentId;
			var file = data.file;

			if( documentId && file ){

				this.submitButton.disabled = false;
				this.fileUpload.showLink();
				this.attachments.addItem( {
					id: documentId,
					delete_url: data.delete_url,
					name: file.name,
					size: file.size
				} );

			} else {

				this.showError( 'There was an issue uploading the document, try again' );
			}

		} else if( responseCode === 401 ){

			this.showError( data.message );

		} else {

			var message = ( data.message || 'A system error has occured, so the file has not been uploaded. Try again.' );
			this.showError( message );
		}
	};

	AttachmentForm.prototype.newFile = function( file ){

		var xhr2 = ma.xhr2();
		var formData = new FormData();

		this.submitButton.disabled = true;
		formData.append( 'document', file );

		if( xhr2.upload ){

			xhr2.upload.addEventListener( 'progress', bind( this.updateProgress, this ), false );
		}

		xhr2.addEventListener( 'error', bind( this.transferFailed, this ), false );
		xhr2.addEventListener( 'abort', bind( this.transferCanceled, this ), false );
		xhr2.addEventListener( 'load', bind( this.loaded, this ), false );

		var csrftoken = getCookie('csrftoken');

		xhr2.open( 'POST', this.fileUpload.action, true );
		xhr2.setRequestHeader("X-CSRFToken", csrftoken);
		xhr2.send( formData );

		this.fileUpload.setProgress( 'uploading file... 0%' );
	};

	AttachmentForm.prototype.deleteDocument = function( documentId, deleteUrl ){
		if( !documentId ){ return; }

		var xhr = ma.xhr2();
		var csrftoken = getCookie('csrftoken');

		xhr.open( 'POST', deleteUrl, true );
		xhr.setRequestHeader("X-CSRFToken", csrftoken);
		xhr.send();

		this.attachments.removeItem( documentId );
	};

	return AttachmentForm;

}( jessie ));

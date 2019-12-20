ma.components.FileUpload = (function( doc, jessie ){

	if( !jessie.hasFeatures(
		'attachListener', 'bind', 'queryOne', 'addClass', 'removeClass', 'cancelDefault', 'getElementData'
	) ){ return; }

	var attachListener = jessie.attachListener;
	var bind = jessie.bind;
	var queryOne = jessie.queryOne;
	var addClass = jessie.addClass;
	var removeClass = jessie.removeClass;
	var cancelDefault = jessie.cancelDefault;

	var GROUP_ERROR_CLASS = ma.FORM_GROUP_ERROR_CLASS;
	var INPUT_ERROR_CLASS = ma.FORM_INPUT_ERROR_CLASS;
	var ERROR_CLASS = ma.FORM_ERROR_CLASS;

	function FileUpload( opts ){

		this.formGroup = queryOne( opts.group );
		this.input = queryOne( opts.input );
		this.limitText = queryOne( opts.limitText );

		if( !this.formGroup ){ throw new Error( 'No form group found' ); }
		if( !this.input ){ throw new Error( 'no input found' ); }
		if( !this.limitText ){ throw new Error( 'no limit text found' ); }

		this.form = this.input.form;
		this.action = jessie.getElementData( this.form, 'xhr-upload' );

		if( !this.form ){ throw new Error( 'no form' ); }
		if( !this.action ){ throw new Error( 'No action on form' ); }

		this.createLink();
		this.createProgress();

		this.linkVisible = false;
		this.progressVisible = false;
		this.inErrorState = false;

		//this.input.style.display = 'none';
		//remove the file input so the file is not uploaded again when saving the form
		this.input.parentNode.removeChild( this.input );
		addClass( this.limitText, 'file-upload__size-limit--js' );

		attachListener( this.link, 'click', bind( this.selectDocument, this ) );
		attachListener( this.input, 'change', bind( this.fileChange, this ) );

		this.events = {
			file: new ma.CustomEvent()
		};

		this.showLink();
	}

	FileUpload.prototype.createLink = function(){

		var link = doc.createElement( 'a' );

		link.innerText = 'Attach document';
		link.className = 'file-upload__link';
		link.style.display = 'none';
		link.href = '#';

		this.limitText.parentNode.insertBefore( link, this.limitText );
		this.link = link;
	};

	FileUpload.prototype.showLink = function(){

		if( !this.linkVisible ){

			this.link.style.display = '';
			this.limitText.style.display = '';
			this.linkVisible = true;

			this.hideProgress();
		}
	};

	FileUpload.prototype.hideLink = function(){

		if( this.linkVisible ){

			this.link.style.display = 'none';
			this.limitText.style.display = 'none';
			this.linkVisible = false;
		}
	};

	FileUpload.prototype.createProgress = function(){

		var progress = doc.createElement( 'span' );
		progress.className = 'file-upload__progress';
		progress.style.display = 'none';

		this.link.parentNode.insertBefore( progress, this.link );
		this.progress = progress;
	};

	FileUpload.prototype.showProgress = function(){

		if( !this.progressVisible ){

			this.progress.style.display = '';
			this.progressVisible = true;

			this.hideLink();
			this.removeError();
		}
	};

	FileUpload.prototype.hideProgress = function(){

		if( this.progressVisible ){

			this.progress.style.display = 'none';
			this.progressVisible = false;
		}
	};

	FileUpload.prototype.selectDocument = function( e ){

		cancelDefault( e );
		this.input.click();
	};

	FileUpload.prototype.fileChange = function(){

		var file = this.input.files[ 0 ];

		if( file ){

			this.events.file.publish( file );
		}
	};

	FileUpload.prototype.setError = function( message ){

		if( !this.error ){

			this.error = doc.createElement( 'span' );
			this.error.className = ERROR_CLASS;
		}

		this.error.innerText = message;
		this.input.value = '';
		this.link.parentNode.insertBefore( this.error, this.link );
		addClass( this.formGroup, GROUP_ERROR_CLASS );
		addClass( this.input, INPUT_ERROR_CLASS );
		this.inErrorState = true;
	};

	FileUpload.prototype.removeError = function(){

		if( this.inErrorState ){

			this.error.parentNode.removeChild( this.error );
			removeClass( this.formGroup, GROUP_ERROR_CLASS );
			removeClass( this.input, INPUT_ERROR_CLASS );
			this.inErrorState = false;
		}
	};

	FileUpload.prototype.setProgress = function( html ){

		this.progress.innerHTML = html;
		this.showProgress();
		this.progress.focus();
	};

	return FileUpload;

}( document, jessie ));

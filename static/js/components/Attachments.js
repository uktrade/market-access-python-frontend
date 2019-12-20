ma.components.Attachments = (function( doc ){

	if( !( jessie.hasFeatures(
		'queryOne',
		'bind',
		'attachListener',
		'getEventTarget',
		'cancelDefault',
		'getElementData',
		'setElementData'
	) ) ){ return; }

	var JS_LIST_CLASS = 'js-documents-list';
	var DATA_KEY = 'document-id';

	var WRAPPER_CLASS = 'attachments';
	var HEADNG_CLASS = 'attachments__heading';
	var LIST_CLASS = 'attachments__list';
	var LIST_ITEM_CLASS = 'attachments__list__item';
	var FILE_NAME_CLASS = 'attachments__list__item__file-name';
	var DELETE_CLASS = 'attachments__list__item__delete';

	function Attachments( fileUpload ){

		if( !fileUpload ){ throw new Error( 'fileUpload is required' ); }

		this.fileUpload = fileUpload;
		this.list = jessie.queryOne( '.' + JS_LIST_CLASS ) || this.createList();
		this.documents = this.list.parentNode;

		this.events = {
			delete: new ma.CustomEvent()
		};

		jessie.attachListener( this.list, 'click', jessie.bind( this.handleClick, this ) );
	}

	Attachments.prototype.handleClick = function( e ){

		var target = jessie.getEventTarget( e );
		var documentId = jessie.getElementData( target, DATA_KEY );

		if( documentId ){

			jessie.cancelDefault( e );
			this.events.delete.publish( documentId );
		}
	};

	Attachments.prototype.createList = function(){

		var wrapper = doc.createElement( 'div' );
		var heading = doc.createElement( 'h3' );
		var list = doc.createElement( 'ul' );

		wrapper.className = WRAPPER_CLASS;

		heading.className = HEADNG_CLASS;
		heading.innerText = 'Attached documents';

		list.className = LIST_CLASS;

		wrapper.appendChild( heading );
		wrapper.appendChild( list );

		return list;
	};

	Attachments.prototype.addItem = function( document ){

		var item = doc.createElement( 'li' );
		var file = doc.createElement( 'span' );
		var deleteLink = doc.createElement( 'a' );
		var input = doc.createElement( 'input' );

		item.className = LIST_ITEM_CLASS;

		file.className = FILE_NAME_CLASS;
		file.innerText = ( document.name + ' - ' + document.size + ' ' );

		deleteLink.className = DELETE_CLASS;
		deleteLink.href = '#';
		deleteLink.innerText = 'Delete';
		jessie.setElementData( deleteLink, DATA_KEY, document.id );

		input.type = 'hidden';
		input.name = 'documentIds';
		input.value = document.id;

		item.appendChild( file );
		item.appendChild( deleteLink );
		item.appendChild( input );

		this.list.appendChild( item );

		if( !this.documents.parentNode ){

			this.fileUpload.formGroup.parentNode.insertBefore( this.documents, this.fileUpload.formGroup );
		}
	};

	Attachments.prototype.removeItem = function( uuid ){

		var input = jessie.queryOne( 'input[value="' + uuid + '"]', this.list );
		var item = input && input.parentNode;

		if( item ){

			this.list.removeChild( item );
		}

		if( !this.list.children.length ){

			this.documents.parentNode.removeChild( this.documents );
		}
	};

	return Attachments;

})( document );

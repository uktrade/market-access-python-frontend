ma.components.Collapsible = (function( doc ){

	if( !jessie.hasFeatures( 'query', 'addClass', 'removeClass', 'bind', 'attachListener', 'getEventTarget' ) ){ return; }

	var addClass = jessie.addClass;
	var removeClass = jessie.removeClass;

	var CONTAINER_CLASS = 'collapsible-widget';
	var CLOSED_CLASS = 'collapsible-widget--closed';
	var OPEN_CLASS = 'collapsible-widget--opened';
	var LABEL_CLASS = 'collapsibe-widget__label button-as-link';

	var TEXT_MORE = 'show more';
	var TEXT_LESS = 'show less';

	function Collapsible( container ){

		if( !container ){ return; }

		this.container = container;
		this.open = false;
		addClass( container, CLOSED_CLASS );

		this.label = doc.createElement( 'button' );
		this.label.className = LABEL_CLASS;
		this.label.innerText = TEXT_MORE;

		this.container.appendChild( this.label );
		jessie.attachListener( this.label, 'click', jessie.bind( this.handleClick, this ) );
	}

	Collapsible.prototype.handleClick = function(){

		var container = this.container;
		this.open = !this.open;

		addClass( container, ( this.open ? OPEN_CLASS : CLOSED_CLASS ) );
		removeClass( container, ( this.open ? CLOSED_CLASS: OPEN_CLASS ) );

		this.label.innerText = ( jessie.hasClass( container, OPEN_CLASS ) ? TEXT_LESS : TEXT_MORE );
	};

	Collapsible.initAll = function(){

		var widgets = jessie.query( '.' + CONTAINER_CLASS );
		var i = 0;
		var widget;

		while( ( widget = widgets[ i++ ] ) ){
			new Collapsible( widget );
		}
	};

	return Collapsible;
}( document ));
